
import cv2
import numpy

import sys

sys.path.append('/home/xm/gitrepo/ros_marlin_bridge/app_global')
from color_print import CONST

from go_game_config import app_config

class CellScanner():
    def __init__(self, board_mean):
        self.__board_mean = board_mean
        self.__ROWS = app_config.game_rule.board_size.row
        self.__COLS = app_config.game_rule.board_size.col
        self.__BLANK = app_config.game_rule.cell_color.blank
        self.__BLACK = app_config.game_rule.cell_color.black
        self.__WHITE = app_config.game_rule.cell_color.white

        self.__FC_YELLOW = CONST.print_color.fore.yellow
        self.__FC_RESET = CONST.print_color.control.reset
        
        # self.__INSPECT_COUNTER = go_game_inspecting_cell.counter


    def scan(self, cell_image, is_inspected):
        '''
        parameter: 
            cell_image must be size of 22x22
        return: 
            detected cell_color
        '''
        # detected_circles = self.__detect_circles(cell_image,show_processing_image=is_inspected)
        # cell_color = self.__BLANK

        # if detected_circles is None:
        #     if is_inspected:
        #         print('Inspected cell, no circles found!')
        #         cv2.imwrite(str(go_game_inspecting_cell.counter) +'.png',cell_image)
                # go_game_inspecting_cell.counter += 1
        # elif len(detected_circles) == 1:
            # detected one circle. 
            # height, width, depth = cell_image.shape
            # mask_circle = numpy.zeros((height, width), numpy.uint8)
            
            # for (x,y,r) in detected_circles[0]:
            #     cv2.circle(mask_circle, (x,y), radius=r, color=1, thickness=-1)
            #     masked_image = cv2.bitwise_and (cell_image, cell_image, mask=mask_circle)
            #     cv2.imshow('fffffffff',masked_image)
                # What color in this circle? black or white
        gray = cv2.cvtColor(cell_image, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray,5)
        average_brightness = numpy.mean(blur)
        cell_color = self.__BLACK
        if is_inspected:
            print('average_brightness = %d' %average_brightness)
            cv2.imshow('cell_image',cell_image)
        if average_brightness > 150:
            cell_color = self.__WHITE
        elif average_brightness > 80:
            cell_color = self.__BLANK
        # print(self.__PT_RESET + 'average_brightness= %d' %average_brightness)
        # if average_brightness > 30:
        #     cell_color = self.__WHITE
        # else:
        #     # if is_inspected: 
        #     print('detected cell_image,  circles=%d' %len(detected_circles))
        return cell_color

    def scan_black(self, cell_image, is_inspected):
        gray = cv2.cvtColor(cell_image, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray,7)
        ret, bin_image = cv2.threshold(blur, 50, 255, cv2.THRESH_BINARY_INV)


        cell_color = self.__BLANK
        count = cv2.countNonZero(bin_image)
        if count > 180:
            cell_color = self.__BLACK

        if is_inspected:
            cv2.imshow('blur_black', blur)
            cv2.imshow('bin_image', bin_image)
            print (count)
        return cell_color

        
    def scan_white(self, cell_image, is_inspected):
        '''
        return: 
            detected cell_color, only for White. because connected black cells have no circle
        '''
        detected_circles = self.__detect_circles(cell_image,show_processing_image=is_inspected)
        cell_color = self.__BLANK
        if detected_circles is None:
            if is_inspected:
                print('Inspected cell, no circles found!')
        elif len(detected_circles) == 1:
            # detected one circle. 
            height, width, depth = cell_image.shape
            mask_circle = numpy.zeros((height, width), numpy.uint8)
            
            for (x,y,r) in detected_circles[0]:
                cv2.circle(mask_circle, (x,y), radius=r, color=1, thickness=-1)
                masked_image = cv2.bitwise_and (cell_image, cell_image, mask=mask_circle)
                cv2.imshow('masked_image', masked_image)
                # What color in this circle? black or white
                average_brightness = numpy.mean(masked_image)
                # print(self.__FC_RESET + 'average_brightness= %d' %average_brightness)
                if average_brightness > 30:
                    cell_color = self.__WHITE
                    # print('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')
        else:
            if is_inspected: 
                print('detected cell_image,  circles=%d' %len(detected_circles))
        return cell_color
   
    def __detect_circles(self, cropped_img, show_processing_image=True):
        # detect circles
        gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray,7)
        canny = cv2.Canny(gray,100,200)
        circles = cv2.HoughCircles(blur, method=cv2.HOUGH_GRADIENT, dp=1, minDist= 1, 
                                    minRadius=8, maxRadius=15, param1=1, param2=20)

        if circles is None:
            if show_processing_image:
                cv2.imshow('nn center lines', cropped_img)
                cv2.imshow('nn gray', gray)
                cv2.imshow('nn blur', blur)
                cv2.imshow('nn canny', canny)
                cv2.waitKey(1)
        if circles is not None:
            detected_circles = numpy.uint16(numpy.around(circles))
            if show_processing_image:
                # draw circles
                img = cropped_img.copy()
                for (x,y,r) in detected_circles[0,:]:
                    # outer circle
                    cv2.circle(img,(x,y),r,(0,255,0),thickness=1)
                    # for showing the center of the circle, is a small 
                    cv2.circle(img,(x,y),3,(0,0,255),1)
                cv2.imshow('center lines',img)
                cv2.imshow('gray',gray)
                cv2.imshow('blur',blur)
                cv2.waitKey(1)
            return detected_circles
        return None



if __name__ == "__main__":
    test = CellScanner('test')