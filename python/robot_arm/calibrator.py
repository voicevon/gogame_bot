# sudo chmod 666 /dev/ttyUSB0

# https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/

from robot_kinematic import Pose_IK, Pose
from human_level_robot import HumanLevel_RobotArm
import sys
sys.path.append('/home/xm/gitrepo/ros_marlin_bridge/go_game_board')
from chessboard_cell import ChessboardCell

sys.path.append('/home/xm/gitrepo/ros_marlin_bridge/app_global')
from go_game_config import app_config

import rospy
import json
import click
import threading
from sensor_msgs.msg import JointState

class Calibrator():
    
    def __init__(self, connect_to_hard_robot):
        self.robot = HumanLevel_RobotArm(app_config.robot_arm.name)
        if connect_to_hard_robot:
            self.robot.bridge_hard_robot_connect_to_marlin()
            self.robot.bridge_hard_robot_home_all_joints()
        self.robot.bridge_soft_robot_connect_to_moveit()

        self.__adjust_distance = 5  # unit is mm
        self.__pose_name_is_upper = False

    def __show_menu_adjust_current_pose(self):
        pose_name = self.robot.current_pose.name
        x = round(self.robot.current_pose.FK.x, 1)
        y = round(self.robot.current_pose.FK.y, 1)
        z = round(self.robot.current_pose.FK.z, 1)
        print('')
        print(" ----------------------------------------------------------------")
        print("| Adjusting Pose: %s: (x=%s, y=%s, z=%s)      " %(pose_name, x, y, z))
        print("|                                                                 |")
        print("|              up               PgUp        -                     |")
        print("|        left down right        PgDn        +                     |")
        print("|                                                                 |") 
        print("|        [1..0] to adjust distance. Current distance = %s mm      |" %self.__adjust_distance)
        print("|        W)rite, U)pper/lower Esc = Return                        |")
        print("|        Space to pick up/place down                              |")
        print(" -----------------------------------------------------------------")   

    def __adjust_current_pose(self):
        '''
        1. Get adjust command from keyboard
        2. Execute adjustment
        '''
        __printable = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
        __dict_adjust_distance = {'1':1, '2':2, '3':3, '4':5, '5':7, 
                          '6':10, '7':20, '8':30, '9':50, '0':100}
        __dict_arrow = {'\x1b[5~':'UP',  '\x1b[6~':'DOWN', 
                       '\x1b[A':'FRONT', '\x1b[B':'BACK', 
                       '\x1b[D':'LEFT',  '\x1b[C':'RIGHT',
                       '-':'MINUS','+':'PLUS'
                       }
        self.robot.hard_robot_follow_FK_joint5()
        while True:
            self.__show_menu_adjust_current_pose()
            key = click.getchar()

            if key in __dict_adjust_distance:
                self.__adjust_distance = __dict_adjust_distance[key]

            elif key in __dict_arrow:
                 self.robot.adjust_FK_step(__dict_arrow[key], self.__adjust_distance)
            elif key == ' ':
                self.robot.eef_pickup_placedown()

            # elif key in dict_sence:
            #     return dict_sence[key]

            elif key == '\x1b':   
                #Escape
                return None

            elif key == 'w':   
                self.robot.update_current_pose_to_diction()
                self.robot.write_pose_diction_to_json_file()
                return None

            elif key == 'u':  
                pose_name = self.robot.current_pose.name
                self.__pose_name_is_upper = not self.__pose_name_is_upper
                if self.__pose_name_is_upper:
                    pose_name = pose_name.upper()
                else:
                    pose_name = pose_name.lower()
                return pose_name
            else:
                click.echo('You pressed: "' + ''.join([ '\\'+hex(ord(i))[1:] if i not in __printable else i for i in key ]) +'"' )

    def __get_pose_name(self, pre_defined_pose_name):
        hot_key_diction = {'v':'VIEW','w':'warehouse','W':'WAREHOUSE','t':'trash','T':'TRASH'}

        if pre_defined_pose_name == None:
            # pose_name should come from user input
            self.__show_menu_main()
            self.__pose_name_is_upper = False
            input_name = raw_input('Input a cell name like "a1"  ')
            if input_name in hot_key_diction:
                pose_name = hot_key_diction[input_name]
            else:
                pose_name = input_name
        else:
            # pose_name is come from adjustment. 
            # shoud be a name of chess board cell . like 'a1,B2,t19,T18...'
            pose_name = pre_defined_pose_name

        # if pre_defined_pose_name in {'view','trash','warehouse'}:
        #     # Only upper is avaliable
        #     pose_name = pre_defined_pose_name.upper()

        return pose_name

    def __show_menu_main(self):
            print("******************************************************************")
            print("*   Testing Human_level_robot, comannds are:                     *")
            print("*                                                                * ")
            print("*   HOME, ZERO, CR1,CR2,CR3,CR5 ......... FK only pose           *")
            print("*             A1   K1   T1                                       *")
            print("*             A10  K10  T10                                      *")
            print("*             A19  K19  T19 .............. Cell Pose             *")
            print("*   V)IEW, t,T)RASH, w,W)AREHOUSE   .... Sence Pose            *")
            print("******************************************************************")

    def main(self):
        pose_IK_only_diction = {'HOME','ZERO','CR1','CR2','CR3','CR5'}
        predefined_pose_name = None
        while True:
            # try to get pose_name. might inforce to upper(), or lower()
            pose_name = self.__get_pose_name(predefined_pose_name)
            if pose_name.upper() in pose_IK_only_diction:
                self.robot.try_IK_only_pose(pose_name)
                self.robot.current_pose.name = pose_name
                predefined_pose_name = None
            else:
                # pose_name is FK doable. because this pose_name is in the pose_dictionary
                if self.robot.this_pose_is_in_diction(pose_name):
                    target_pose = self.robot.get_target_pose_by_name(pose_name)
                else:
                    target_pose = self.robot.current_pose.clone(pose_name)
                self.robot.goto_here(target_pose)
                predefined_pose_name = self.__adjust_current_pose()


