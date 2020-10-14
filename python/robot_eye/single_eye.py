
import cv2
import numpy as np
import threading
import click
import rospy  # only for sleep


import sys
sys.path.append('/home/xm/gitrepo/gogame_bot/python')
from go_game_board.chessboard import ChessboardLayout, DiedAreaScanner
from app_global.go_game_config import app_config, CvDebugger
from app_global.color_print import CONST


from mark_scanner import MarkScanner
from board_scanner import BoardScanner
from layout_scanner import LayoutScanner

class CvWindows():
    def __init__(self):
        self.name = 'origin'
        self.is_shown = True
        self.pos_x = 40
        self.pos_y = 30
        self.__showing_windows = {'origin':[True,40,30], 
                          'candy':[True,400,30], 
                          'chessboard':[False,40,300]
                          }

    def from_name(self, window_name):
        self.name = window_name
        self.is_shown = self.__showing_windows[window_name][0]
        self.pos_x = self.__showing_windows[window_name][1]
        self.pos_y = self.__showing_windows[window_name][2]
        return self

    def get_window(self,window_name):
        target = CvWindows()
        target.name = window_name
        target.is_shown = self.__showing_windows[window_name][0]
        target.pos_x = self.__showing_windows[window_name][1]
        target.pos_y = self.__showing_windows[window_name][2]
        return target

    def get_all_windows(self):
        return self.__showing_windows


class SingleEye():

    def __init__(self):
        self.__mark_scanner = MarkScanner()
        self.__board_scanner = BoardScanner()
        self.__layout_scanner = LayoutScanner()
        self.__capture_device = cv2.VideoCapture(app_config.robot_eye.camera_index)

        self.windows={'original':'original','candy':'candy','chessboard':'chessboard'}
        self.__cvWindow = CvWindows()
        self.__thread_eyes = {}

        self.__FC_YELLOW = CONST.print_color.fore.yellow
        self.__FC_RESET = CONST.print_color.control.reset
        self.__MARK_STABLE_DEPTH = app_config.robot_eye.mark_scanner.stable_depth
        self.__LAYOUT_STABLE_DEPTH = app_config.robot_eye.layout_scanner.stable_depth

    def __capture_newest_image(self):
        ret, img = self.__capture_device.read()
        ret, img = self.__capture_device.read()
        ret, img = self.__capture_device.read()
        ret, img = self.__capture_device.read()
        ret, img = self.__capture_device.read()
        if app_config.robot_eye.show_origin:
            CvDebugger.show_debug_image ('orign',img, ' ')
            # cp = img.copy()
            # debug_text = '  ' + datetime.now().strftime('%s')
            # cv2.putText(cp, debug_text, (10,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 1)
            # cv2.imshow('origin', cp)

            # cv2.waitKey(1)
        return ret, img

    def get_stable_layout(self,min_stable_depth):
        stable_depth = 0
        while stable_depth < min_stable_depth:
            ret, img_origin = self.__capture_newest_image()
            if ret:
                # got origin image
                img_board = self.__board_scanner.get_whole_area_of_chessboard(img_origin)
                if img_board is not None:
                    # got board image
                    layout, stable_depth = self.__layout_scanner.start_scan(img_board, self.__LAYOUT_STABLE_DEPTH)
        layout.rename_to('stable detect layout (depth = %d)' % stable_depth)
        return layout

    def get_stable_mark(self,min_stable_depth):
        stable_depth = 0
        while stable_depth < min_stable_depth:
            ret, img = self.__capture_device.read()
            ret, img = self.__capture_device.read()
            ret, img = self.__capture_device.read()
            ret, img = self.__capture_device.read()
            ret, img = self.__capture_device.read()
            if ret:
                mark_index, stable_depth = self.__mark_scanner.detect_mark(img, min_stable_depth)
        return mark_index
        
    def start_show(self,eye_name):
        xx = self.__cvWindow.get_all_windows()[eye_name]
        xx[0] = True
        # self.__thread_eye = threading.Thread(target=self.__robot_eye.monitor)
        if self.__thread_eyes.get(eye_name) == None:
            self.__thread_eyes[eye_name] = threading.Thread(target=self.__start_show, args=[eye_name])
            self.__thread_eyes[eye_name].start()
            
    def stop_show(self, eye_name):
        # this_window = self.__cvWindow.get_window(window_name)
        self.__cvWindow.get_all_windows()[eye_name][0] = False

    def monitor_all(self):
        '''
        Should be in an individual thread. 
        '''
        for this_window in self.__cvWindow.get_all_windows():
            obj_window = self.__cvWindow.from_name(this_window)
            cv2.namedWindow(obj_window.name)
            cv2.moveWindow(obj_window.name, obj_window.pos_x, obj_window.pos_y)

        while True:
            # https://stackoverflow.com/questions/3294889/iterating-over-dictionaries-using-for-loops
            for name,values in self.__cvWindow.get_all_windows().iteritems():
                if values[0]:
                    ret,frame = self.__capture_device.read()
                    # ret,frame = self.__capture_device.read()
                    cv2.imshow(name, frame)
                    cv2.waitKey(1)



if __name__ == '__main__':
    # How can show two video window,  from one threads?
    # myrobotEye.start_show('candy')
    myrobotEye = SingleEye()
    while True:
        menu = []
        menu.append('***********************************************************')
        menu.append('* 1. (TODO) List cameras, You can see the IDs.            *')
        menu.append('* 2. Capture image from camera (id = 0)                   *')
        menu.append('* 3.                                           *')
        menu.append('* 4. get_stable_layout()                                  *')
        menu.append('* 5. Scan instruction marks(mode=?)                       *')
        menu.append('* 6. get_stable_mark()                                    *')
        menu.append('* 7. Died_area_scanner                                    *')
        menu.append('***********************************************************')

        # for m in menu:
        #     print(m)

        # key = click.getchar()
        key = '4'
        if key == '1':
            pass

        elif key == '2':
            myrobotEye.show_origin()

        elif key == '3':
            layout.print_out()

        elif key == '4':
            layout = myrobotEye.get_stable_layout(app_config.robot_eye.layout_scanner.stable_depth)
            layout.print_out()

        elif key == '5':
            myrobotEye.scan_mark_to_command(mode=3)

        elif key == '6':
            myrobotEye.get_stable_mark(5)

        elif key == '7':
            scanner =  DiedAreaScanner()
            print('1111111111111111111')
            layout =  myrobotEye.get_stable_layout(5)
            print('2222222222222')
            scanner.set_layout_array(layout.get_layout_array())
            print('3333333333333')
            scanner.start_scan(app_config.game_rule.cell_color.black)
            print('444444444444')
            scanner.print_out_died_area()
            rospy.sleep(333)
