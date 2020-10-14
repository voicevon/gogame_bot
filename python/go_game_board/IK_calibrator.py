        

import sys
sys.path.append('/home/xm/gitrepo/ros_marlin_bridge/robot_arm')
from human_level_robot import HumanLevel_RobotArm

from robot_kinematic import Pose,Pose_FK


sys.path.append('/home/xm/gitrepo/ros_marlin_bridge/go_gameboard')
from chessboard_cell import ChessboardCell

sys.path.append('/home/xm/gitrepo/ros_marlin_bridge/app_global')
from color_print import CONST
from go_game_config import app_config


import rospy


class Runner():
    
    class ChessboardHelper():
            def __init__(self):
                self.layout = [([0] * 19) for i in range(19)]
                # below values are from manually calibrattion
                # t1 at top_left corner of XY-coordinator
                t1_x = -0.159  
                t1_y = 0.48
                # a19 at bottom_right corner of XY-coordinator
                a19_x = 0.156
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
                target_FK = Pose_FK()
                target_FK.x = cell.col_id * self.__cell_space_x + self.__chessboard_left
                target_FK.y = cell.row_id * self.__cell_space_y + self.__chessboard_bottom
                target_FK.z = 0.02
                target_FK.w = 0
                return target_FK

    def __init__(self):
        self.__chessboard_helper = self.ChessboardHelper()
        self.__robot = HumanLevel_RobotArm(app_config.robot_arm.name)
        self.__robot.bridge_soft_robot_connect_to_moveit()
        self.__robot.bridge_hard_robot_connect_to_marlin()
        self.__robot.bridge_hard_robot_home_all_joints()
        self.__robot.bridge_set_hard_robot_following(True)

    def __move_to_FK_Position(self,target_FK):
        '''
        unit of target_FK is meter. 
        '''
        target_FK.x *= 1000
        target_FK.y *= 1000
        target_FK.z *= 1000
        self.__robot.bridge_soft_robot_goto_FK_pose_unit_mm(target_FK)

    def move_row_by_row(self, start_cell_name='T1', step=1,is_upper_letter=True):
        cell = ChessboardCell()
        cell.from_name(start_cell_name)
        start_cell_id = cell.id
        for index in range(start_cell_id ,361, step):
            if index % 19 == 0:
                # change postion to new row
                cell.from_id(180)
                temp_FK = self.__chessboard_helper.get_interpolated_FK_from_cell(cell)
                self.__move_to_FK_Position(temp_FK)
            cell.from_id(index)
            print(cell.to_diction())
            target_FK = self.__chessboard_helper.get_interpolated_FK_from_cell(cell)
            if is_upper_letter:
                self.__robot.current_pose.name = cell.name.upper()
                target_FK.z = 0.001
            else:
                self.__robot.current_pose.name = cell.name.lower()
                target_FK.z = 0.098

            self.__move_to_FK_Position(target_FK)
            rospy.sleep(10)
            self.__robot.update_current_pose_to_diction()
            self.__robot.write_pose_diction_to_json_file()


    def __Deal_with_this_cell(self, cell):
        target_FK = self.__chessboard_helper.get_interpolated_FK_from_cell(cell)
        target_FK.z = 0.001
        self.__robot.current_pose.name = cell.name.upper()
        self.__move_to_FK_Position(target_FK)
        self.__robot.update_current_pose_to_diction()
        self.__robot.write_pose_diction_to_json_file()

    def create_four_corners(self):
        corners = [(0,0), (0,18), (18,0), (18,18)]
        for col,row in corners:
            cell = ChessboardCell()
            cell.from_col_row_id(col, row)
            self.__Deal_with_this_cell(cell)






    def move_four_corners(self,pause_second=5):
        target_cells = ['A1','A19','T1','T19']
        for this_cell in target_cells:
            cell = ChessboardCell()
            cell.from_name(this_cell)
            target_FK = self.__chessboard_helper.get_interpolated_FK_from_cell(cell)
            self.__move_to_FK_Position(target_FK)
            rospy.sleep(pause_second)


import click
if __name__ == "__main__":
    runner = Runner()
    print ('*************************************************************')
    print ('*  1.  create IK for Four corners                        *')
    print ('*  2.  show position of Four corners                        *')
    print ('*  3.  auto calibrate lower letter                          *')
    print ('*  4.  auto calibrate upper letter                          *')
    print ('*  5.  auto calibrate lower and upper letter                *')
    print ('*************************************************************')
        
    k = click.getchar()
    if k == '3':
        runner.move_row_by_row(start_cell_name='T1', step=1, is_upper_letter=False)
    elif k == '4':
        runner.move_row_by_row(start_cell_name='T1', step=1, is_upper_letter=True)
    elif k =='5':
        runner.move_row_by_row(start_cell_name='T1', step=1, is_upper_letter=True)
        runner.move_row_by_row(start_cell_name='T1', step=1, is_upper_letter=False)

    elif k == '1':
        runner.create_four_corners()
    elif k == '2':
        runner.move_four_corners(pause_second=10)
