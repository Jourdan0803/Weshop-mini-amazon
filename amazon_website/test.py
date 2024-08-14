import world
import ups
import json
import socket, select
import threading
import psycopg2

# recv_lock = threading.Lock()

def handle_worldArrived(seqnum_manager, world_socket, recvMsg):
    for single in recvMsg.arrived:
        world.sendAcks(world_socket, seqnum=single.seqnum)
        if recvMsg.acks:
            for ack in recvMsg.acks:
                seqnum_manager.confirm_sequence(ack)
    print("In arrived")


def handle_worldReady(seqnum_manager, world_socket, ups_socket, recvMsg):
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
        ups_order = None
        # if UPS account
        if row[7] != "None":
            ups_account = row[7]

            cursor.execute("SELECT amazon_orderdetails.product_id_id, amazon_orderdetails.quantity FROM amazon_orderdetails WHERE amazon_orderdetails.order_id_id = %s", [order_id])
            rows = cursor.fetchall()
            product_ids = [row[0] for row in rows]
            product_counts = [row[1] for row in rows]

            descriptions = []
            for id in product_ids:
                query = "SELECT amazon_products.description FROM amazon_products WHERE amazon_products.id = %s"
                cursor.execute(query, [id])
                row = cursor.fetchone()
                if row:
                    descriptions.append(row[0])
            print("descriptions: ", descriptions)
            print("type: ", type(descriptions[0]))

            things_list = []
            for i in range(len(product_ids)):
                product = ups.createProduct(productId=product_ids[i], productCount=product_counts[i], productDescription=descriptions[i])
                things_list.append(product)
            
            ups_order = ups.createUPSOrder(ups_account, things_list)

        seqnum = seqnum_manager.check_sequence()
        seqnum_manager.add_sequence(seqnum)
        print("ask truck from ups, seq: ", seqnum)
        if ups_order is None:
            ups.sendRequestTruck(ups_socket, seq_num=seqnum, warehouse_id=1, warehouse_x=1, warehouse_y=1, dest_x=dest_x, dest_y=dest_y, ship_id=order_id)
        else:
            ups.sendRequestTruck(ups_socket, seq_num=seqnum, warehouse_id=1, warehouse_x=1, warehouse_y=1, dest_x=dest_x, dest_y=dest_y, ship_id=order_id, ups_order=ups_order)
        while True:
            # with recv_lock:
            #     acks = ups.receive_command(ups_socket)
            #     if acks is not None:
            #         for ack in acks.acks:
            #             print("Request Truck ack: ", ack)
            #             seqnum_manager.confirm_sequence(ack)
            #         break
            # # ups.sendRequestTruck(ups_socket, seq_num=seqnum, warehouse_id=1, warehouse_x=1, warehouse_y=1, dest_x=dest_x, dest_y=dest_y, ship_id=order_id)
                # if ups_order is None:
                #     ups.sendRequestTruck(ups_socket, seq_num=seqnum, warehouse_id=1, warehouse_x=1, warehouse_y=1, dest_x=dest_x, dest_y=dest_y, ship_id=order_id)
                # else:
                #     ups.sendRequestTruck(ups_socket, seq_num=seqnum, warehouse_id=1, warehouse_x=1, warehouse_y=1, dest_x=dest_x, dest_y=dest_y, ship_id=order_id, ups_order=ups_order)
                acks = ups.receive_command(ups_socket)
                if acks is not None:
                    for ack in acks.acks:
                        print("Request Truck ack: ", ack)
                        seqnum_manager.confirm_sequence(ack)
                    break
                print("Resend request truck")
                if ups_order is None:
                    ups.sendRequestTruck(ups_socket, seq_num=seqnum, warehouse_id=1, warehouse_x=1, warehouse_y=1, dest_x=dest_x, dest_y=dest_y, ship_id=order_id)
                else:
                    ups.sendRequestTruck(ups_socket, seq_num=seqnum, warehouse_id=1, warehouse_x=1, warehouse_y=1, dest_x=dest_x, dest_y=dest_y, ship_id=order_id, ups_order=ups_order)


def handle_worldLoaded(seqnum_manager, world_socket, ups_socket, recvMsg):
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
        seqnum = seqnum_manager.check_sequence()
        seqnum_manager.add_sequence(seqnum)
        print("send deliver to ups, seqnum: ", seqnum)
        ups.sendDeliverPackage(ups_socket, seq_num=seqnum, ship_id=order_id)
        while True:
            # with recv_lock:
            #     acks = ups.receive_command(ups_socket)
            #     if acks is not None:
            #         for ack in acks.acks:
            #             print("Deliver Package ack: ", ack)
            #             seqnum_manager.confirm_sequence(ack)
            #         break
            #     ups.sendDeliverPackage(ups_socket, seq_num=seqnum, ship_id=order_id)
            acks = ups.receive_command(ups_socket)
            if acks is not None:
                for ack in acks.acks:
                    print("Deliver Package ack: ", ack)
                    seqnum_manager.confirm_sequence(ack)
                break
            print("resend deliver package")
            ups.sendDeliverPackage(ups_socket, seq_num=seqnum, ship_id=order_id)


