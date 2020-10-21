#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('/home/xm/gitrepo/gogame_bot/python')
from app_global.color_print import CONST
from app_global.gogame_config import app_config


from chessboard_cell import ChessboardCell
import logging




class ChessboardLayout():

    def __init__(self,name):
        self.name = name

        self._ROWS = app_config.game_rule.board_size.row
        self._COLS = app_config.game_rule.board_size.col
        
        self.__BLANK = app_config.game_rule.cell_color.blank
        self.__BLANK = app_config.game_rule.cell_color.blank
        self._BLACK = app_config.game_rule.cell_color.black
        self._WHITE = app_config.game_rule.cell_color.white



        self._FC_YELLOW = CONST.print_color.fore.yellow
        self._BG_RED = CONST.print_color.background.red
        self._FC_RESET = CONST.print_color.control.reset

        self._layout_array = [([0] * self._COLS) for i in range(self._ROWS)]

    def play_col_row(self, col_id, row_id, color_code):
        cell = ChessboardCell()
        cell.from_col_row_id(col_id=col_id, row_id=row_id)
        self.play(cell.name, color_code)

    def play(self, cell_name, color_code):
        # print('[Info] ChessBoard.play(cell_name=%s,color=%s)' %(cell_name,color))
        cell = ChessboardCell()
        cell.from_name(cell_name)
        # value = self.__BLANK
        # if color =='Black':
        #     value = self._BLACK
        # elif color == 'White':
        #     value = self._WHITE
        # else:
        #     logging.info('ChessBoard.play(cell_name=%s,color=%s)' %(cell_name,color))
        self._layout_array[cell.col_id][cell.row_id] = color_code

    def print_out(self):
        int_to_char = {self.__BLANK:'. ',self._BLACK:'X ', self._WHITE:'O ',}
        print(self._FC_YELLOW + self.name)
        cell = ChessboardCell()
        # print column name on table head
        header = '    '
        for col_id in range (self._COLS,-1,-1):
            cell.from_col_row_id(col_id=col_id, row_id=1)
            header += cell.col_letter + ' '
        print(self._FC_YELLOW + header)
        # print layout row by row
        for row_id in range(0, self._ROWS):
            rowNum = self._ROWS - row_id
            col_string = ''
            for col_id in range(0,self._COLS):
                col_string += int_to_char[self._layout_array[18 - col_id][18 - row_id]]
            row_string = "%02d" % rowNum + '  '
            print(self._FC_YELLOW + row_string + self._FC_RESET + col_string + self._FC_YELLOW + row_string)
        print(self._FC_YELLOW + header)

    def get_cell_color(self, cell):
        col = cell.col
        row = cell.row
        return self.get_cell_color_col_row(col,row)

    def get_cell_color_col_row(self, col_id, row_id):
        return self._layout_array[col_id][row_id]
    
    def set_cell_value_from_name(self, cell_name, new_value):
        cell = ChessboardCell()
        cell.from_name(cell_name)
        self.set_cell_value(self, cell.col_id, self.row_id, new_value)

    def set_cell_value(self, col_id, row_id, new_value):
        self._layout_array[col_id][row_id] = new_value
        
    def compare_with(self, target_layout, do_print_out=False):
        '''
        return: 
            total_diff_cells: the number of different cells.
            last_cell_name: first cell_name that different, might be None
            my_color: color of last_cell
            target_color: color of last_cell
        '''
        diffs = []
        cell = ChessboardCell()
        my_cell_color = target_cell_color = self.__BLANK

        int_to_char = {self.__BLANK:'. ',self._BLACK:'X ', self._WHITE:'O '}
        if do_print_out:
            title = self._FC_RESET + '       ' 
            title += self._BG_RED + self._FC_YELLOW + self.name 
            title += self._FC_RESET + '                                         '
            title += self._BG_RED + self._FC_YELLOW + target_layout.name + self._FC_RESET
            print(title)

            # print column name on table head
            header = '  '
            for col_id in range (self._COLS,-1,-1):
                cell.from_col_row_id(col_id=col_id, row_id=1)
                header += cell.col_letter + ' '
            header += '  ' + header
            print(self._FC_YELLOW + header)

        # print layout row by row
        for row_id in range(self._ROWS-1, -1, -1):
            rowNum = row_id + 1
            my_col_string = target_col_string = ''
            for col_id in range(self._COLS-1, -1, -1):
                print_color = self._FC_RESET
                target_cell_color = target_layout.get_cell_color_col_row(col_id=col_id, row_id=row_id)
                if (self._layout_array[col_id][row_id] != target_cell_color):
                    #color is different
                    print_color = self._BG_RED + self._FC_YELLOW  
                    cell.from_col_row_id(col_id=col_id, row_id=row_id)
                    my_cell_color = self._layout_array[col_id][row_id]
                    diffs.append((cell.name, my_cell_color, target_cell_color))
                
                if do_print_out:
                    my_col_string += print_color + int_to_char[self._layout_array[col_id][row_id]] + self._FC_RESET
                    k = target_layout.get_cell_color_col_row(col_id, row_id)
                    target_col_string += print_color + int_to_char[k] + self._FC_RESET
            if do_print_out:
                row_string = self._FC_YELLOW + "%02d" % rowNum
                col_string = row_string +' '+ my_col_string + ' ' + row_string + '  ' + target_col_string + ' ' + row_string
                print(col_string )
        if do_print_out:
            print(self._FC_YELLOW + header)
            print(self._BG_RED + self._FC_YELLOW + '%s' %diffs + self._FC_RESET)
        return diffs
        # return total,cell.name ,my_cell_color, target_cell_color




        # for row in range(0, 19):
        #     for col in range(0, 19):
        #         target_cell_color = target_layout.get_cell_color_col_row(col_id=col,row_id=row)
        #         if (self._layout_array[col][row] != target_cell_color):
        #             cell.from_col_row_id(col_id=col, row_id=row)
        #             my_cell_color = self._layout_array[col][row]

        #             # print('[INFO]: ChessboardMap.compare_cell_map() diff at: %s' %cell.name)
        # return total,cell.name ,my_cell_color, target_cell_color

        # # self.print_cell_map()
        # # target_layout.print_cell_map()
        # # TODO: What if more than one cell are different ?
        # total = 0
        # cell = ChessboardCell()
        # my_cell_color = target_cell_color = self.__BLANK
        # for row in range(0, 19):
        #     for col in range(0, 19):
        #         target_cell_color = target_layout.get_cell_color_col_row(col_id=col,row_id=row)
        #         if (self._layout_array[col][row] != target_cell_color):
        #             cell.from_col_row_id(col_id=col, row_id=row)
        #             my_cell_color = self._layout_array[col][row]

        #             # print('[INFO]: ChessboardMap.compare_cell_map() diff at: %s' %cell.name)
        # return total,cell.name ,my_cell_color, target_cell_color
    
    def get_layout_array(self):
        return self._layout_array

    def clear(self):
        for i in range(19):
            for j in range(19):
                self._layout_array[i][j] = 0

    def rename_to(self, new_name):
        self.name = new_name

    def get_first_cell(self, target_color):
        '''
        return:
            (x,y) is the target position
            (-1,-1) means not found!
        '''
        cell = ChessboardCell()
        for row_id in range(0, self._ROWS):
            for col_id in range(0, self._COLS):
                if self._layout_array[col_id][row_id] == target_color:
                    cell.from_col_row_id(col_id,row_id)
                    return cell
        return None


