# -*- coding:utf-8 -*-

import socket
import select
import struct
import json


HOST = ("127.0.0.1", 8000)
HOST2 = ("127.0.0.1", 8001)


def chat_robot():
    res = b""
    while True:
        recv = yield res
        if b"hello" in recv or b"hi" in recv:
            res = "Ni hao!"
        elif b"name" in recv:
            res = "I am smart robot!"
        elif b"love" in recv:
            res = "I love you!"
        else:
            res = "Sorry, I cant't understand your say!"


class SocketServer(object):
    def __init__(self):
        self.sk1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sk1.bind(HOST)
        self.sk1.listen(10)

        self.sk2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sk2.bind(HOST2)
        self.sk2.listen(10)

        self.r_inputs = [self.sk1, self.sk2]
        self.w_inputs = []

        self.robot = chat_robot()
        self.robot.__next__()

    def handler(self):
        while True:
            r, w, e = select.select(self.r_inputs, self.w_inputs, [], 0.05)
            for obj in r:
                if obj in [self.sk1, self.sk2]:
                    print("New connection is come:", obj)
                    conn, addr = obj.accept()
                    self.r_inputs.append(conn)
                else:
                    print("Have user send data:", obj)
                    try:
                        data_length = obj.recv(4)
                    except ConnectionResetError:
                        data_length = b""

                    if data_length:
                        self.w_inputs.append(obj)
                        data_size = struct.unpack("i", data_length)[0]
                        data_json = obj.recv(data_size)
                        data = json.loads(data_json.decode())
                        rec_size = 0
                        data_size = data.get("data_size")
                        recv_data = b""
                        if data.get("action") == "chat":
                            while rec_size < data_size:
                                res = obj.recv(1024)
                                recv_data += res
                                rec_size += len(res)
                            self.chat(recv_data)
                        elif data.get("action") == "upload":
                            file_name = data.get("file_name")
                            with open(file_name, "wb") as f:
                                while rec_size < data_size:
                                    res = obj.recv(1024)
                                    f.write(res)
                                    rec_size += len(res)

                    else:
                        obj.close()
                        self.r_inputs.remove(obj)
                        if self.w_inputs:
                            self.w_inputs.remove(obj)

    def chat(self, data):
        for obj in self.w_inputs:
            robot_res = self.robot.send(data)
            print(robot_res)
            obj.sendall(bytes(robot_res, encoding="utf-8"))
            self.w_inputs.remove(obj)


if __name__ == '__main__':
    sk = SocketServer()
    sk.handler()