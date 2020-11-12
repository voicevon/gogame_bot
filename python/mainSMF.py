#!/usr/bin/env python
# -*- coding: utf-8 -*-


# roslaunch go_scara_moveit demo.launch


# cd ~/PhoenixGo
# bazel-bin/mcts/mcts_main --gtp --config_path=etc/mcts_1gpu.conf --logtostderr --v=0 --listen_port=50007

# sudo chmod 666 /dev/ttyUSB0

import sys
sys.path.append('/home/xm/gitrepo/gogame_bot/python')
from robot_eye.single_eye import SingleEye

from gogame_board.chessboard import ChessboardLayout, DiedAreaScanner
from gogame_board.chessboard_cell import ChessboardCell

from robot_arm.human_level_robot import HumanLevel_RobotArm

from app_global.color_print import CONST
from app_global.gogame_config import app_config

from gogame_ai_client import GoGameAiClient
import paho.mqtt.client as mqtt
import time
import logging


class GoManager():

    def __init__(self):
        self.__goto = self.at_state_game_over
        self.__ai_go = GoGameAiClient()
        self.__eye = SingleEye()
        self.__arm = HumanLevel_RobotArm(app_config.robot_arm.name)
        self.__died_area_scanner = DiedAreaScanner()
        self.__mqtt = mqtt.Client("xuming-2038-2334") #create new instance
        self.__target_demo_layout = ChessboardLayout('Demo_target')

        self.__BLACK = app_config.game_rule.cell_color.black
        self.__WHITE = app_config.game_rule.cell_color.white
        self.__BLANK = app_config.game_rule.cell_color.blank
        self.__MARK_STABLE_DEPTH = app_config.robot_eye.mark_scanner.stable_depth
        self.__LAYOUT_STABLE_DEPTH = app_config.robot_eye.layout_scanner.stable_depth

        self.__FC_YELLOW = CONST.print_color.fore.yellow
        self.__FC_GREEN = CONST.print_color.fore.green
        self.__FC_PINK = CONST.print_color.fore.pink
        self.__FC_RESET = CONST.print_color.control.reset
        self.__BG_RED = CONST.print_color.background.red
        self.__BOLD = CONST.print_color.control.bold

    def start_arm(self):
        self.__arm.bridge_soft_robot_connect_to_moveit()
        self.__arm.bridge_hard_robot_connect_to_marlin()
        self.__arm.bridge_hard_robot_home_all_joints()

    def start_mqtt(self):
        broker = app_config.server.mqtt.broker_addr
        uid = app_config.server.mqtt.username
        psw = app_config.server.mqtt.password
        self.__mqtt.username_pw_set(username=uid, password=psw)
        self.__mqtt.connect(broker)
        print(self.__FC_GREEN + '[Info]: MQTT has connected to: %s' %broker)
        app_config.server.mqtt.client = self.__mqtt
        self.__mqtt.loop_start()
        self.__mqtt.subscribe("gogame/eye/cell_scanner/inspecting/cell_name")
        self.__mqtt.publish(topic="fishtank/switch/r4/command", payload="OFF", retain=True)
        self.__mqtt.on_message = self.__mqtt_on_message
        # self.__mqtt.loop_stop()

    def __mqtt_on_message(self, client, userdata, message):
        print("message received " ,str(message.payload.decode("utf-8")))
        print("message topic=",message.topic)
        print("message qos=",message.qos)
        print("message retain flag=",message.retain)
        if message.topic == 'gogame/eye/cell_scanner/inspecting/cell_name':
            print('MQTT command: Update inspecting cell to:    %s' %message.payload)
            app_config.robot_eye.layout_scanner.inspecting.cell_name = message.payload

    def __remove_one_cell_to_trash(self, color):
        '''
        return: how many chesses have benn removed
            0 = zero chess has been removed
            1 = one chess has been removed
        '''
        the_layout = self.__eye.get_stable_layout(self.__LAYOUT_STABLE_DEPTH)
        the_layout.print_out()
        cell = the_layout.get_first_cell(color)
        if cell is not None:
            print (self.__FC_GREEN + '[INFO]: GoManager.__remove_one_cell_to_trash() ' + cell.name + self.__FC_RESET)
            # move the first chess cell to trash
            # cell = ChessboardCell()
            # cell.from_col_row_id(col_id=col, row_id=row)
            self.__arm.action_pickup_chess_from_a_cell(cell.name)
            self.__arm.action_place_chess_to_trash_bin()
            return 1
        return 0

    def __remove_died_area_(self, target_color_code):
        '''
        Will do:
            1. check died area
            2. remove died cells on __ai_layout
        Will not do:
            3. remove cells phisically with robot arm
        '''
        died_area_helper = DiedAreaDetector()
        area = died_area_helper.start(self.__ai_go.layout.get_layout_array(), target_color_code)
        for col in range(0,19):
            for row in range(0,19):
                if area[col][row] == 0:
                    cell = ChessboardCell()
                    cell.from_col_row_id(col,row)
                    # self.__arm.action_pickup_chess_from_a_cell(cell.name)
                    # self.__arm.action_place_chess_to_trash_bin()
                    self.__ai_go.layout.play_col_row(col,row,self.__BLANK)

    def at_state_begin(self):
        # scan the marks, to run markable command
        command = self.__eye.get_stable_mark(self.__MARK_STABLE_DEPTH)

        if command == 4:
            self.__ai_go.start_new_game()
            self.__mqtt.publish('gogame/smf/status', 'computer_playing', retain=True)
            self.__goto = self.at_state_computer_play
        else:
            print(self.__FC_YELLOW + '[Warning]: GoManger.at_begining()  scanned command=%d' %command)
            self.__goto = self.at_state_game_over

    def at_state_game_over(self):
        # scan the marks, to run markable command
        command = self.__eye.get_stable_mark(self.__MARK_STABLE_DEPTH)
        if command == 0:
            self.__goto = self.at_demo_from_warehouse
        
        if command == 1:
            self.__goto = self.at_demo_mover

        if command == 2:
            self.__goto = self.at_demo_remove_to_trashbin_black
  
        elif command == 3:
            self.__goto = self.at_demo_remove_to_trashbin_white


        elif command == 4:
            self.__goto = self.at_state_begin
            self.__mqtt.publish('gogame/smf/status','begining',retain=True)
        else:
            print(self.__FC_YELLOW + '[Warning]: GoManger.at_begining()  scanned command=%d' %command)

    def at_state_computer_play(self):
        self.__ai_go.get_final_score()
        # get command from PhonixGo
        cell_name = self.__ai_go.get_ai_move()
        if cell_name is not None:
            # some time the ai_player will return a 'resign' as a cell name.
            logging.info(self.__FC_PINK + 'AI step: place black at: %s' %cell_name + self.__FC_RESET)
            # robot arm play a chess, The instruction is from AI.
            self.__arm.action_pickup_chess_from_warehouse()
            self.__arm.action_place_chess_to_a_cell(cell_name=cell_name)
            self.__ai_go.layout.play(cell_name, self.__BLACK)

        self.__goto = self.at_state_scan_died_white

    def at_state_withdraw_white(self):
        cell = self.__died_area_scanner.get_first_died_cell()
        if cell is None:
            # There is no died area to be removed
            self.__goto = self.at_state_compare_layout_black
        else:
            # only remove one cell of the died area.
            # will go on to remove other cells on the next invoking
            self.__arm.action_pickup_chess_from_a_cell(cell.name)
            self.__arm.action_place_chess_to_trash_bin()
            self.__ai_go.layout.play(cell.name, self.__BLANK)
            self.__died_area_scanner.died_cell_removed_first_one()

    def at_state_withdraw_black(self):
        cell = self.__died_area_scanner.get_first_died_cell()
        if cell is None:
            # There is no died area to be removed
            self.__goto = self.at_state_compare_layout_white
        else:
            # only remove one cell of the died area.
            # will go on to remove other cells on the next invoking
            self.__arm.action_pickup_chess_from_a_cell(cell.name)
            self.__arm.action_place_chess_to_trash_bin()
            self.__ai_go.layout.play(cell.name, self.__BLANK)
            self.__died_area_scanner.died_cell_removed_first_one()

    def at_state_scan_died_black(self):
        self.__died_area_scanner.set_layout_array(self.__ai_go.layout.get_layout_array())
        count = self.__died_area_scanner.start_scan(self.__BLACK)
        if count > 0:
            self.__died_area_scanner.print_out_died_area()

        self.__goto = self.at_state_withdraw_black

    def at_state_scan_died_white(self):
        self.__died_area_scanner.set_layout_array(self.__ai_go.layout.get_layout_array())
        count = self.__died_area_scanner.start_scan(self.__WHITE)
        if count > 0:
            self.__died_area_scanner.print_out_died_area()
        self.__goto = self.at_state_withdraw_white

    def at_state_compare_layout_white(self):
        layout = self.__eye.get_stable_layout(self.__LAYOUT_STABLE_DEPTH)
        diffs = self.__ai_go.layout.compare_with(layout)
        if len(diffs) == 0:
            self.__goto = self.at_state_computer_play
        else: 
            diffs = self.__ai_go.layout.compare_with(layout, do_print_out=True)
            time.sleep(10)

    def at_state_compare_layout_black(self):
        layout = self.__eye.get_stable_layout(self.__LAYOUT_STABLE_DEPTH)
        diffs = self.__ai_go.layout.compare_with(layout)

        same = False
        if len(diffs) == 0:
            same = True
        elif len(diffs) == 1:
            # Only one cell is different.
            cell_name, ai_color, scanned_color = diffs[0]
            if scanned_color == self.__WHITE:
                # And the scanned layout says: it's white color, because it's put by user, He runs so fast! :)
                same = True
        if same:
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  Now please place your chess onto the board. ')
            self.__goto = self.at_state_user_play
            self.__mqtt.publish('gogame/smf/status','user_playing',retain=True)
            self.__mqtt.publish(topic="fishtank/switch/r4/command",payload="ON",retain=True)
        else:
            # more than one cells are different,  or the only one different cell is black color. 
            diffs = self.__ai_go.layout.compare_with(layout, do_print_out=True)
            time.sleep(10)

    def at_state_user_play(self):
        # check mark command, might be game over. 
        mark = self.__eye.get_stable_mark(self.__MARK_STABLE_DEPTH)
        
        if mark != 4:
            # Game over: 
            print(self.__BOLD + self.__FC_YELLOW + self.__BG_RED + 'Game Over!' + self.__FC_RESET)

            key = raw_input('Please confirm Game over by input "over"  ')
            if key == 'over':
                self.__ai_go.layout.clear()
                self.__ai_go.stop_game()
                self.__mqtt.publish('gogame/smf/status','game_over', retain=True)
                self.__goto = self.at_state_game_over
                return

        stable_layout = self.__eye.get_stable_layout(self.__LAYOUT_STABLE_DEPTH)
        do_print_diffs = False
        diffs = self.__ai_go.layout.compare_with(stable_layout)
        if len(diffs) == 0:
            # there is no use move
            pass
        elif len(diffs) == 1:
            # detected user move, and only one move, need to check color
            for cell_name, ai_color,detected_color in diffs:
                if ai_color==self.__BLANK and detected_color==self.__WHITE:
                    # detected cell is  White color. Means user put in a cell
                    print(self.__FC_PINK + 'detected: user has placed to cell: ' + cell_name)
                    # send command to PhonixGo
                    self.__ai_go.feed_user_move(cell_name)
                    self.__ai_go.layout.print_out()
                    self.__mqtt.publish('gogame/smf/status', 'computer_playing', retain=True)
                    self.__mqtt.publish(topic="fishtank/switch/r4/command", payload="OFF", retain=True)
                    self.__goto = self.at_state_scan_died_black
                    return
                else:
                    do_print_diffs = True
                    # self.__ai_go.layout.print_out()
                    # stable_layout.print_out()
        else:
            # more than one different, 
            # reason A: died area has not been entirely removed
            # reason B: detection is wrong
            # reason C: layout has benn disterbed by user. Like children playing bad with angry.
            do_print_diffs = True

        if do_print_diffs:
            diffs = self.__ai_go.layout.compare_with(stable_layout, do_print_out=True)
            print(self.__BG_RED + self.__FC_YELLOW + 'Too many different the between two layout.' + self.__FC_RESET)

        # print(diff_cell_name,my_color,detected_color)
        # logging.warn('diff_cell_name=%s, my_color=%d, detected_color=%d' %(diff_cell_name, my_color, detected_color))

    def main_loop(self):
        last_function = self.__goto
        self.__goto()
        if last_function != self.__goto:
            print(CONST.print_color.background.blue + CONST.print_color.fore.yellow)
            print(self.__goto.__name__)
            print(CONST.print_color.control.reset)

    def start(self):
        self.start_arm()
        self.start_mqtt()

    def at_demo_from_warehouse(self):
        layout = self.__eye.get_stable_layout(self.__MARK_STABLE_DEPTH)
        layout.print_out()
        cell = layout.get_first_cell(self.__BLANK)
        self.__arm.action_pickup_chess_from_warehouse()
        self.__arm.action_place_chess_to_a_cell(cell.name)
        # layout = self.__eye.get_stable_layout(self.__MARK_STABLE_DEPTH)
        # layout.print_out()
        self.__goto = self.at_state_game_over

    def at_demo_remove_to_trashbin_black(self):
        count = self.__remove_one_cell_to_trash(self.__BLACK)
        if count == 0:
            self.__remove_one_cell_to_trash(self.__WHITE)  
        self.__goto = self.at_state_game_over

    def at_demo_remove_to_trashbin_white(self):
        count = self.__remove_one_cell_to_trash(self.__WHITE)
        if count == 0:
            self.__remove_one_cell_to_trash(self.__BLACK)
        self.__goto = self.at_state_game_over

    def at_demo_mover(self):  # Must be no arguiment function for self.__goto
        do_vision_check = app_config.mainloop.at_demo_mover.do_vision_check
        layout = self.__eye.get_stable_layout(self.__LAYOUT_STABLE_DEPTH)
        layout.print_out()
        cell = layout.get_first_cell(self.__BLACK)
        if cell is not None:
            print('First black cell = %s' % cell.name)
            # self.__target_demo_layout.set_cell_value(cell.col_id, cell.row_id, self.__BLACK)
            id_black = cell.id
            self.__target_demo_layout.set_cell_value(cell.col_id, cell.row_id, self.__BLACK)
            cell = layout.get_first_cell(self.__WHITE)
            if cell is not None:
                self.__target_demo_layout.set_cell_value(cell.col_id, cell.row_id, self.__WHITE)
                print('First white cell = %s' % cell.name)
                # self.__target_demo_layout.set_cell_value(cell.col_id, cell.row_id, self.__WHITE)
                id_white = cell.id
                id = id_black
                if id_white < id_black:
                    id = id_white
                
                for i in range(id,359):
                    cell.from_id(i)
                    cell_color = layout.get_cell_color_col_row(cell.col_id, cell.row_id)
                    self.__arm.action_pickup_chess_from_a_cell(cell.name)
                    self.__target_demo_layout.set_cell_value(cell.col_id, cell.row_id, self.__BLANK)
                    cell.from_id(i+2)
                    self.__arm.action_place_chess_to_a_cell(cell.name,auto_park=do_vision_check)
                    self.__target_demo_layout.set_cell_value(cell.col_id, cell.row_id, cell_color)
                    if do_vision_check:
                        layout = self.__eye.get_stable_layout(self.__LAYOUT_STABLE_DEPTH)
                        diffs = layout.compare_with(self.__target_demo_layout, do_print_out = True)
                        if len(diffs) > 0:
                            cell_name, source_cell_color, target_cell_color = diffs[0]
                            app_config.robot_eye.layout_scanner.inspecting.cell_name = cell_name
                            key = raw_input ('Test failed! Please check')
                self.__arm.action_pickup_chess_from_a_cell('B19')
                self.__arm.action_place_chess_to_trash_bin(park_to_view_point=False)
                self.__target_demo_layout.set_cell_value_from_name('B19',self.__BLANK)
                self.__arm.action_pickup_chess_from_a_cell('A19')
                self.__arm.action_place_chess_to_trash_bin(park_to_view_point=True)
                self.__target_demo_layout.set_cell_value_from_name('A19',self.__BLANK)
                
        self.__goto = self.at_state_game_over

    def at_ending_demo(self):
        self.__goto = self.at_ending_demo

    def test_die_area_detector(self):
        layout = self.__eye.get_stable_layout(self.__MARK_STABLE_DEPTH)
        layout.print_out()
        
        die_helper = DiedAreaDetector()
        die_helper.start(layout.get_layout_array(),self.__BLACK)



if __name__ == "__main__":

    #
    #   ^-----------> demo_from_wherehouse -------->|
    #   ^                                           |
    #   ^-----------> demo_to_trashbin ------------>|
    #   ^                                           |
    #   ^-----------> demo_remove_white ----------->|
    #   ^                                           |
    #   ^-----------> demo_remove_black ----------->|
    #   ^                                           |
    #   ^     |<-------- ending demo <--------------|
    #   ^     |
    #  game_over ---> begin ---> computer_playing ---> scan_died_white ---> draw_white ---> compare_black ---> user_playing
    #   ^                           ^                                                                             |
    #   ^                           |<-- compare_white <---- draw_black <-----scan_died_black <-------------------|
    #   ^                                                                                                         |
    #   ^---------------------------------------------------------------------------------------------------------|

    k = 1
    if k==1:
        system = GoManager()
        system.start()
        while True:
            system.main_loop()
    if k==2:
        test = GoManager()
        test.test_die_area_detector()