class DiedAreaScanner(ChessboardLayout):
    def __init__(self):
        ChessboardLayout.__init__(self,'Died area scanner')
        self.__died_area_array = [([0] * 19) for i in range(19)]

        # self.__DIED_BLACK = self._BLACK + 100
        # self.__DIED_WHITE = self._WHITE + 100

    def __is_around_alived(self, col, row):
        '''
        # look neibours is alive or not.
        #       A cell might have 4 neibours,  TODO: 3 neibours, or 2 neibours
        # return:
        #       15 = has been waken up, because this cell is blank 
        #       16 = has been waken up, because this cell is connected to #15
        #       17 = has benn waken up, because this cell is connected to #16
        '''

        # look up,down,left,right. 
        if row > 0:
            s = self.__died_area_array[col][row - 1]
            if s > 11:
                # upper cell is blank
                return s + 1
        if col > 0:
            s = self.__died_area_array[col - 1][row]
            if s > 11:
                # left cell is blank
                return s + 1
        if row < 18:
            s = self.__died_area_array[col][row + 1]
            if s > 11:
                # lower cell is blank
                return s + 1
        if col < 18:
            s = self.__died_area_array[col + 1][row]
            if s > 11:
                # righ cell is blank
                return s + 1
        return 0

    def __try_to_make_alive(self, col, row):
        '''
        # based on neighbor's value:
        #       15 = has been waken up, because this cell is blank 
        #       16 = has been waken up, because this cell is connected to #15
        # my value will be:
        #       16 = has been waken up, because this cell is connected to #15
        #       17 = has benn waken up, because this cell is connected to #16
        '''
        connecting_type = self.__is_around_alived(col,row)
        if connecting_type > 11:
            self.__died_area_array[col][row] = connecting_type
            return connecting_type

        return 0

    def __backword_loop(self):
        c = 0
        for col in range(18,-1,-1):
            for row in range(18,-1,-1):
                if self.__died_area_array[col][row] == 0:
                    # Yes, this cell wants to be waken up
                    wake_up_type = self.__is_around_alived(col,row)
                    if wake_up_type > 11:
                        c += 1
                        if wake_up_type > 17:
                            wake_up_type = 17
                        self.__died_area_array[col][row] = wake_up_type 
        return c

    def __forward_loop(self):
        count = 0
        for col in range(0,19):
            for row in range(0,19):
                if self.__died_area_array[col][row] == 0:
                    # Yes, this cell wants to be waken up
                    wake_up_type = self.__try_to_make_alive(col=col, row=row)
                    if wake_up_type > 11:
                        count += 1
                        if wake_up_type > 17:
                            wake_up_type = 17
                        self.__died_area_array[col][row] = wake_up_type
        return count

    def start_scan(self, target_color):
        '''
        return:
            count: How many cells are died

        # 0 = assume cell is died
        # 1 = No need to be waken up, because this cell is opposit color
        # 15 = has been wakup up, because this cell is blank
        '''
        self.__init_died_area_array(self._layout_array, target_color)
        # print('inited')
        # self.print_out()

        count = 9999
        while count > 0:
            count = 0 
            count += self.__forward_loop()
            # self.print_out()
            count += self.__backword_loop()
            # self.print_out()

        count = 0
        for col in range(0, self._COLS):
            for row in range(0, self._ROWS):
                if self.__died_area_array[col][row] == 0:
                    count += 1
        return count

    def print_out_died_area(self):
        int_to_char = {0:'x ', 1:'O ', 15:'. ', 16:'- ', 17:'* ', 8:'B ', 3:'W '}
        print(self._FC_YELLOW + 'Died area')
        cell = ChessboardCell()
        # print column name on table head
        header = '    '
        for col_id in range (19,-1,-1):
            cell.from_col_row_id(col_id=col_id, row_id=1)
            header += cell.col_letter + ' '
        print(self._FC_YELLOW + header)
        # print layout row by row
        for row_id in range(0, 19):
            rowNum = 19 - row_id
            col_string = ''
            for col_id in range(0,19):
                value = self.__died_area_array[18 - col_id][18 - row_id]
                if value == 0:
                    col_string += self._BG_RED + int_to_char[value] + self._FC_RESET
                else:
                    col_string += int_to_char[value]

            row_string = "%02d" % rowNum + '  '
            print (self._FC_YELLOW + row_string + self._FC_RESET + col_string + self._FC_YELLOW + row_string)
        print(self._FC_YELLOW + header)

    def get_first_died_cell(self):
        '''
        return:
            None means not found!
        '''
        cell = ChessboardCell()
        for row_id in range(0, self._ROWS):
            for col_id in range(0, self._COLS):
                if self.__died_area_array[col_id][row_id] == 0:
                    cell.from_col_row_id(col_id,row_id)
                    return cell
        return None

    def died_cell_removed_first_one(self):
        cell = ChessboardCell()
        cell = self.get_first_died_cell()
        self.__died_area_array[cell.col_id][cell.row_id] = 15

    def __init_died_area_array(self, origin_array,target_color_code):
        '''
        # Based on origin_array
        #       0 = Blank
        #       3 = White
        #       8 = Black
        # init self.__died_area_array
        #       0 = assume cell is died
        #       1 = No need to be waken up, because this cell is opposit color
        #       15 = has been wakup up, because this cell is blank
        '''
        # assume all target_color on the board is died.
        for col in range(0,19):
            for row in range(0,19):
                value = origin_array[col][row]
                if value == 0:
                    # blank cell
                    self.__died_area_array[col][row] = 15
                elif value == target_color_code:
                    self.__died_area_array[col][row] = 0
                else:
                    # oppsite color
                    self.__died_area_array[col][row] = 1

    def set_layout_array(self,layout_array):
        self._layout_array = layout_array


