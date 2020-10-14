#!/usr/bin/env python
# -*- coding: utf-8 -*-


# cd ~/PhoenixGo
# bazel-bin/mcts/mcts_main --gtp --config_path=etc/mcts_1gpu.conf --logtostderr --v=0 --listen_port=50007


import socket


class GoGameClient(object):
    '''
    Connet to PhonixGo, or any other Go player.
    Via TCP socket.
    The player must be running in cloud, 
    '''
    def __init__(self, host, port):
        self.thread_stop = False
        self.HOST = host  # '192.168.123.201'
        self.PORT = port  # 50007
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # 定义socket类型，网络通信，TCP

    def openSocket(self):
        try:
            self.s.connect((self.HOST, self.PORT))       # 要连接的IP与端口
            return True
        except ConnectionRefusedError:
            return False

    def WriteCommand(self, command):
        self.s.sendall(command.encode())      # 把命令发送给对端

        data = self.s.recv(1024)     # 把接收的数据定义为变量'

        my_continue = True
        while my_continue:
            if(data.count(b'\n\n') > 0):
                print("Get Data:::")
                print(data)  # 输出变量
                my_continue = False
            else:
                data = data + self.s.recv(1024)
        return data

    def colseSocket(self):
        self.s.close()   # 关闭连接


myGoGameClient = GoGameClient('192.168.123.123', 50007)


if __name__ == '__main__':
    coonn = myGoGameClient.openSocket()
    print(coonn)
    test_cmd = raw_input("Input command: not 1 ")
    myGoGameClient.colseSocket()
 