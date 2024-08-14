import world
import ups
import json
import socket, select
import threading
import psycopg2


def handle_worldArrived(seqnum_manager, world_socket, recvMsg, seqnum):
    for single in recvMsg.arrived:
        world.sendAcks(world_socket, seqnum=single.seqnum)
        if recvMsg.acks:
            for ack in recvMsg.acks:
                seqnum_manager.confirm_sequence(ack)
    print("In arrived")


def handle_worldReady(seqnum_manager, world_socket, ups_socket, recvMsg, seqnum):
    for single in recvMsg.ready:
        world.sendAcks(world_socket, seqnum=single.seqnum)

        # change status in db
        order_id = single.shipid
        sql_query = "SELECT * FROM amazon_orders WHERE id = %s LIMIT 1"
        cursor.execute(sql_query, [order_id])
        row = cursor.fetchone()
        order_status = row[1]
        if order_status == "packing":
            update_query = "UPDATE amazon_orders SET status = 'packed' WHERE id = %s"
            cursor.execute(update_query, [order_id])
            connection.commit()

        # requestTruck
        dest_x, dest_y = row[3], row[4]
        seqnum = seqnum_manager.check_sequence(seqnum)
        seqnum_manager.add_sequence(seqnum)
        ups.sendRequestTruck(ups_socket, seq_num=seqnum, warehouse_id=1, warehouse_x=1, warehouse_y=1, dest_x=dest_x, dest_y=dest_y, ship_id=order_id)
        while True:
            ack = ups.receive_command(ups_socket)
            if ack is not None:
                print("Request Truck ack: ", ack)
                seqnum_manager.confirm_sequence(ack)
                break
            ups.sendRequestTruck(ups_socket, seq_num=seqnum, warehouse_id=1, warehouse_x=1, warehouse_y=1, dest_x=dest_x, dest_y=dest_y, ship_id=order_id)



def handle_worldLoaded(seqnum_manager, world_socket, ups_socket, recvMsg, seqnum):
    for single in recvMsg.loaded:
        world.sendAcks(world_socket, seqnum=single.seqnum)

        # change status in db
        order_id = single.shipid
        sql_query = "SELECT * FROM amazon_orders WHERE id = %s LIMIT 1"
        cursor.execute(sql_query, [order_id])
        row = cursor.fetchone()
        if row:
            order_status = row[1]
            if order_status == "packed":
                update_query = "UPDATE amazon_orders SET status = 'delivering' WHERE id = %s"
                cursor.execute(update_query, [order_id])
                connection.commit()
        else:
            print("Error in load")
        
        # request deliver package
        print("send to ups, DELIVER")
        seqnum = seqnum_manager.check_sequence(seqnum)
        seqnum_manager.add_sequence(seqnum)
        ups.sendDeliverPackage(ups_socket, seq_num=seqnum, ship_id=order_id)
        while True:
            ack = ups.receive_command(ups_socket)
            if ack is not None:
                print("Deliver Package ack: ", ack)
                seqnum_manager.confirm_sequence(ack)
                break
            ups.sendDeliverPackage(ups_socket, seq_num=seqnum, ship_id=order_id)
                        


def handle_worldError(world_socket, recvMsg):
    print("encounter errors: \n", recvMsg)
    for single in recvMsg.error:
        world.sendAcks(world_socket, seqnum=single.seqnum)


def handle_frontBuyMore(world_socket, info, seqnum_manager, seqnum):
    product = world.initProduct(id=int(info['id']), description=info['description'], count=int(info['count']))
    things_list = [product]

    seqnum = seqnum_manager.check_sequence(seqnum)
    seqnum_manager.add_sequence(seqnum)
    world.sendPurchaseMore(world_socket, whnum=int(info['whnum']), things_list=things_list, seqnum=seqnum)
 

