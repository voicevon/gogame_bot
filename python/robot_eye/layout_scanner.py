#!/usr/bin/env python
# -*- coding: utf-8 -*-


from cell_scanner import CellScanner
import cv2
import numpy

import sys
sys.path.append('/home/xm/gitrepo/gogame_bot/python')
from gogame_board.chessboard import ChessboardLayout, ChessboardCell
from app_global.color_print import CONST
from app_global.gogame_config import app_config

class LayoutScanner():

    def __init__(self):
        self.__detected_layout = ChessboardLayout('Detected layout')

        # history
        self.__history = []
        self.__history_length = 0 
        # self.__diffs = []

        self.__BLANK = app_config.game_rule.cell_color.blank
        self.__BLACK = app_config.game_rule.cell_color.black
        self.__WHITE = app_config.game_rule.cell_color.white
        self.__ROWS = app_config.game_rule.board_size.row 
        self.__COLS = app_config.game_rule.board_size.col

        self.__SPACE_X = app_config.robot_eye.cell_scanner.dimension.cell_space_x
        self.__SPACE_Y = app_config.robot_eye.cell_scanner.dimension.cell_space_y
        self.__VIEW_RANGE = 1.6

        self.__inspect_cell =  ChessboardCell()
        self.__inspect_cell.from_name(app_config.robot_eye.layout_scanner.inspecting.cell_name)

        self.__FC_GREEN = CONST.print_color.fore.green
        self.__FC_YELLOW = CONST.print_color.fore.yellow
        self.__FC_RESET = CONST.print_color.control.reset


        self.Min_BlackColor = numpy.array([0, 0, 0])  # 要识别黑子颜色的下限
        self.Max_BlackColor = numpy.array([180, 255, 80])  # 要识别黑子的颜色的上限
        self.Min_WhiteColor = numpy.array([0, 0, 200])  # 要识别白子颜色的下限
        self.Max_WhiteColor = numpy.array([180, 100, 255])  # 要识别白子的颜色的上限

    
    def __append_to_history(self, layout):
        '''
        return:
            stable_depth, minimum number is 1.
        '''
        while len(self.__history) > self.__history_length:
            del self.__history[0]
        self.__history.append(layout)

        # update stable_depth
        stable_depth = 1
        if len(self.__history) > 2:
            for i in range(len(self.__history)-1):
                diffs = self.__history[-1].compare_with(self.__history[i]) 
                if len(diffs) == 0:
                    # no different
                    stable_depth += 1
        return stable_depth

    def start_scan(self, img_board, history_length=3, show_processing_image=True, pause_second=1):
        '''
        return A:
            -1,-1: not detected any layout
        return B:
            the lastest layout in history,
            stable_depth
        '''
        self.__history_length = history_length
        detected_layout = ChessboardLayout('Detected layout')

        board_gray = cv2.cvtColor(img_board, cv2.COLOR_BGR2GRAY)
        board_brightness = numpy.mean(board_gray)
        # print('board_brightness()= %d' %board_brightness)

        cell_scanner = CellScanner(board_brightness)

        # Split board_image to 361 samll images. detect circle one by one
        for col in range(0,self.__COLS):
            for row in range(0,self.__ROWS):
                # crop to small image, around cell center
                x1 = self.__SPACE_X * col 
                y1 = self.__SPACE_Y * row 
                x2 = x1 + int(self.__SPACE_X * self.__VIEW_RANGE)
                y2 = y1 + int(self.__SPACE_Y * self.__VIEW_RANGE)
                cell_img_big = img_board[y1:y2, x1:x2]

                shrink_size = 6
                x1 = self.__SPACE_X * col + shrink_size
                y1 = self.__SPACE_Y * row + shrink_size
                x2 = x1 + int(self.__SPACE_X * self.__VIEW_RANGE - 2 * shrink_size)
                y2 = y1 + int(self.__SPACE_Y * self.__VIEW_RANGE - 2 * shrink_size)
                cell_img_small = img_board[y1:y2, x1:x2]

                is_inspected_cell = False
                self.__inspect_cell.from_name(app_config.robot_eye.layout_scanner.inspecting.cell_name)
                if (col == 18 - self.__inspect_cell.col_id) and (18- row == self.__inspect_cell.row_id):
                    cv2.imshow('bbbb',cell_img_big)
                    cv2.imshow('ssss',cell_img_small)
                    is_inspected_cell = True

                # color = cell_scanner.scan(cell_img,is_inspected_cell)
                color = cell_scanner.scan_white(cell_img_big, is_inspected_cell)
                detected_layout.play_col_row(col_id=18-col, row_id=18-row, color_code=color)
                if color != self.__WHITE:
                    color = cell_scanner.scan_black(cell_img_small, is_inspected_cell)
                    detected_layout.play_col_row(col_id=18-col, row_id=18-row, color_code=color)

        stable_depth = self.__append_to_history(detected_layout)
        # target_layout.print_out()
        if app_config.robot_eye.layout_scanner.show_scan_image:
            self.__show_debug(img_board,stable_depth)


        return self.__history[-1], stable_depth


    def __show_debug(self, img_board,stable_depth):
        copy = img_board.copy()
        cv2.putText(copy, 'Depth= ' + str(stable_depth),(10,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),1)
        if len(self.__history) > 2:
            diffs = self.__history[-1].compare_with(self.__history[-2])
            text = ''
            for name,color_a, color_b in diffs:
                text += '' + name + ','
               # draw a red circle on each different cells
                diff_cell = ChessboardCell()
                diff_cell.from_name(name)
                x,y = diff_cell.to_camera__board_xy()
                cv2.circle(copy, (x,y), 16, (0,0,255), 2)
            # draw a blue circle on last_moving cell
            cell = ChessboardCell()
            cell_name = app_config.current_game.lastest_move_cell_name
            if cell_name is not None:
                cell.from_name(cell_name)
                x,y = cell.to_camera__board_xy()
                cv2.circle(copy, (x,y),16, (255,0,0), 3)
            cv2.putText(copy, 'diffs= ' + text, (10,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 1)
            cv2.imshow('layout_scanner', copy)
            is_success, img_encode = cv2.imencode(".jpg", copy)
            if is_success:
                img_pub = img_encode.tobytes()
                app_config.server.mqtt.client.publish(topic='gogame/eye/layout_scanner/chess_board', payload=img_pub)
            cv2.waitKey(1)


if __name__ == "__main__":
    runner = LayoutScanner()