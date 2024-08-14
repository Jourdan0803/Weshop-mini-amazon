import socket
from google.protobuf.internal.encoder import _EncodeVarint
from google.protobuf.internal.decoder import _DecodeVarint32
import sys
from .ups_amazon_pb2 import UtoACommands


def send_command(sock, message):
    try:
        message_bytes = message.SerializeToString()
        # print(message_bytes)
        _EncodeVarint(sock.send, len(message_bytes), None)
        sock.send(message_bytes)
    except Exception as e:
        print(f"Failed to send message: {e}")


def receive_command(socket):
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
    res = UtoACommands()
    res.ParseFromString(message)
    return res