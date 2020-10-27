import cv2
import numpy

class MarkScanner():
    '''
    Will scan a special area where is a black circle.
    Once user want send a command to robot, Just put a black chess to a cell in scanner area.
    '''

    def __init__(self):
        # self.source_image = None
        # self.__lastest_mark_index = -1
        self.__stable_depth = 0
        
        # detected history
        self.__history = []
        self.__max_history_length = 2
        # make sure history has two items at least
        self.__history.append(-1)
        self.__history.append(-1)

        #below value is manualy measured.
        self.__scan_area_x_min = 0
        self.__scan_area_x_max = 90
        self.__scan_area_y_min = 30
        self.__scan_area_y_max = 250

        self.__min_mark_circle_center_y = 22
        self.__max_mark_circle_center_y = 190 
        self.__mark_circle_count = 5

        self.__mark_space = (self.__max_mark_circle_center_y - self.__min_mark_circle_center_y) / (self.__mark_circle_count - 1)

    
    def __append_to_history(self, mark_index):
        while len(self.__history) > self.__max_history_length: 
            # print('len=%d ,max=%d' %(len(self.__history),self.__max_history_length))
            del self.__history[0]
        self.__history.append(mark_index)

        # update stable_depth
        self.__stable_depth = 1
        for i in range(0, len(self.__history)):
            if self.__history[-1] == self.__history [i]:
                self.__stable_depth += 1
        # print(self.__history)


    def detect_mark(self, origin_image, history_length,show_processing_image=True):
        '''
        return A:
            -1,-1: not detected any circle
        return B:
            mark_index 
            stable_depth
        '''
        # crop source_image to proper area
        self.__max_history_length = history_length
        cropped_img = origin_image[self.__scan_area_y_min:self.__scan_area_y_max, self.__scan_area_x_min:self.__scan_area_x_max]  # [y1:y2, x1:x2] this is a numpy slicing
        if show_processing_image:
            cv2.imshow('cropped',cropped_img)
            cv2.waitKey(1)
        # detect circles
        circles = self.__detect_circles(cropped_img, show_processing_image)
        if circles is None:
            return -1,-1
        #----------------------------------------------------------------------------------
        # detected at least one circle, if more than one circle, do nothing.
        if len(circles) == 1:
            # Yes, got one circle!
            x,y,r = circles[0][0]
            b,g,r = cropped_img[y,x]
            if b + g + r < 100:
                # the circle is a black circle, not a white circle
                mark_index = int(1.0* ( y - self.__min_mark_circle_center_y) / self.__mark_space + 0.5)
                # Append to history
                self.__append_to_history(mark_index)

        return self.__history[-1], self.__stable_depth
    
    def __detect_circles(self, cropped_img, show_processing_image=True):
        # detect circles
        gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray,5)
        # cv2.imshow('gray',gray)
        cv2.imshow('blur',blur)
        circles = cv2.HoughCircles(gray, method=cv2.HOUGH_GRADIENT, dp=1, minDist= 4, 
                                    minRadius=10, maxRadius=20, param1=50, param2=30)

        if circles is not None:
            detected_circles = numpy.uint16(numpy.around(circles))
            if show_processing_image:
                # draw circles
                img = cropped_img.copy()
                for (x,y,r) in detected_circles[0,:]:
                    # outer circle
                    cv2.circle(img,(x,y),r,(0,255,0),3)
                    # for showing the center of the circle, is a small 
                    cv2.circle(img,(x,y),r,(0,255,255),3)
                # draw mark_line                    
                for i in range(5):
                    y = self.__min_mark_circle_center_y + i * self.__mark_space
                    cv2.line(img,(0,y),(200,y),color=(0,255,0),thickness=2)
                cv2.imshow('center lines',img)
                cv2.waitKey(1)
            return detected_circles
        return None



if __name__ == "__main__":
    test = MarkScanner()
