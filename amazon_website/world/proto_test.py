from create_msg import *
from transmit_msg import *
import socket

try:
    world_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as e:
    print(f"Failed to create socket: {e}")
    sys.exit(1)

server_address = ('127.0.0.1', 23456)
try:
    world_socket.connect(server_address)
except socket.error as e:
    print(f"Unable to connect to {server_address}: {e}")
    # world_socket.close()
    sys.exit(1)

# APackinitWarehouse
warehouse1 = initWarehouse(id=1, x=1, y=1)

# AConnect
warehouse_list = []
warehouse_list.append(warehouse1)
connect = initConnect(warehouse_list=warehouse_list)

# connect
print(connect)
send_message(world_socket, connect)
response = receive_connect(world_socket)
print(response)


# Product
product1 = initProduct(id=1, description="test product", count=1)
# print(product1)

things_list = [product1]
# print(things_list)
purchase = PurchaseMore(whnum=1, things_list=things_list, seqnum=1)

buy_list = [purchase]
topack_list = []
load_list = []
query_list=[]
acks = None

command = createCmd(buy_list, topack_list, load_list, query_list)
# create cmd
print(command)
send_message(world_socket, command)
response = receive_message(world_socket)
print("======================")
print(response)

world_socket.close()
