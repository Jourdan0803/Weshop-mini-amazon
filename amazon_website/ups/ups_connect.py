import socket
import sys
from .ups_amazon_pb2 import ConnectWorldId
from .create_msg import *
from .transmit_msg import *
# import world

def testConnect():
    try:
        ups_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print(f"Failed to create socket: {e}")
        sys.exit(1)

    ups_address = ('vcm-38978.vm.duke.edu', 9008)
    try:
        ups_socket.connect(ups_address)
    except socket.error as e:
        print(f"Unable to connect to {ups_address}: {e}")
        sys.exit(1)
    return ups_socket
    

def sendRequestTruck(ups_socket, seq_num, warehouse_id, warehouse_x, warehouse_y, dest_x, dest_y, ship_id, ups_order=None, acks_list=None, error_list=None):
    truck = requestTruck(seq_num, warehouse_id, warehouse_x, warehouse_y, dest_x, dest_y, ship_id, ups_order=ups_order)
    truckReqs_list = [truck]
    cmd = a2uCmd(truckReqs_list=truckReqs_list, acks_list=acks_list, error_list=error_list)
    send_command(ups_socket, cmd)
    # return seq_num+1

def sendDeliverPackage(ups_socket, seq_num, ship_id, acks_list=None, error_list=None):
    package = deliverPackage(seq_num, ship_id)
    package_list = [package]
    cmd = a2uCmd(DeliverReqs_list=package_list, acks_list=acks_list, error_list=error_list)
    send_command(ups_socket, cmd)
    # return seq_num+1

def sendWordid(ups_socket, worldid, seqnum):
    connect = ConnectWorldId(worldid=worldid, seqnum=seqnum)
    send_command(ups_socket, connect)
    # return seqnum+1

def sendAcks(ups_socket, seqnum):
    acks_list = [seqnum]
    cmd = a2uCmd(acks_list=acks_list)
    send_command(ups_socket, cmd)
    # return seqnum + 1

def connect2UPS():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('0.0.0.0', 9008)
    server_socket.bind(server_address)
    server_socket.listen(5)

    ups_socket, ups_address = server_socket.accept()
    _, ups_port = ups_address
    # print(ups_address)
    return ups_socket, ups_port

    