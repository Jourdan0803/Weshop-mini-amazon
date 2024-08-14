from .world_amazon_pb2 import AProduct, AInitWarehouse, AConnect, AConnected, APack, APacked, ALoaded, APutOnTruck, APurchaseMore, AErr, APackage, ACommands, AResponses, AQuery

def initProduct(id, description, count):
    product = AProduct()
    product.id = id
    product.description = description
    product.count = count
    return product

def initWarehouse(id, x, y):
    ware = AInitWarehouse()
    ware.id = id
    ware.x = x
    ware.y = y
    return ware

def initConnect(warehouse_list=None, worldid=0):
    connect = AConnect()
    if worldid != 0:
        connect.worldid = worldid
    if warehouse_list is not None:
        connect.initwh.extend(warehouse_list)
    connect.isAmazon = True
    return connect

def confirmConnect(worldid, result):
    connected = AConnected()
    connected.worldid = worldid
    connected.result = result
    return connected

def initPack(whnum, things_list, shipid, seqnum):
    pack = APack()
    pack.whnum = whnum
    pack.things.extend(things_list)
    pack.shipid = shipid
    pack.seqnum = seqnum
    return pack

def confirmPack(shipid, seqnum):
    packed = APacked()
    packed.shipid = shipid
    packed.seqnum = seqnum
    return packed

def confirmLoad(shipid, seqnum):
    loaded = ALoaded()
    loaded.shipid = shipid
    loaded.seqnum = seqnum
    return loaded

def initPutOnTruck(whnum, truckid, shipid, seqnum):
    putOnTruck = APutOnTruck()
    putOnTruck.whnum = whnum
    putOnTruck.truckid = truckid
    putOnTruck.shipid = shipid
    putOnTruck.seqnum = seqnum
    return putOnTruck

def PurchaseMore(whnum, things_list, seqnum):
    purchaseMore = APurchaseMore()
    purchaseMore.whnum = whnum
    purchaseMore.things.extend(things_list)
    purchaseMore.seqnum = seqnum
    return purchaseMore

def Error(err, originseqnum, seqnum):
    error = AErr()
    error.err = err
    error.originseqnum = originseqnum
    error.seqnum = seqnum
    return error

def initQuery(packageid, seqnum):
    query = AQuery()
    query.packageid = packageid
    query.seqnum = seqnum
    return query

def initPackage(packageid, status, seqnum):
    package = APackage()
    package.packageid = packageid
    package.status = status
    package.seqnum = seqnum
    return package

def createCmd(buy_list=None, topack_list=None, load_list=None, query_list=None, acks_list=None, simspeed=None, disconnect=False):
    cmd = ACommands()
    if buy_list is not None:
        cmd.buy.extend(buy_list)
    if topack_list is not None:
        cmd.topack.extend(topack_list)
    if load_list is not None:
        cmd.load.extend(load_list)
    if query_list is not None:
        cmd.queries.extend(query_list)
    if acks_list is not None:
        cmd.acks.extend(acks_list)

    # optinal
    if simspeed is not None:
        cmd.simspeed = simspeed
    cmd.disconnect = disconnect

    return cmd
    
def recvRes(arrived_list=None, ready_list=None, loaded_list=None, error_list=None, acks_list=None, packagestatus_list=None, finished=False):
    res = AResponses()
    if arrived_list is not None:
        res.arrived.extend(arrived_list)
    if ready_list is not None:
        res.ready.extend(ready_list)
    if loaded_list is not None:
        res.loaded.extend(loaded_list)
    if error_list is not None:
        res.error.extend(error_list)
    if packagestatus_list is not None:
        res.packagestatus.extend(packagestatus_list)
    if acks_list is not None:
        res.acks.extend(acks_list)
    if finished is not None:
        res.finished = finished
    return res