def handle_frontTopack(world_socket, info, seqnum_manager, seqnum):
    things_list = []
    for thing in info['things_list']:
        product = world.initProduct(id=int(thing['id']), description=thing['description'], count=int(thing['count']))
        things_list.append(product)

    seqnum = seqnum_manager.check_sequence(seqnum)
    seqnum_manager.add_sequence(seqnum)
    world.sendTopack(world_socket=world_socket, whnum=int(info['whnum']), things_list=things_list, shipid=info['orderid'], seqnum=seqnum)
    while True:
        ack = world.receive_message(world_socket)
        if ack is not None:
            print(ack)
            seqnum_manager.confirm_sequence(ack)
            break
        world.sendTopack(world_socket=world_socket, whnum=int(info['whnum']), things_list=things_list, shipid=info['orderid'], seqnum=seqnum)
                    


def handle_upsArrived(world_socket, ups_socket, cmd, seqnum_manager, seqnum):
    for single in cmd.arrived:
        ups.sendAcks(ups_socket, seqnum=single.seq_num)

        seqnum = seqnum_manager.check_sequence(seqnum)
        seqnum_manager.add_sequence(seqnum)
        world.sendPutOnTruck(world_socket, 1, single.truck_id, single.ship_id, seqnum=seqnum)
        
        while True:
            ack = world.receive_message(world_socket)
            if ack is not None:
                seqnum_manager.confirm_sequence(ack)
                break
            world.sendPutOnTruck(world_socket, 1, single.truck_id, single.ship_id, seqnum=seqnum)
 


def handle_upsDelivered(ups_socket, cmd):
    for single in cmd.delivered:
        ups.sendAcks(ups_socket, seqnum=single.seq_num)

        # change status in db
        order_id = single.ship_id
        sql_query = "SELECT * FROM amazon_orders WHERE id = %s LIMIT 1"
        cursor.execute(sql_query, [order_id])
        row = cursor.fetchone()
        if row:
            order_status = row[1]
            if order_status == "delivering":
                update_query = "UPDATE amazon_orders SET status = 'delivered' WHERE id = %s"
                cursor.execute(update_query, [order_id])
                connection.commit()

def handle_upsDest(ups_socket, cmd):
    for single in cmd.dest:
        ups.sendAcks(ups_socket, seqnum=single.seq_num)

        order_id = single.ship_id
        sql_query = "SELECT * FROM amazon_orders WHERE id = %s LIMIT 1"
        cursor.execute(sql_query, [order_id])
        row = cursor.fetchone()
        if row:
            dest_x, dest_y = single.dest_X, single.dest_y
            update_query = "UPDATE amazon_orders SET dest_x = " + dest_x +"AND dest_y=" + dest_y + " WHERE id = %s"
            cursor.execute(update_query, [order_id])
            connection.commit()

def handle_upsError(ups_socket, cmd):
    for single in cmd.error:
        ups.sendAcks(ups_socket, seqnum=single.seq_num)


class SequenceManager:
    def __init__(self):
        self.sequence_table = {}

    def add_sequence(self, seq):
        self.sequence_table[seq] = True
    
    def check_sequence(self, seqnum):
        while seqnum in self.sequence_table:
            seqnum += 1
        return seqnum

    def confirm_sequence(self, ack):
        if ack in self.sequence_table:
            del self.sequence_table[ack]
        else:
            print(f"Sequence {ack} not found")


