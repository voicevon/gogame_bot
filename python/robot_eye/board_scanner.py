#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
import cv2
import rospy


import sys
sys.path.append('/home/xm/gitrepo/ros_marlin_bridge/app_global')
from color_print import CONST

from go_game_config import app_config, CvDebugger


class BoardScanner():

    def __init__(self):


        # self.__BLANK = app_config.game_rule.cell_color.blank
        # self.__BLACK = app_config.game_rule.cell_color.black
        # self.__WHITE = app_config.game_rule.cell_color.white

        self.__CROP_WIDTH = app_config.robot_eye.board_scanner.cropping.crop_width_on_x
        self.__CROP_HEIGHT = app_config.robot_eye.board_scanner.cropping.crop_height_on_y



        self.__FC_GREEN = CONST.print_color.fore.green
        self.__FC_YELLOW = CONST.print_color.fore.yellow
        self.__FC_RESET = CONST.print_color.control.reset


        '''
            HSV模型中颜色的参数分别是：色调（H），饱和度（S），明度（V）
            下面两个值是要识别的颜色范围
            红色：
            H：0--10 156-180
            S：43--255
            V：46--255
            黑色：
            H:0--180
            S:0--255
            V:0--46
            白色：
            H:0--180
            S:0--30
            V:221--255
            灰色：
            H：0--180
            S:0--43
            V:46--220
            蓝色：
            H：100--124
            S:43 -- 255
            V：46--255
            红色：
            H：0--10 156-180
            S：43--255
            V：46--255
            黄色：
            H：26--34
            S:43 -- 255
            V：46--255
        '''
        self.Min_BoardColor = numpy.array([0, 20, 0])  # 要识别棋盘的颜色的下限
        self.Max_BoardColor = numpy.array([180, 255, 200])  # 要识别棋盘的颜色的上限
        # self.Min_BlackColor = numpy.array([0, 0, 0])  # 要识别黑子颜色的下限
        # self.Max_BlackColor = numpy.array([180, 255, 80])  # 要识别黑子的颜色的上限
        # self.Min_WhiteColor = numpy.array([0, 0, 200])  # 要识别白子颜色的下限
        # self.Max_WhiteColor = numpy.array([180, 100, 255])  # 要识别白子的颜色的上限
        self.IsShowBoardGrid = True  # 是否显示棋子的理论位置
        self.IsShowBeginAndEndImg = False  # 是否显示开始结束标记图片
        self.BeginX = -85  # 起始位置X方向偏移距离220
        self.BeginY = 39  # 起始位置Y方向偏移距离-45
        self.BeginLenth = 30  # 开始区域取的大小
        self.IsShowBlackImg = False  # 是否显示识别黑子的图片
        self.IsShowWhiteImg = False  # 是否显示识别白子的图片

    def get_whole_area_of_chessboard_new_idea(self,img):
        # https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
        # https://www.geeksforgeeks.org/perspective-transformation-python-opencv/


        # detect edges using Canny
        img_target = img.copy()
        img_approx = img.copy()
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # canny = cv2.Canny(img, 149,150)
        canny = cv2.Canny(img_gray, 120,200)
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
        if target_rec is None:
            return 
        x1,y1,x2,y2 = target_rec
        bounding_rectangle = cv2.rectangle(img_target,(x1,y1),(x1+x2,y1+y2),(255,0,0),2)
        cv2.imshow('target',bounding_rectangle)

        approx_image = cv2.drawContours(img_approx, approx, -1, (255,0,0),22)
        # print('>>>>>>>>>>>>>>>>>>>>>>', approx)
        # print('----------------------------------------------------------')
        cv2.imshow('approx', approx_image)

        # tr = approx[1]
        # print(tr)
        # x,y = tr[0]   
        # print(x,y)
        
        # source = cv2.line(img, approx)
        result = None
        if len(approx) == 4:
            x_tr, y_tr = approx[0][0]
            x_tl, y_tl = approx[1][0]
            x_bl, y_bl = approx[2][0]
            x_br, y_br = approx[3][0]
            # Locate points of the documents or object which you want to transform 
            width = self.__CROP_WIDTH
            height = self.__CROP_HEIGHT
            pts1 = numpy.float32([[x_tl, y_tl], [x_bl, y_bl], [x_br, y_br], [x_tr, y_tr]]) 
            target_point = numpy.float32([[0, 0], [0, height], [width, height], [width, 0]])
            
            # Apply Perspective Transform Algorithm 
            matrix = cv2.getPerspectiveTransform(pts1, target_point) 
            result = cv2.warpPerspective(approx_image, matrix, (self.__CROP_WIDTH, self.__CROP_HEIGHT)) 
            # print(x_tr, y_tr)
            cv2.imshow('finnal',result)
        cv2.waitKey(1)
        if result is not None:
            singleQiPan = result[0:self.__CROP_HEIGHT, 0:self.__CROP_WIDTH]
            return singleQiPan


    def get_whole_area_of_chessboard(self, img):
        # 第二步，获取棋盘
        kernel_4 = numpy.ones((4, 4), numpy.uint8)  # 4x4的卷积核

        HSV = cv2.cvtColor(src=img, code=cv2.COLOR_BGR2HSV)
        '''
        HSV模型中颜色的参数分别是：色调（H），饱和度（S），明度（V）
        下面两个值是要识别的颜色范围
        红色：
        H：0--10 156-180
        S：43--255
        V：46--255
        黄色：
        H：26--34
        S:43 -- 255
        V：46--255
        '''
        Lower = self.Min_BoardColor  # 要识别颜色的下限
        Upper = self.Max_BoardColor  # 要识别的颜色的上限
        # mask是把HSV图片中在颜色范围内的区域变成白色，其他区域变成黑色
        mask = cv2.inRange(HSV, Lower, Upper)
        # cv2.imshow("img", Img)
        # cv2.imshow("mask", mask)
        # cv2.waitKey(0)
        # 下面是用卷积进行滤波
        dilation = cv2.dilate(mask, kernel_4, iterations=1)
        # cv2.imshow("dilation", dilation)
        # cv2.waitKey(0)
        # 将滤波后的图像变成二值图像放在binary中
        ret, binary = cv2.threshold(dilation, 127, 255, cv2.THRESH_BINARY)
        # 在binary中发现轮廓，轮廓按照面积从小到大排列
        # image, contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 找到最大的轮廓，理论上来说，就应该是棋盘轮廓。冒泡一个
        iMianJi = 0
        for i in range(0, len(contours)):  # 遍历所有的轮廓
            if iMianJi < cv2.contourArea(contours[i]):

                iMianJi = cv2.contourArea(contours[i])
                qipan = contours[i]

        # 判断最大面积，如果最大面积小于下限，说明红边被遮挡了，这时候是识别不出棋盘的
        # print(iMianJi)

        x, y, w, h = cv2.boundingRect(qipan)  # 将轮廓分解为识别对象的左上角坐标和宽、高
        # 在图像上画上矩形（图片、左上角坐标、右下角坐标、颜色、线条宽度）
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255,), 3)
        # # 给识别对象写上标号
        # font=cv2.FONT_HERSHEY_SIMPLEX
        # cv2.putText(img,str(1),(x-10,y+10), font, 1,(0,0,255),2)#加减10是调整字符位置
        # cv2.imshow('Img', img)
        # cv2.waitKey(0)
        # print("i mianji = {0}".format(iMianJi))
        if iMianJi < 170000:
            # return False, layout
            CvDebugger.show_debug_image('board_scanner warning:', img, 'Area is too small')
            return None
        # 因为是取的黄色棋盘，所以棋盘外面暂时没有偏移；下一步需要根据实际情况，对棋盘的进行偏移处理
        # 另外，这里没有考虑棋盘旋转的情况，默认的棋盘应该是正好卡在一个正方形里面的。这里考虑到变形，会有些许的调整。
        dst = self.Toushi(img,x,y,w,h,qipan)
        xNew = x + 0
        yNew = y + 0
        xEnd = x + self.__CROP_WIDTH
        yEnd = y + self.__CROP_HEIGHT
        # cv2.rectangle(Img,(xNew,yNew),(xEnd,yEnd),(0,255,),1)


        # 获取到了棋盘
        singleQiPan = dst[yNew:yEnd, xNew:xEnd]
        CvDebugger.show_debug_image('board_scaner', singleQiPan, 'Got it')
        return singleQiPan

    def __show_detection_line(self, img_board):
        dxBuChang = 22 
        dyBuChang = 22
        img_viewer = img_board.copy()
        for x in range(0,19):
            # vertical line along Y-axis
            xn = dxBuChang * x + dxBuChang / 2 + 5
            cv2.line(img_viewer,(xn,0),(xn,900),(0,255,0),1)
        for y in range(0,19):
            # horizontal line, along X-axis
            yn = dyBuChang * y + dyBuChang / 2 + 5          
            cv2.line(img_viewer,(0,yn),(900,yn),(0,255,0),1)
        cv2.imshow('board viewer',img_viewer)

        cv2.waitKey(1)

        # self.__detect_circles(img_board)

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
        pts1 = numpy.float32([pp1, pp2, pp3, pp4])
        pts2 = numpy.float32([[x, y],[x+430,y],[x+430,y+430],[x, y+430]])
        # print("pts1:{0}".format(pts1))
        # print("pts2:{0}".format(pts2))
        M = cv2.getPerspectiveTransform(pts1,pts2)
        dst = cv2.warpPerspective(img, M, (width, height))
        # cv2.imshow("dst", dst)
        return dst


if __name__ == "__main__":
    test = BoardScanner()