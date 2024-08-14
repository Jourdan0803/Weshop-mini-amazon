from .create_msg import *
from .transmit_msg import *
import socket
import threading


def testConnect():
    try:
        world_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print(f"Failed to create socket: {e}")
        sys.exit(1)

    world_address = ('152.3.65.200', 23456)
    try:
        world_socket.connect(world_address)
    except socket.error as e:
        print(f"Unable to connect to {world_address}: {e}")
        sys.exit(1)
    return world_socket

def sendPurchaseMore(world_socket, whnum, things_list, seqnum, acks_list=None, simspeed=None, disconnect=False):
    purchase = PurchaseMore(whnum, things_list, seqnum)
    buy_list = [purchase]
    command = createCmd(buy_list=buy_list, acks_list=acks_list, simspeed=simspeed, disconnect=disconnect)
    send_message(world_socket, command)
    # return seqnum + 1


def sendTopack(world_socket, whnum, things_list, shipid, seqnum, acks_list=None, simspeed=None, disconnect=False):
    package = initPack(whnum, things_list, shipid, seqnum)
    topack_list = [package]
    cmd = createCmd(topack_list=topack_list, acks_list=acks_list, simspeed=simspeed, disconnect=disconnect)
    send_message(world_socket, cmd)
    # return seqnum + 1

def sendPutOnTruck(world_socket, whnum, truckid, shipid, seqnum, acks_list=None, simspeed=None, disconnect=False):
    load = initPutOnTruck(whnum, truckid, shipid, seqnum)
    load_list = [load]
    cmd = createCmd(load_list=load_list, acks_list=acks_list, simspeed=simspeed, disconnect=disconnect)
    send_message(world_socket, cmd)
    # return seqnum + 1

def sendQuery(world_socket, packageid, seqnum, acks_list=None, simspeed=None, disconnect=False):
    query = initQuery(packageid=packageid, seqnum=seqnum)
    query_list = [query]
    cmd = createCmd(query_list=query_list, acks_list=acks_list, simspeed=simspeed, disconnect=disconnect)
    send_message(world_socket, cmd)
    # return seqnum + 1

def sendAcks(world_socket, seqnum, simspeed=None, disconnect=False):
    acks_list = [seqnum]
    cmd = createCmd(acks_list=acks_list, simspeed=simspeed, disconnect=disconnect)
    send_message(world_socket, cmd)
    # return seqnum + 1



def checkAck(seqnum, ack):
    if seqnum == ack:
        return True
    else:
        return False
    


def listenQuery(world_socket):
    seqnum = 10000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    HOST = '127.0.0.1'
    PORT = 9008
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Listening on {HOST}:{PORT}...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connected to {client_address}")

        request_handler_thread = threading.Thread(target=handle_query, args=(client_socket, world_socket, seqnum))
        request_handler_thread.start()

def handle_query(client_socket, world_socket, seqnum):
    request = client_socket.recv(1024).decode()
    print(f"Received request: {request}")

    # ask world
    if(request['info'] == "query"):
        sendQuery(world_socket, request['packageid'], seqnum)
        status = receive_message(world_socket)    

    # send back to front
    response = status.packagestatus[0]
    client_socket.sendall(response.encode())

    client_socket.close()

# listen_thread = threading.Thread(target=listenQuery, args=(world_socket,))
# listen_thread.start()
    
# receive ready, waiting ups and ask to load, need a thread?
def handle_ready(world_socket):
    while True:
        ready = receive_message(world_socket)
        if ready.ready:
            print(ready)
            break








if __name__ == "__main__":
    world_socket = testConnect()

    warehouse1 = initWarehouse(id=1, x=1, y=1)
    product1 = initProduct(id=1, description="22 bag", count=20)
    product2 = initProduct(id=2, description="CF bag", count=20)
    product3 = initProduct(id=3, description="19 bag", count=5)
    things_list = [product1, product2]

    # AConnect
    warehouse_list = []
    warehouse_list.append(warehouse1)
    connect = initConnect(warehouse_list=warehouse_list)
    # connect = initConnect(worldid=3)
    send_message(world_socket, connect)
    response = receive_connect(world_socket)
    print("connect result: ", response)

    # purchase more
    sendPurchaseMore(world_socket, whnum=1, things_list=things_list, seqnum=100)
    arrived = receive_message(world_socket)
    if arrived.error:
        print("err in arrived\n")
    if arrived.arrived:
        print("purchase result: ", arrived.arrived)
    print(arrived.acks[0])

    # topack
    test_list = [product1]
    product4 = initProduct(id=1, description="22 bag", count=5)
    sendTopack(world_socket=world_socket, whnum=1, things_list=[product4], shipid=43, seqnum=60)
    ready = receive_message(world_socket)
    if ready.error:
        print("error in ready\n")
    print("pack result: ", ready.acks[0])

    while True:
        ready = receive_message(world_socket)
        if ready.ready:
            print(ready.ready)
            break


    # # query
    # sendQuery(world_socket, packageid=1, seqnum=4)
    # queryRes = receive_message(world_socket)
    # print(queryRes)


    # response = recvRes(ready_list=ready.ready, error_list=ready.error)
    # print(response)

    # sendPutOnTruck(world_socket, whnum=1, truckid=1, shipid=1, seqnum=3)
    # response = receive_message(world_socket)
    # print("truck result: ", response)
    
