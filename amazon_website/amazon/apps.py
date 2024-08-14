from django.apps import AppConfig
import socket, threading
from django.conf import settings 

global_client_socket = None
def connect2back():
    front_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    front_address = ('127.0.0.1', 9009)
    front_socket.bind(front_address)
    front_socket.listen(5)

    back_socket, client_address = front_socket.accept()
    print("Connection from:", client_address)


    # back_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # back_address = ('127.0.0.1', 9009)
    # back_socket.connect(back_address)
    # print("connect with backend")

    return back_socket


class AmazonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'amazon'
    initialized = False
    def ready(self):
        if not self.initialized:
            print("connect:", self.initialized)
            self.initialized = True
            
            settings.GLOBAL_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            front_address = ('127.0.0.1', 34521)
            settings.GLOBAL_SOCKET.bind(front_address)
            settings.GLOBAL_SOCKET.listen(5)
            
            thread = threading.Thread(target=accept_connections, args=(settings.GLOBAL_SOCKET,))
            thread.daemon = True
            thread.start()
            print("test, ",global_client_socket)
    # def ready(self):
    #     if not self.initialized:
    #         print("connect:", self.initialized)
    #         self.initialized = True
            
    #         settings.GLOBAL_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    #         back_address = ('127.0.0.1', 34521)
    #         thread = threading.Thread(target=accept_connections, args=(settings.GLOBAL_SOCKET))
    #         thread.daemon = True
    #         thread.start()


# 函数用于接受连接并处理请求
def accept_connections(server_socket):
    print("Waiting for a connection...")
    while True:
        # back_socket = front_socket.connect(back_address)
        # global global_client_socket
        # global_client_socket = back_socket
        # break
        client_socket, client_address = server_socket.accept()
        # print(f"Connection accepted from {client_address}")
        global global_client_socket
        # print(f"Old Global Client Socket: {global_client_socket}")
        global_client_socket = client_socket
        # print(f"New Global Client Socket: {global_client_socket}, Local Client Socket: {client_socket}")
        # print(global_client_socket, client_socket)
