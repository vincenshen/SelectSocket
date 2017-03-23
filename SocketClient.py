# -*- coding:utf-8 -*-
import socket
import struct
import json
import os


HOST = ("127.0.0.1", 8000)


class SocketClient(object):
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(HOST)

    def handler(self):
        while True:
            menu = """
            --------function list---------
              chat
              upload
            ------------------------------
            """
            print(menu)
            cmd = input("Please input function>>>").strip()
            if not cmd:
                continue
            if hasattr(self, cmd):
                func = getattr(self, cmd)
                func()
            else:
                print("\033[31mInvalid cmd.\033[0m")

    def chat(self):
        while True:
            data = input("Chat with robot>>>").strip()
            if data == "bye": break
            data_head = {
                "action": "chat",
                "data_size": len(data)
            }
            self.send_response(data_head)
            self.client.sendall(bytes(data, encoding="utf-8"))
            data = self.client.recv(1024)
            print(data.decode())

    def upload(self):
        while True:
            file_name = input("Upload file>>>").strip()
            if file_name == "bye": break
            if os.path.isfile(file_name):
                file_size = os.path.getsize(file_name)
                data_head = {
                    "action": "upload",
                    "file_name": file_name,
                    "data_size": file_size
                }
                self.send_response(data_head)
                with open(file_name, "rb") as f:
                    while True:
                        block = f.read(1024)
                        if block:
                            self.client.send(block)
                        else:
                            print("transfer complete!")
                            break

    def send_response(self, data):
        """
        向Server发送数据包
        """
        data = json.dumps(data).encode()
        self.client.send(struct.pack("i", len(data)))
        self.client.send(data)


if __name__ == '__main__':
    sc = SocketClient()
    sc.handler()