def handle_worldError(world_socket, recvMsg):
    print("encounter errors: \n", recvMsg)
    for single in recvMsg.error:
        world.sendAcks(world_socket, seqnum=single.seqnum)


def handle_frontBuyMore(world_socket, info, seqnum_manager):
    product = world.initProduct(id=int(info['id']), description=info['description'], count=int(info['count']))
    things_list = [product]

    seqnum = seqnum_manager.check_sequence()
    seqnum_manager.add_sequence(seqnum)
    print("seqnum in buymore: ", seqnum)
    world.sendPurchaseMore(world_socket, whnum=int(info['whnum']), things_list=things_list, seqnum=seqnum)
    print("after purchase more")

    while True:
        print("in while")
        recvMsg = world.receive_message(world_socket)
        if recvMsg:
            if recvMsg.acks:
                for ack in recvMsg.acks:
                    seqnum_manager.confirm_sequence(ack)
                    print("In buy more acks: ", ack)

            if recvMsg.arrived:
                for single in recvMsg.arrived:
                    world.sendAcks(world_socket, seqnum=single.seqnum)

                    update_query = "UPDATE amazon_products SET uploading = 0 WHERE amazon_products.id = %s"
                    cursor.execute(update_query, [single.things[0].id])
                    connection.commit()
                break 
        print("Resend purchase more")
        world.sendPurchaseMore(world_socket, whnum=int(info['whnum']), things_list=things_list, seqnum=seqnum)
           
 

def handle_frontTopack(world_socket, info, seqnum_manager):
    things_list = []
    for thing in info['things_list']:
        product = world.initProduct(id=int(thing['id']), description=thing['description'], count=int(thing['count']))
        things_list.append(product)

    seqnum = seqnum_manager.check_sequence()
    seqnum_manager.add_sequence(seqnum)
    print("seqnum in sentoPack: ", seqnum)
    world.sendTopack(world_socket=world_socket, whnum=int(info['whnum']), things_list=things_list, shipid=info['orderid'], seqnum=seqnum)
    while True:
        # with recv_lock:
        acks = world.receive_message(world_socket)
        if acks is not None:
            for ack in acks.acks:
                print("front topack ack: ", ack)
                seqnum_manager.confirm_sequence(ack)
            break
        print("Resend in topack")
        world.sendTopack(world_socket=world_socket, whnum=int(info['whnum']), things_list=things_list, shipid=info['orderid'], seqnum=seqnum)
     

def handle_upsArrived(world_socket, ups_socket, cmd, seqnum_manager, ups_requests):
    for single in cmd.arrived:
        ups.sendAcks(ups_socket, seqnum=single.seq_num)
        if single.seq_num in ups_requests:
            return
        ups_requests.append(single.seq_num)

        seqnum = seqnum_manager.check_sequence()
        seqnum_manager.add_sequence(seqnum)
        world.sendPutOnTruck(world_socket, 1, single.truck_id, single.ship_id, seqnum=seqnum)
        
        while True:
            # with recv_lock:
            #     acks = world.receive_message(world_socket)
            #     if acks is not None:
            #         for ack in acks.acks:
            #             seqnum_manager.confirm_sequence(ack)
            #         break
            #     world.sendPutOnTruck(world_socket, 1, single.truck_id, single.ship_id, seqnum=seqnum)
            acks = world.receive_message(world_socket)
            if acks is not None:
                for ack in acks.acks:
                    seqnum_manager.confirm_sequence(ack)
                break
            print("Resend in put on truck")
            world.sendPutOnTruck(world_socket, 1, single.truck_id, single.ship_id, seqnum=seqnum)

def handle_upsDelivered(ups_socket, cmd, ups_requests):
    for single in cmd.delivered:
        ups.sendAcks(ups_socket, seqnum=single.seq_num)
        if single.seq_num in ups_requests:
            return
        ups_requests.append(single.seq_num)

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


def handle_upsDest(ups_socket, cmd, ups_requests):
    for single in cmd.dest:
        ups.sendAcks(ups_socket, seqnum=single.seq_num)
        if single.seq_num in ups_requests:
            return
        ups_requests.append(single.seq_num)

        order_id = single.ship_id
        sql_query = "SELECT * FROM amazon_orders WHERE id = %s LIMIT 1"
        cursor.execute(sql_query, [order_id])
        row = cursor.fetchone()
        if row:
            dest_x, dest_y = single.dest_x, single.dest_y
            update_query = "UPDATE amazon_orders SET dest_x = %s, dest_y = %s WHERE id = %s"
            cursor.execute(update_query, (dest_x, dest_y, order_id))
            connection.commit()


def handle_upsError(ups_socket, cmd, ups_requests):
    for single in cmd.error:
        ups.sendAcks(ups_socket, seqnum=single.seq_num)
        if single.seq_num in ups_requests:
            return
        ups_requests.append(single.seq_num)


