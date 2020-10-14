# !/usr/bin/env python
# -*- coding: utf-8 -*-


# cd ~/PhoenixGo
# bazel-bin/mcts/mcts_main --gtp --config_path=etc/mcts_1gpu.conf --logtostderr --v=0 --listen_port=50007


import socket
import logging

import sys
sys.path.append('/home/xm/gitrepo/ros_marlin_bridge/go_game_board')
from chessboard_cell import ChessboardCell
from chessboard import ChessboardLayout

sys.path.append('/home/xm/gitrepo/ros_marlin_bridge/app_global')
from color_print import CONST
from go_game_config import app_config


class GoGameAiClient(object):
    '''
    Connet to PhonixGo, or any other Go player.
    Via TCP socket.
    The player must be running in cloud, 
    '''
    def __init__(self):
        self.layout = ChessboardLayout('AI layout')
        self.__is_connected = False
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # 定义socket类型，网络通信，TCP

        self.__BLANK = app_config.game_rule.cell_color.blank
        self.__BLACK = app_config.game_rule.cell_color.black
        self.__WHITE = app_config.game_rule.cell_color.white

        self.__FC_BLACK = app_config.game_rule.cell_color.black

    def __connect_to_server(self):
        if self.__is_connected:
            logging.warn('GoGameAiCient: connect() is invoked when connected')
            return

        server = app_config.server.AI.ip
        port = app_config.server.AI.port
        # self.__ai_go.connect(server, port)
         # try:
        print('>>>>>>>>>>>>>>>>>>>>>>>>>> server: %s Port: %d'%(server, port))
        self.__socket.connect((server, port))       # 要连接的IP与端口
        print('>>>>>>>>>>>>>>>>>>>>>>>>>> PhoenixGo is Connected >>>>>>>>>>>>>')
            # return True
        # except ConnectionRefusedError:
        #     return False
        self.__is_connected = True

    def __disconnct(self):
        self.__socket.close()   # 关闭连接`
        self.__is_connected = False

    def __to_ai(self, command):
        command += '\n'
        self.__socket.sendall(command.encode())      # 把命令发送给对端
        data = self.__socket.recv(1024)     # 把接收的数据定义为变量'
        
        receiving = True
        while receiving:
            if(data.count(b'\n\n') > 0):
                receiving = False
            else:
                data = data + self.__socket.recv(1024)
        text = data.decode().replace("\n\n", "")
        return text
    

    def list_commands(self):
        the_list = self.__to_ai('list_commands')
        print(the_list)

    def get_board(self):
        '''
        PhoenixGo doesn't support this command.
        See list_commands()
        '''
        ret = self.__to_ai('showboard')
        print ret

    def start_new_game(self):
        self.__connect_to_server()
        ret = self.__to_ai("clear_board")
        if(ret.count("=") > 0):
            print("AI棋盘: 清空成功\r\n")
            self.layout.clear()
            app_config.current_game.lastest_move_cell_name = None
        else:
            logging.error('Start ai player error! ')

    def stop_game(self):
        self.__disconnct()

    def get_ai_move(self):
        # AI computing
        ret = self.__to_ai('genmove b')
        cell_name = ret.replace("= ", "")
        self.layout.play(cell_name, self.__FC_BLACK)
        app_config.current_game.lastest_move_cell_name = cell_name
        return cell_name

    def feed_user_move(self, cell_name):
        self.layout.play(cell_name,self.__WHITE)
        command = "play w " + cell_name
        ret = self.__to_ai(command)
        if ret.decode().count("=") > 0:
            app_config.current_game.lastest_move_cell_name = cell_name
            return
        else:
            logging.warn('feed_user_move() ret=%s' %ret)


if __name__ == "__main__":

    runner = GoGameAiClient()
    conn = runner.start_new_game()
    print(conn)
    runner.list_commands()
    runner.start_new_game()
    runner.feed_user_move('Q4')
    cell_name = runner.get_ai_move()
    print(cell_name)
    runner.stop_game()


    # while True:
    #     # runner.get_ai_move()
    #     runner.get_board()

    runner.__disconnct()

 