class ChessboardPosition():
    '''
    unit is meter
    '''
    def __init__(self):
        self.layout = [([0] * 19) for i in range(19)]
        # below values are from manually calibrattion
        # t1 at top_left corner of XY-coordinator
        t1_x = -0.165  
        t1_y = 0.48
        # a19 at bottom_right corner of XY-coordinator
        a19_x = 0.152
        a19_y = 0.159

        self.__cell_space_x = (a19_x - t1_x) / 18
        self.__cell_space_y = (a19_y - t1_y) / 18
        self.__chessboard_left = t1_x
        self.__chessboard_bottom = t1_y

        # TODO: replace with logging 
        print('--------------------------------------------space X, Y')
        print(self.__cell_space_x)
        print(self.__cell_space_y)



    def get_interpolated_FK_from_cell(self, cell):
        # target_FK = Pose_FK()
        x = cell.col_id * self.__cell_space_x + self.__chessboard_left
        y = cell.row_id * self.__cell_space_y + self.__chessboard_bottom
        z = 0.02
        w = 0

        return x, y, z, w


    
if __name__ == "__main__":
    test1 = ChessboardLayout('Test1')
    test1.play('T19',app_config.game_rule.cell_color.black)
    test1.print_out()
    cell = test1.get_first_cell(app_config.game_rule.cell_color.black) 
    cell = ChessboardCell()
    # cell.from_col_row_id(x,y)
    print('x=%d, y=%d, name=%s' %(cell.col_id, cell.row_id, cell.name))


    test2 = ChessboardLayout('Test2')
    test2.play('T19',app_config.game_rule.cell_color.black)
    test2.play('K10',app_config.game_rule.cell_color.white)
    x = test2.compare_with(test1,do_print_out=True)
    print x
    