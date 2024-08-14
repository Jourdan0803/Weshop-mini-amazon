import socket
from google.protobuf.internal.encoder import _EncodeVarint
from google.protobuf.internal.decoder import _DecodeVarint32
import sys
from .world_amazon_pb2 import AConnected, AResponses

def send_message(sock, message):
    try:
        message_bytes = message.SerializeToString()
        # print(message_bytes)
        _EncodeVarint(sock.send, len(message_bytes), None)
        sock.send(message_bytes)
    except Exception as e:
        print(f"Failed to send message: {e}")


def receive_message(socket):
    msg = []
    new_pos = 0
    while True:
        try:
            ch = socket.recv(1)
            if not ch:
                return None
            msg += ch
            msg_len, new_pos = _DecodeVarint32(msg, 0)
            if new_pos != 0:
                break
        except Exception as e:
            pass
            # print("Receive error\n")
            # return None
    message = socket.recv(msg_len)
    res = AResponses()
    res.ParseFromString(message)
    return res

def receive_connect(socket):
    msg = []
    while True:
        try:
            ch = socket.recv(1)
            if not ch:
                return None
            msg += ch
            msg_len, new_pos = _DecodeVarint32(msg, 0)
            if new_pos != 0:
                # print("break")
                break
        except Exception as e:
            pass
            # print("Error in receiving message:", e)
            # return None
    
    message = socket.recv(msg_len)
    res = AConnected()
    res.ParseFromString(message)
    return res