if __name__ == "__main__":
    # front
    front_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    front_address = ('127.0.0.1', 34521)
    front_socket.connect(front_address)
    print("front scoket")
    
    # world
    world_socket = world.testConnect()
    print("world scoket")

    # ups
    ups_socket, ups_address = ups.connect2UPS()
    sockets = [front_socket, world_socket, ups_socket]
    print("ups socket")
    # sockets = [front_socket, world_socket]

    # Sequence Number Pool
    seqnum_manager = SequenceManager()

    connection = psycopg2.connect(
        host='viaduct.proxy.rlwy.net',
        port='57301',
        dbname='railway',
        user='postgres',
        password='obVguPhVnsZHXxYReyNnBFvBPDqBFPox'
    )
    cursor = connection.cursor()

    seqnum = 1

    worldid = 0
    warehouse1 = world.initWarehouse(id=1, x=1, y=1)
    warehouse2 = world.initWarehouse(id=2, x=2, y=2)
    warehouse3 = world.initWarehouse(id=3, x=3, y=3)
    warehouse_list = [warehouse1, warehouse2, warehouse3]
    connect = world.initConnect(warehouse_list=warehouse_list)
    world.send_message(world_socket, connect)
    print("after initConnect")

    while True:
        readable, _, _ = select.select(sockets, [], [], 2)

        for s in readable:
            addr, port = s.getpeername()
            print(addr, port)
            if port == 23456:
                # from world
                print("========================in world")
                if worldid == 0 :
                    world_connected = world.receive_connect(world_socket)
                    print(world_connected)
                    while world_connected.result != "connected!":
                        connect = world.initConnect(warehouse_list=warehouse_list)
                        world.send_message(world_socket, connect)
                    worldid = world_connected.worldid

                    # send worldid to ups
                    connect = ups.connectWorldid(worldid=worldid, seqnum=seqnum)
                    ups.send_command(ups_socket, connect)
                    while True:
                        ack = ups.receive_command(ups_socket)
                        if ack is not None:
                            seqnum_manager.confirm_sequence(ack)
                            break
                        ups.send_command(ups_socket, connect)
                    print("Connect ups ack: ", ack)
                    seqnum_manager.add_sequence(seqnum)
                    seqnum = seqnum + 1
                    seqnum = seqnum_manager.check_sequence(seqnum)
                    continue
                
                recvMsg = world.receive_message(world_socket)
                print(recvMsg)
                if not recvMsg:
                    print("empty")
                    break
                if recvMsg.arrived:
                    # buymore success, send to front
                    # while not world.checkAck(recvMsg.arrived.seqnum, recvMsg.acks[0]):
                    #     seqnum = world.sendPurchaseMore(world_socket, whnum=int(info['whnum']), things_list=things_list, seqnum=seqnum)
                    #     arrived = world.receive_message(world_socket)
                    # for single in recvMsg.arrived:
                    #     seqnum_manager.add_sequence(seqnum)
                    #     seqnum = world.sendAcks(world_socket, seqnum=single.seqnum)
                    #     seqnum = seqnum_manager.check_sequence(seqnum)
                    # print("In arrived")
                    # successPurchase = "success"
                    # front_socket.sendall(successPurchase.encode())
                    # print("send success to front")
                    request_handler_thread = threading.Thread(target=handle_worldArrived, args=(seqnum_manager, world_socket, recvMsg, seqnum))
                    request_handler_thread.start()
                    continue
                elif recvMsg.ready:
                    request_handler_thread = threading.Thread(target=handle_worldReady, args=(seqnum_manager, world_socket, ups_socket, recvMsg, seqnum))
                    request_handler_thread.start()
                    # for single in recvMsg.ready:
                    #     seqnum_manager.add_sequence(seqnum)
                    #     seqnum = world.sendAcks(world_socket, seqnum=single.seqnum)
                    #     seqnum = seqnum_manager.check_sequence(seqnum)

                    #     # change status in db
                    #     order_id = single.shipid
                    #     sql_query = "SELECT * FROM amazon_orders WHERE id = %s LIMIT 1"
                    #     cursor.execute(sql_query, [order_id])
                    #     row = cursor.fetchone()
                    #     order_status = row[1]
                    #     if order_status == "packing":
                    #         update_query = "UPDATE amazon_orders SET status = 'packed' WHERE id = %s"
                    #         cursor.execute(update_query, [order_id])
                    #         connection.commit()

                    #     # requestTruck
                    #     dest_x, dest_y = row[3], row[4]
                    #     seqnum_manager.add_sequence(seqnum)
                    #     seqnum = ups.sendRequestTruck(ups_socket, seq_num=seqnum, warehouse_id=1, warehouse_x=1, warehouse_y=1, dest_x=dest_x, dest_y=dest_y, ship_id=order_id)
                    #     # ack = ups.receive_command(ups_socket)
                    #     while True:
                    #         ack = ups.receive_command(ups_socket)
                    #         if ack is not None:
                    #             seqnum_manager.confirm_sequence(ack)
                    #             break
                    #         ups.sendRequestTruck(ups_socket, seq_num=seqnum, warehouse_id=1, warehouse_x=1, warehouse_y=1, dest_x=dest_x, dest_y=dest_y, ship_id=order_id)
                    #     print("Request Truck ack: ", ack)
                        # ack = ups.receive_command(ups_socket)
                        # print("Request Truck: ", ack)

                    # # change status in db
                    # order_id = recvMsg.ready[0].shipid
                    # sql_query = "SELECT * FROM amazon_orders WHERE id = %s LIMIT 1"
                    # cursor.execute(sql_query, [order_id])
                    # row = cursor.fetchone()
                    # order_status = row[1]
                    # if order_status == "packing":
                    #     update_query = "UPDATE amazon_orders SET status = 'packed' WHERE id = %s"
                    #     cursor.execute(update_query, [order_id])
                    #     connection.commit()
                    continue
                elif recvMsg.loaded:
                    request_handler_thread = threading.Thread(target=handle_worldLoaded, args=(seqnum_manager, world_socket, ups_socket, recvMsg, seqnum))
                    request_handler_thread.start()
                    # for single in recvMsg.loaded:
                    #     seqnum_manager.add_sequence(seqnum)
                    #     seqnum = world.sendAcks(world_socket, seqnum=single.seqnum)
                    #     seqnum = seqnum_manager.check_sequence(seqnum)

                    #     # change status in db
                    #     order_id = single.shipid
                    #     sql_query = "SELECT * FROM amazon_orders WHERE id = %s LIMIT 1"
                    #     cursor.execute(sql_query, [order_id])
                    #     row = cursor.fetchone()
                    #     if row:
                    #         order_status = row[1]
                    #         if order_status == "packed":
                    #             update_query = "UPDATE amazon_orders SET status = 'delivering' WHERE id = %s"
                    #             cursor.execute(update_query, [order_id])
                    #             connection.commit()
                    #     else:
                    #         print("Error in load")
                        
                    #     # request deliver package, TBD
                    #     print("send to ups, DELIVER")
                    #     seqnum_manager.add_sequence(seqnum)
                    #     seqnum = ups.sendDeliverPackage(ups_socket, seq_num=seqnum, ship_id=order_id)
                    #     seqnum = seqnum_manager.check_sequence(seqnum)
                    #     ack = ups.receive_command(ups_socket)
                    #     while True:
                    #         ack = ups.receive_command(ups_socket)
                    #         if ack is not None:
                    #             seqnum_manager.confirm_sequence(ack)
                    #             break
                    #         ups.sendDeliverPackage(ups_socket, seq_num=seqnum, ship_id=order_id)
                    #     print("Deliver Package ack: ", ack)
                    #     seqnum = seqnum_manager.check_sequence(seqnum)

                    # # change status in db
                    # order_id = recvMsg.loaded[0].shipid
                    # sql_query = "SELECT * FROM amazon_orders WHERE id = %s LIMIT 1"
                    # cursor.execute(sql_query, [order_id])
                    # row = cursor.fetchone()
                    # if row:
                    #     order_status = row[1]
                    #     if order_status == "packed":
                    #         update_query = "UPDATE amazon_orders SET status = 'delivering' WHERE id = %s"
                    #         cursor.execute(update_query, [order_id])
                    #         connection.commit()
                    # else:
                    #     print("Error in load")
                    continue
                elif recvMsg.error:
                    # error
                    request_handler_thread = threading.Thread(target=handle_worldError, args=(seqnum_manager, world_socket, recvMsg, seqnum))
                    request_handler_thread.start()
                    # print("encounter errors: \n", recvMsg)
                    # for single in recvMsg.error:
                    #     seqnum_manager.add_sequence(seqnum)
                    #     seqnum = world.sendAcks(world_socket, seqnum=single.seqnum)
                    #     seqnum = seqnum_manager.check_sequence(seqnum)
                    continue
                

            if port == 34521:
                # from front end
                print("====================================in front")
                info = front_socket.recv(4096)
                info = json.loads(info.decode())
                print("Received info details:", info)

                if info['method'] == "buymore":
                    # product = world.initProduct(id=int(info['id']), description=info['description'], count=int(info['count']))
                    # things_list = [product]
                    # seqnum = world.sendPurchaseMore(world_socket, whnum=int(info['whnum']), things_list=things_list, seqnum=seqnum)
                    request_handler_thread = threading.Thread(target=handle_frontBuyMore, args=(world_socket, info, seqnum_manager, seqnum))
                    request_handler_thread.start()
                    continue
                elif info['method'] == "topack":
                    # send to world, topack
                    # things_list = []
                    # for thing in info['things_list']:
                    #     product = world.initProduct(id=int(thing['id']), description=thing['description'], count=int(thing['count']))
                    #     things_list.append(product)
                    # seqnum = world.sendTopack(world_socket=world_socket, whnum=int(info['whnum']), things_list=things_list, shipid=info['orderid'], seqnum=seqnum)
                    # ready = world.receive_message(world_socket)
                    # print(ready)
                    request_handler_thread = threading.Thread(target=handle_frontTopack, args=(world_socket, info, seqnum_manager, seqnum))
                    request_handler_thread.start()
                    continue
            
            # waiting for UPS connection
            if port == ups_address:
                print("====================================in UPS")
                cmd = ups.receive_command(ups_socket)
                print("UPS cmd:", cmd)
                if cmd.arrived: # ask world to load
                    # for single in cmd.arrived:
                    #     seqnum_manager.add_sequence(seqnum)
                    #     seqnum = ups.sendAcks(ups_socket, seqnum=single.seq_num)
                    #     seqnum = seqnum_manager.check_sequence(seqnum)

                    #     seqnum_manager.add_sequence(seqnum)
                    #     seqnum = world.sendPutOnTruck(world_socket, 1, single.truck_id, single.ship_id, seqnum=seqnum)
                    #     seqnum = seqnum_manager.check_sequence(seqnum)

                    #     to_load_ack = world.receive_message(world_socket)
                    #     seqnum_manager.confirm_sequence(ack)
                    #     print(to_load_ack)
                    request_handler_thread = threading.Thread(target=handle_upsArrived, args=(world_socket, ups_socket, cmd, seqnum_manager, seqnum))
                    request_handler_thread.start()
                elif cmd.delivered:
                    # for single in cmd.delivered:
                    #     seqnum_manager.add_sequence(seqnum)
                    #     seqnum = ups.sendAcks(ups_socket, seqnum=single.seq_num)
                    #     seqnum = seqnum_manager.check_sequence(seqnum)

                    #     # change status in db
                    #     order_id = single.ship_id
                    #     sql_query = "SELECT * FROM amazon_orders WHERE id = %s LIMIT 1"
                    #     cursor.execute(sql_query, [order_id])
                    #     row = cursor.fetchone()
                    #     if row:
                    #         order_status = row[1]
                    #         if order_status == "delivering":
                    #             update_query = "UPDATE amazon_orders SET status = 'delivered' WHERE id = %s"
                    #             cursor.execute(update_query, [order_id])
                    #             connection.commit()
                    request_handler_thread = threading.Thread(target=handle_upsDelivered, args=(ups_socket, cmd))
                    request_handler_thread.start()
                elif cmd.dest:
                    # for single in cmd.dest:
                    #     seqnum_manager.add_sequence(seqnum)
                    #     seqnum = ups.sendAcks(ups_socket, seqnum=single.seq_num)
                    #     seqnum = seqnum_manager.check_sequence(seqnum)

                    #     order_id = single.ship_id
                    #     sql_query = "SELECT * FROM amazon_orders WHERE id = %s LIMIT 1"
                    #     cursor.execute(sql_query, [order_id])
                    #     row = cursor.fetchone()
                    #     if row:
                    #         dest_x, dest_y = single.dest_X, single.dest_y
                    #         update_query = "UPDATE amazon_orders SET dest_x = " + dest_x +"AND dest_y=" + dest_y + " WHERE id = %s"
                    #         cursor.execute(update_query, [order_id])
                    #         connection.commit()
                    request_handler_thread = threading.Thread(target=handle_upsDest, args=(ups_socket, cmd))
                    request_handler_thread.start()
                elif cmd.error:
                    request_handler_thread = threading.Thread(target=handle_upsError, args=(ups_socket, cmd))
                    request_handler_thread.start()
                    # for single in cmd.error:
                    #     seqnum_manager.add_sequence(seqnum)
                    #     seqnum = ups.sendAcks(ups_socket, seqnum=single.seq_num)
                    #     seqnum = seqnum_manager.check_sequence(seqnum)
                
            
            