class SequenceManager:
    def __init__(self):
        self.sequence_table = {}
        self.seqnum = 1
        self.lock = threading.Lock()

    def add_sequence(self, seq):
        with self.lock:
            self.sequence_table[seq] = True
    
    def check_sequence(self):
        with self.lock:
            self.seqnum += 1
            while self.seqnum in self.sequence_table:
                self.seqnum += 1
            return self.seqnum

    def confirm_sequence(self, ack):
        with self.lock:
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
    world_socket.settimeout(5)
    print("world scoket")

    # ups
    ups_socket, ups_address = ups.connect2UPS()
    sockets = [front_socket, world_socket, ups_socket]
    print("ups socket")
    # sockets = [front_socket, world_socket]

    # Sequence Number Pool
    seqnum_manager = SequenceManager()
    ups_requests = []

    connection = psycopg2.connect(
        host='db',
        port='5432',
        dbname='miniAmazon',
        user='postgres',
        password='passw0rd'
    )
    cursor = connection.cursor()

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
                print("worldid: ", worldid)
                if worldid == 0 :
                    world_connected = world.receive_connect(world_socket)
                    print(world_connected)
                    while world_connected.result != "connected!":
                        world.send_message(world_socket, connect)
                    worldid = world_connected.worldid

                    # send worldid to ups
                    seqnum = seqnum_manager.check_sequence()
                    seqnum_manager.add_sequence(seqnum)
                    print("send worldid to ups, seqnum: ", seqnum)
                    # ups_socket = 1
                    connect = ups.connectWorldid(worldid=worldid, seqnum=seqnum)
                    ups.send_command(ups_socket, connect)
                    while True:
                        acks = ups.receive_command(ups_socket)
                        print(acks.acks)
                        if acks:
                            for ack in acks.acks:
                                seqnum_manager.confirm_sequence(ack)
                            break
                        ups.send_command(ups_socket, connect)
                    print("Connect ups ack: ", acks)
                    continue
                
                recvMsg = world.receive_message(world_socket)
                print(recvMsg)

                if recvMsg.arrived:
                    handle_worldArrived(seqnum_manager, world_socket, recvMsg)
                    # request_handler_thread = threading.Thread(target=handle_worldArrived, args=(seqnum_manager, world_socket, recvMsg))
                    # request_handler_thread.start()
                    # continue
                elif recvMsg.ready:
                    handle_worldReady(seqnum_manager, world_socket, ups_socket, recvMsg)
                    # request_handler_thread = threading.Thread(target=handle_worldReady, args=(seqnum_manager, world_socket, ups_socket, recvMsg))
                    # request_handler_thread.start()
                    # continue
                elif recvMsg.loaded:
                    handle_worldLoaded(seqnum_manager, world_socket, ups_socket, recvMsg)
                    # request_handler_thread = threading.Thread(target=handle_worldLoaded, args=(seqnum_manager, world_socket, ups_socket, recvMsg))
                    # request_handler_thread.start()
                    # continue
                elif recvMsg.error:
                    # error
                    handle_worldError(world_socket, recvMsg)
                    # request_handler_thread = threading.Thread(target=handle_worldError, args=(seqnum_manager, world_socket, recvMsg))
                    # request_handler_thread.start()
                    # continue
                

            if port == 34521:
                # from front end
                print("====================================in front")
                info = front_socket.recv(4096)
                info = json.loads(info.decode())
                print("Received info details:", info)

                if info['method'] == "buymore":
                    handle_frontBuyMore(world_socket, info, seqnum_manager)
                    # request_handler_thread = threading.Thread(target=handle_frontBuyMore, args=(world_socket, info, seqnum_manager))
                    # request_handler_thread.start()
                    # continue
                elif info['method'] == "topack":
                    handle_frontTopack(world_socket, info, seqnum_manager)
                    # request_handler_thread = threading.Thread(target=handle_frontTopack, args=(world_socket, info, seqnum_manager))
                    # request_handler_thread.start()
                    # continue
            
            # waiting for UPS connection
            if port == ups_address:
                print("====================================in UPS")
                cmd = ups.receive_command(ups_socket)
                print("UPS cmd:", cmd)

                if cmd.arrived: # ask world to load
                    handle_upsArrived(world_socket, ups_socket, cmd, seqnum_manager, ups_requests)
                    # request_handler_thread = threading.Thread(target=handle_upsArrived, args=(world_socket, ups_socket, cmd, seqnum_manager))
                    # request_handler_thread.start()
                    # continue
                elif cmd.delivered:
                    handle_upsDelivered(ups_socket, cmd, ups_requests)
                    # request_handler_thread = threading.Thread(target=handle_upsDelivered, args=(ups_socket, cmd))
                    # request_handler_thread.start()
                    # continue
                elif cmd.dest:
                    handle_upsDest(ups_socket, cmd, ups_requests)
                    # request_handler_thread = threading.Thread(target=handle_upsDest, args=(ups_socket, cmd))
                    # request_handler_thread.start()
                    # continue
                elif cmd.error:
                    handle_upsError(ups_socket, cmd, ups_requests)
                    # request_handler_thread = threading.Thread(target=handle_upsError, args=(ups_socket, cmd))
                    # request_handler_thread.start()
                    # continue
                