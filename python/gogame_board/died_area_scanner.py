import sys
sys.path.append('/home/xm/gitrepo/ros_marlin_bridge/perfect')
from color_print import const
from go_game_const import app_config

import logging
import time
sys.path.append('/home/xm/gitrepo/ros_marlin_bridge/go_gameboard')
from chessboard_cell import ChessboardCell


# class DiedAreaScanner():

#     def __init__(self):
#         self.__target_color_code = 3
#         self.__died_area_array = [([0] * 19) for i in range(19)]

#         self.__FC_YELLOW = const.print_color.fore.yellow
#         self.__FC_RESET = const.print_color.control.reset

#     def __is_around_alived(self, col, row):
#         '''
#         # look neibours is alive or not.
#         #       A cell might have 4 neibours,  TODO: 3 neibours, or 2 neibours
#         # return:
#         #       15 = has been waken up, because this cell is blank 
#         #       16 = has been waken up, because this cell is connected to #15
#         #       17 = has benn waken up, because this cell is connected to #16
#         '''

#         # look up,down,left,right. 
#         if row > 1:
#             s = self.__died_area_array[col][row - 1]
#             if s > 11:
#                 # upper cell is blank
#                 return s + 1
#         if col > 1:
#             s = self.__died_area_array[col - 1][row]
#             if s > 11:
#                 # left cell is blank
#                 return s + 1
#         if row < 18:
#             s = self.__died_area_array[col][row + 1]
#             if s > 11:
#                 # lower cell is blank
#                 return s + 1
#         if col < 18:
#             s = self.__died_area_array[col + 1][row]
#             if s > 11:
#                 # righ cell is blank
#                 return s + 1
#         return 0

#     def __try_to_make_alive(self, col, row):
#         '''
#         # based on neighbor's value:
#         #       15 = has been waken up, because this cell is blank 
#         #       16 = has been waken up, because this cell is connected to #15
#         # my value will be:
#         #       16 = has been waken up, because this cell is connected to #15
#         #       17 = has benn waken up, because this cell is connected to #16
#         '''
#         connecting_type = self.__is_around_alived(col,row)
#         if connecting_type > 11:
#             self.__died_area_array[col][row] = connecting_type
#             return connecting_type

#         return 0

        
#     def backword_loop(self):
#         c = 0
#         for col in range(18,-1,-1):
#             for row in range(18,-1,-1):
#                 if self.__died_area_array[col][row] == 0:
#                     # Yes, this cell wants to be waken up
#                     wake_up_type = self.__is_around_alived(col,row)
#                     if wake_up_type > 11:
#                         c += 1
#                         if wake_up_type > 17:
#                             wake_up_type = 17
#                         self.__died_area_array[col][row] = wake_up_type 
#         return c

#     def forward_loop(self):
#         count = 0
#         for col in range(0,19):
#             for row in range(0,19):
#                 if self.__died_area_array[col][row] == 0:
#                     # Yes, this cell wants to be waken up
#                     wake_up_type = self.__try_to_make_alive(col=col, row=row)
#                     if wake_up_type > 11:
#                         count += 1
#                         if wake_up_type > 17:
#                             wake_up_type = 17
#                         self.__died_area_array[col][row] = wake_up_type
#         return count

#     def start(self, layout_array, target_color_code):
#         '''
#         # 0 = assume cell is died
#         # 1 = No need to be waken up, because this cell is opposit color
#         # 15 = has been wakup up, because this cell is blank
#         '''
#         self.__init_died_area_array(layout_array, self.__target_color_code)
#         # print('inited')
#         # self.print_out()

#         count = 9999
#         while count > 0:
#             count = 0 
#             count += self.forward_loop()
#             # self.print_out()
#             count += self.backword_loop()
#             # self.print_out()
#         return self.__died_area_array


#     def print_out(self):
#         int_to_char = {0:'x ', 1:'O ', 15:'. ', 16:'- ', 17:'* ', 8:'B ', 3:'W '}
#         print()
#         print()
#         print(self.__FC_YELLOW + 'Died area')
#         cell = ChessboardCell()
#         # print column name on table head
#         header = '    '
#         for col_id in range (19,-1,-1):
#             cell.from_col_row_id(col_id=col_id, row_id=1)
#             header += cell.col_letter + ' '
#         print(self.__FC_YELLOW + header)
#         # print layout row by row
#         for row_id in range(0, 19):
#             rowNum = 19 - row_id
#             col_string = ''
#             for col_id in range(0,19):
#                 col_string += int_to_char[self.__died_area_array[18 - col_id][18 - row_id]]
#             row_string = "%02d" % rowNum + '  '
#             print (self.__FC_YELLOW + row_string + self.__FC_RESET + col_string + self.__FC_YELLOW + row_string)
#         print(self.__FC_YELLOW + header)

#     def __init_died_area_array(self, origin_array,target_color_code):
#         '''
#         # Based on origin_array
#         #       0 = Blank
#         #       3 = White
#         #       8 = Black
#         # init self.__died_area_array
#         #       0 = assume cell is died
#         #       1 = No need to be waken up, because this cell is opposit color
#         #       15 = has been wakup up, because this cell is blank
#         '''
#         # assume all target_color on the board is died.
#         for col in range(0,19):
#             for row in range(0,19):
#                 value = origin_array[col][row]
#                 if value == 0:
#                     # blank cell
#                     self.__died_area_array[col][row] = 15
#                 elif value == target_color_code:
#                     self.__died_area_array[col][row] = 0
#                 else:
#                     # oppsite color
#                     self.__died_area_array[col][row] = 1

