
import cv2
import numpy as np
import threading
import click
import time  # only for sleep


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

    def Toushi(self, img, x, y, w, h, contour):
        # cv2.imshow("imgss", img)
        height, width = img.shape[:2]
        dp1 = dp2 = dp3 = dp4 = 10000
        for i in range(len(contour)):
            ddp1 = abs(contour[i][0][0]-x) + abs(contour[i][0][1]-y)
            if ddp1<dp1:
                dp1 = ddp1
                pp1 = contour[i][0]
            ddp2 = abs(contour[i][0][0]-(x+w)) + abs(contour[i][0][1]-y)
            if ddp2<dp2:
                dp2 = ddp2
                pp2 = contour[i][0]
            ddp3 = abs(contour[i][0][0]-(x+w)) + abs(contour[i][0][1]-(y+h))
            if ddp3<dp3:
                dp3 = ddp3
                pp3 = contour[i][0]
            ddp4 = abs(contour[i][0][0]-x) + abs(contour[i][0][1]-(y+h))
            if ddp4<dp4:
                dp4 = ddp4
                pp4 = contour[i][0]
        pts1 = np.float32([pp1, pp2, pp3, pp4])
        pts2 = np.float32([[x, y],[x+430,y],[x+430,y+430],[x, y+430]])
        # print("pts1:{0}".format(pts1))
        # print("pts2:{0}".format(pts2))
        M = cv2.getPerspectiveTransform(pts1,pts2)
        dst = cv2.warpPerspective(img, M, (width, height))
        # cv2.imshow("dst", dst)
        return dst

    def compo(self,img):

        dst = self.Toushi(img,x,y,w,h,qipan)
        xNew = x + 0
        yNew = y + 0
        xEnd = x + self.__CROP_WIDTH
        yEnd = y + self.__CROP_HEIGHT
        # cv2.rectangle(Img,(xNew,yNew),(xEnd,yEnd),(0,255,),1)


        singleQiPan = dst[yNew:yEnd, xNew:xEnd]
        CvDebugger.show_debug_image('board_scaner', singleQiPan, 'Got it')
        return singleQiPan

    def new_idea(self,img):
        # https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
        # https://www.geeksforgeeks.org/perspective-transformation-python-opencv/


        # detect edges using Canny
        img_target = img.copy()
        img_approx = img.copy()
        canny = cv2.Canny(img, 149,150)
        cv2.imshow('canny', canny)
        # retrieve contours by findCountours
        contours, hierarchy = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        img_contour = cv2.drawContours(img, contours, -1, (0,255,75), 1)
        cv2.imshow('contours',img_contour)

        target_contour = None
        approx = None
        # print('````````````````````````````````````````````')
        for con in contours:
            rec = cv2.boundingRect(con)
            area = cv2.contourArea(con)
            if area > 17000:
                # print(rec, area)
                # target_contour.append(con)
                target_contour = con
                target_rec = rec
                # cv2.imshow('im2',im2)
                # approxPolyDP to decrease number of vericales
                epsilon = 0.1 * cv2.arcLength(con, True)
                approx = cv2.approxPolyDP(con, epsilon, True)


        # img_target = cv2.drawContours(img, target_contour, -1, (0,255,0), 2)
        # print(target_rec)
        # (rec,area) = target_contour
        x1,y1,x2,y2 = target_rec
        bounding_rectangle = cv2.rectangle(img_target,(x1,y1),(x1+x2,y1+y2),(255,0,0),2)
        cv2.imshow('target',bounding_rectangle)

        approx_image = cv2.drawContours(img_approx, approx, -1, (255,0,0),22)
        print('>>>>>>>>>>>>>>>>>>>>>>', approx)
        print('----------------------------------------------------------')
        cv2.imshow('approx', approx_image)

        # tr = approx[1]
        # print(tr)
        # x,y = tr[0]   
        # print(x,y)
        
        # source = cv2.line(img, approx)
        if len(approx) == 4:
            x_tr, y_tr = approx[0][0]
            x_tl, y_tl = approx[1][0]
            x_bl, y_bl = approx[2][0]
            x_br, y_br = approx[3][0]
            # Locate points of the documents or object which you want to transform 
            width = 500
            height = 500
            pts1 = np.float32([[x_tl, y_tl], [x_bl, y_bl], [x_br, y_br], [x_tr, y_tr]]) 
            target_point = np.float32([[0, 0], [0, height], [width, height], [width, 0]])
            
            # Apply Perspective Transform Algorithm 
            matrix = cv2.getPerspectiveTransform(pts1, target_point) 
            result = cv2.warpPerspective(approx_image, matrix, (500, 600)) 
            # print(x_tr, y_tr)
            cv2.imshow('finnal',result)
        cv2.waitKey(1)


    def get_chessboard_test(self):
        ret, img = self.__capture_newest_image()
        if ret:
            self.new_idea(img)

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
        key = '8'
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
        
        elif key == '8':
            myrobotEye.get_chessboard_test()
            # layout = myrobotEye.get_stable_layout(app_config.robot_eye.layout_scanner.stable_depth)
            # time.sleep(0.1)