class Runner():

    def __init__(self, hard_robot_online):
        self.__robot = Human_level_robot('goscara')
        if hard_robot_online:
            self.__robot.bridge_hard_robot_connect_to_marlin()
            self.__robot.bridge_hard_robot_home_all_joints()
        self.__robot.bridge_soft_robot_connect_to_moveit()
        self.__last_pressed_key = ''
        self.__keyboard = threading.Thread(target=self.keyboard)
        self.__keyboard.start()

    def __get_cell_name(self, row_index, col_index):
        '''
        row_index = [1..19]
        col_index = [1..19]
        '''
        row_names = 'ABCDEFGHJKLMNOPQRS'
        row_letter = row_names[row_index-1:row_index]
        return row_letter + str(col_index)

    def menffei_runner(self):
        '''
        v -> w -> W -> pickup -> Cell(a1) -> A1 -> place -> a1 -> v
        v -> a1 -> A1 -> pickup -> a1 -> T -> place
        '''
        self.__robot.eye_open('origin')
        # self.__robot.eye_open('candy')

        for row in range(1,19):
            for col in range(1,20):
                cell_name = self.__get_cell_name(row, col) 
                print(cell_name)
                self.__robot.action_pickup_chess_from_warehouse()

                self.__robot.action_place_chess_to_a_cell(cell_name)

                self.__robot.action_pickup_chess_from_a_cell(cell_name)

                self.__robot.action_place_chess_to_trash_bin()
                print('Press any key, Esc to zero')
                key = click.getchar()
                if key == '\x1b':   
                    #Escape
                    zero = self.__robot.get_target_pose_by_name('ZERO')
                    self.__robot.goto_here(zero)
                    print('You can shout down the power now.')
                    key = click.getchar()


    def keyboard(self):
        '''
        Should start a new thread.
        '''
        while True:
            k = click.getchar()
            self.__last_pressed_key = k
            print ('Key is pressed by another threading')

    def test_row_by_row(self,start_cell_name):
        self.__robot.eye_open('origin')
        first_cell = ChessboardCell()
        first_cell.from_name(start_cell_name)
        second_cell = ChessboardCell()
        # pickup from warehouse, the first one
        self.__robot.action_pickup_chess_from_warehouse()
        self.__robot.action_place_chess_to_a_cell(first_cell.name)

        # pickup from warehouse, the second one
        self.__robot.action_pickup_chess_from_warehouse()
        second_cell.from_id(first_cell.id + 1)
        self.__robot.action_place_chess_to_a_cell(second_cell.name)
        

        for i in range(first_cell.row_id * 19 ,361):
            this_cell = ChessboardCell()
            this_cell.from_id(i)
            next_cell= ChessboardCell()
            next_cell.from_id(i+2)
            print('******************************* %s' %this_cell.name)
            print('******************************* %s' %next_cell.name)
            self.__robot.action_pickup_chess_from_a_cell(this_cell.name)
            self.__robot.action_place_chess_to_a_cell(next_cell.name)

            if self.__last_pressed_key == '\x1b':  #Esc
                self.__robot.eef_sleep()
                zero = self.__robot.get_target_pose_by_name('ZERO')
                self.__robot.goto_here(zero)
                return

    def test_col_by_col(self,start_col):
            self.__robot.eye_open('origin')
            self.__robot.action_pickup_chess_from_warehouse()
            self.__robot.action_place_chess_to_a_cell('A' + str(start_col))
            self.__robot.action_pickup_chess_from_warehouse()
            self.__robot.action_place_chess_to_a_cell('B' + str(start_col))
            

            for iCol in range(0,19):
                for iRow in range(start_col,19):
                    this_cell = ChessboardCell()
                    this_cell.from_id(iRow * 19 + iCol)
                    next_cell = ChessboardCell()
                    next_cell.from_id(iRow * 19  + iCol)
                    print('******************************* %s' %this_cell.name)
                    print('******************************* %s' %next_cell.name)
                    self.__robot.action_pickup_chess_from_a_cell(this_cell.name)
                    self.__robot.action_place_chess_to_a_cell(next_cell.name)

                    if self.__last_pressed_key == '\x1b':  #Esc
                        self.__robot.eef_sleep()
                        zero = self.__robot.get_target_pose_by_name('ZERO')
                        self.__robot.goto_here(zero)
                        return

    def test_pickup_from_warehouse(self,auto_pause):
            self.__robot.eye_open('origin')
            # self.__robot.eye_open('candy')

            for i in range(0,360):
                self.__robot.action_pickup_chess_from_warehouse()
                this_cell = ChessboardCell()
                this_cell.from_id(i)
                self.__robot.action_place_chess_to_a_cell(this_cell.name)

            if auto_pause:
                key = click.getchar()
                if key == '\x1b':   
                    #Escape
                    zero = self.__robot.get_target_pose_by_name('ZERO')
                    self.__robot.goto_here(zero)
                    print('You can shout down the power now.')
                    key = click.getchar()

    def test_place_to_trash(self,auto_pause):
            # self.__robot.eye_open('origin')
            # self.__robot.eye_open('candy')

            for i in range(0,360):
                # self.__robot.action_pickup_chess_from_warehouse()
                this_cell = ChessboardCell()
                this_cell.from_id(i)
                self.__robot.action_pickup_chess_from_a_cell(this_cell.name)
                self.__robot.action_place_chess_to_trash_bin(True)

            if auto_pause:
                key = click.getchar()
                if key == '\x1b':   
                    #Escape
                    zero = self.__robot.get_target_pose_by_name('ZERO')
                    self.__robot.goto_here(zero)
                    print('You can shout down the power now.')
                    key = click.getchar()
    def xingfaming_demo(self):
        # move to Q4
        # move down ...
        self.__robot.action_pickup_chess_from_a_cell('Q4')
        self.__robot.action_place_chess_to_trash_bin()

        #
        self.__robot.action_pickup_chess_from_warehouse()
        self.__robot.action_place_chess_to_a_cell('Q4')

        #
        target_pose  =  self.__robot.get_target_pose_by_name('VIEW')
        self.__robot.goto_here(target_pose)


if __name__ == "__main__":
    print ('*************************************************************')
    print ('*  1.  Calibrator                                           *')
    print ('*  2.  Test Row_by_row                                      *')
    print ('*  3.  Test Col_by_col                                      *')
    print ('*  4.  pickup from warehouse                                *')
    print ('*  5.  place to trash                                       *')
    print ('*************************************************************')
    k = click.getchar()
    if k == '1':
        tester1 = Calibrator(True)
        tester1.main()

    elif k == '2':
        tester2 = Runner(True)
        tester2.test_row_by_row('A1')

    elif k == '3':
        tester2 = Runner(True)
        tester2.test_col_by_col(1)

    elif k == '4':
        tester2 = Runner(True)
        tester2.test_pickup_from_warehouse(False)

    elif k == '5':
        tester2 = Runner(True)
        tester2.test_place_to_trash(False)
   