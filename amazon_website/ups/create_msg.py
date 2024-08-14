import socket
from google.protobuf.internal.encoder import _EncodeVarint
from google.protobuf.internal.decoder import _DecodeVarint32
import sys
from .ups_amazon_pb2 import ConnectWorldId, RequestTruck, TruckArrived, DeliverPackage, U2ADelivered, AtoUCommands, UtoACommands, Err, UPSOrder, Product, FinalDest

def connectWorldid(worldid, seqnum):
    connect = ConnectWorldId()
    connect.world_id = worldid
    connect.seq_num = seqnum
    return connect

def requestTruck(seq_num, warehouse_id, warehouse_x, warehouse_y, dest_x, dest_y, ship_id, ups_order=None):
    request = RequestTruck()
    request.seq_num = seq_num
    request.warehouse_id = warehouse_id
    request.warehouse_x = warehouse_x
    request.warehouse_y = warehouse_y
    request.dest_x = dest_x
    request.dest_y = dest_y
    request.ship_id = ship_id
    if ups_order is not None:
        # request.ups_order = ups_order
        request.ups_order.CopyFrom(ups_order)
    return request

def truckArrived(seq_num, ship_id, truck_id):
    truck = TruckArrived()
    truck.seq_num = seq_num
    truck.ship_id = ship_id
    truck.truck_id = truck_id
    return truck

def deliverPackage(seq_num, ship_id):
    package = DeliverPackage()
    package.seq_num = seq_num
    package.ship_id = ship_id
    return package

def u2aDelivered(seq_num, ship_id):
    package = U2ADelivered()
    package.seq_num = seq_num
    package.ship_id = ship_id
    return package

def a2uCmd(truckReqs_list=None, DeliverReqs_list=None, acks_list=None, error_list=None):
    command = AtoUCommands()
    if truckReqs_list is not None:
        command.truckReqs.extend(truckReqs_list)
    if DeliverReqs_list is not None:
        command.delivReqs.extend(DeliverReqs_list)
    if acks_list is not None:
        command.acks.extend(acks_list)
    if error_list is not None:
        command.error.extend(error_list)
    return command

def u2aCmd(arrived_list=None, delivered_list=None, error_list=None, acks_list=None, dest_list=None):
    command = UtoACommands()
    if arrived_list is not None:
        command.arrived.extend(arrived_list)
    if delivered_list is not None:
        command.delivered.extend(delivered_list)
    if error_list is not None:
        command.error.extend(error_list)
    if arrived_list is not None:
        command.acks.extend(acks_list)
    if dest_list is not None:
        command.dest.extend(dest_list)
    return command

def error(err, originseqnum, seqnum):
    error = Err()
    error.err = err
    error.originseqnum = originseqnum
    error.seqnum = seqnum
    return error

def createUPSOrder(UPSuserId, product_list=None):
    order = UPSOrder()
    order.UPSuserId = UPSuserId
    if product_list is not None:
        order.product.extend(product_list)
    return order

def createProduct(productId, productCount, productDescription):
    product = Product()
    product.productId = productId
    product.productCount = productCount
    product.productDescription = productDescription
    return product

def createFinalDest(seqnum, shipid, dest_x, dest_y):
    dest = FinalDest()
    dest.seq_num = seqnum
    dest.ship_id = shipid
    dest.dest_x = dest_x
    dest.dest_y = dest_y
    return dest