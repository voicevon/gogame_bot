#! /usr/bin/env python
# -*- coding: utf-8 -*-


# sudo chmod 666 /dev/ttyUSB0

import logging
import sys
sys.path.append("../")

from app_global.color_print import CONST   # do not use  from app_global.color_print,  don't know why! 
from app_global.gogame_config import app_config

from robot_arm.helper import Robot_pose_helper
from robot_arm.robot_kinematic import Pose,Pose_FK

if app_config.robot_arm.type == 'FAZE4':
    from robot_arm.hard_robot_faze4 import Hard_robot_Faze4
    
if app_config.robot_arm.type =='GO_SCARA':
    from robot_arm.hard_robot_go_scara import Hard_robot_GoScara

if app_config.host_os == 'ubuntu_gui':
    import rospy 
    from std_msgs.msg import String
    from sensor_msgs.msg import JointState
    from robot_arm.soft_robot import Soft_robot

class HumanLevel_RobotArm:
    '''
    This is an abstract robot.
    It is a  thing that Understood 3 types of commands
        1. How to play go game on chessboard. 
        2. Some position is out of the chessboard, like
            Home, trash, warehouse,viewer point
        3. Some actions,like
            up(5mm),dn(5mm)
    This robot has two robot instance: soft_robot and hard robot
        soft_robot: actrually is MoveIt_client.
            Will implement IK.
        hard_robot: actrually is Faze4_host.
            Hard_robot doesn't process IK.
            Saying hard_robot/firmware doesn't know what is IK. Accept joint_angle/linear position directly.
    '''
    def __init__(self, hard_robot_type):
        '''
        soft_robot will be always online.
        hard_robot can be online , or offline(for debuging software convenience )
        '''
        self.__FC_YELLOW = CONST.print_color.fore.yellow
        self.__FC_RED = CONST.print_color.fore.red
        self.__FC_RESET = CONST.print_color.control.reset
        # self.__robot_eye = RobotEye()
        # self.__robot_eye.start_show('origin')
        self.__robot_type_name = hard_robot_type

        if hard_robot_type.upper() == 'FAZE4':
           self.__hard_robot = Hard_robot_Faze4()
        elif hard_robot_type.upper() == 'GO_SCARA':
            self.__hard_robot = Hard_robot_GoScara()
            # print('Human_level_robot:: Created instance Go_Scara, named self.__hard_robot')
        else:
            logging.error(self.__FC_RED + ' Wrong arg of hard_robot_type %s' %hard_robot_type + self.__FC_RESET)

        if app_config.robot_arm.enable_moveit:
            self.__soft_robot = Soft_robot()
            rospy.init_node(self.__robot_type_name)

        self.__hard_robot_is_following = False  # to avoid repeated subscription
        # The host will not subsribe message from MoveIt, in this solution
        self.__pose_helper = Robot_pose_helper()
        self.current_pose = Pose()

        self.__at_picked_up = False
        self.__log_level = 0

    def bridge_hard_robot_connect_to_marlin(self):
        self.__hard_robot.connect_to_marlin()

    def bridge_hard_robot_home_all_joints(self):
        self.__hard_robot.home_all_joints()

    def bridge_soft_robot_connect_to_moveit(self):
        if app_config.robot_arm.enable_moveit:
            self.__soft_robot.connect_to_moveit()

    def this_pose_is_in_diction(self,pose_name):
        if pose_name in self.__pose_helper.pose_diction:
            return True
        return False
    def bridge_set_hard_robot_following(self, yes_enable_it):
        self.__set_hard_robot_folllowing(yes_enable_it)

    def __set_hard_robot_folllowing(self, yes_enable_it):
        '''
        RELEASE:     hard_robot DO NOT follow MoveIt
        CALIBRATION: hard_robot DO follow MoveIt 
        '''
        if yes_enable_it and (self.__hard_robot_is_following == False):
            # ROS topic Subscriber 
            self.sub_handler = rospy.Subscriber('joint_states',JointState,self.__hard_robot.Convert_to_gcode_Send)
            print('********************************** start follow FK')
        if (yes_enable_it == False) and self.__hard_robot_is_following:
            # Unsubsribe 'joint_states'
            # https://answers.ros.org/question/46613/rospy-how-do-you-unsubscribe-to-a-topic-from-within-the-callback/
            self.sub_handler.unregister()
            print('*********************************** stop follow FK')

        self.__hard_robot_is_following = yes_enable_it

    def update_current_pose_to_diction(self):
        dict_IK = self.__hard_robot.current_pose_IK.to_diction()
        dict_FK = self.current_pose.FK.to_diction()

        pose_name = self.current_pose.name
        # self.__pose_helper.pose_diction[pose_name]['IK'] = dict_IK
        # self.__pose_helper.pose_diction[pose_name]['FK'] = dict_FK
        self.__pose_helper.pose_diction[pose_name] = {'IK':dict_IK,'FK':dict_FK}
        print('[Info]: Updated %s to pose_diction!  IK=%s, FK=%s' %(pose_name,dict_IK,dict_FK))

    def write_pose_diction_to_json_file(self):
        self.__pose_helper.write_pose_diction_to_json_file()
        print('[Info]:  Writen pose_diction to file')

    def try_IK_only_pose(self,pose_name):
        self.__set_hard_robot_folllowing(False)
        __pose_name = pose_name.upper()
        if __pose_name == "HOME":
            # 'HOME' is special. pose_diction can't help
            self.__hard_robot.home_all_joints()
        else:
            # 'ZERO','CR1', 'CR2', 'CR3', 'CR5'
            IK_dict = self.__pose_helper.pose_diction[__pose_name]['IK']
            self.__hard_robot.set_joints_angle_in_degree(IK_dict)
        return True

    def hard_robot_follow_FK_joint5(self):
        self.__hard_robot.jonit5_is_following_FK = True

    def bridge_soft_robot_goto_FK_pose_unit_mm(self, target_FK):
        self.__soft_robot.goto_the_pose_uint_mm(target_FK)

    def adjust_FK_step(self, command, adjust_distance):
        '''
        pose_name: {A1..T19,TRASH,VIEW,HOUSE}
        command: {'UP','DOWN','LEFT','RIGHT','FRONT','BACK'}
        distance: unit is mm
        will update self.current_pose.FK and return it.
        '''
        print ('Execute adjustment for : ' + command )
        # command_upper = command.upper()
        # if command_upper not in self.pose_helper.pose_FK_adjust_command_diction:
        #     return False

        target_FK = self.current_pose.FK
        if command == 'UP':
            target_FK.z += adjust_distance
        elif command == "DOWN":
            target_FK.z -= adjust_distance
        elif command == "LEFT":
            target_FK.x -= adjust_distance
        elif command == "RIGHT":
            target_FK.x += adjust_distance
        elif command == "FRONT":
            target_FK.y += adjust_distance
        elif command == "BACK":
            target_FK.y -= adjust_distance
        elif command == 'MINUS':
            self.__hard_robot.joint5_angle_minus()
        elif command == 'PLUS':
            self.__hard_robot.joint5_angle_plus()

        self.__set_hard_robot_folllowing(True)
        self.__soft_robot.goto_the_pose_uint_mm(target_FK)

        dict_FK = target_FK.to_diction()
        self.current_pose.FK.from_diction(dict_FK) 
        return dict_FK

    def get_target_pose_by_name(self, pose_name):
        '''

        '''
        target_pose = self.__pose_helper.from_pose_diction(pose_name) 
        if target_pose == None:
            # not found in pose_diction,
            target_pose = Pose()
            target_pose.name = pose_name
        return target_pose

    def get_target_pose_by_FK_IK(self, pose_name, fk, ik):
        target_pose = Pose()
        target_pose.name = pose_name
        target_pose.FK.from_diction(fk)
        target_pose.IK.from_diction(ik)
        return target_pose

    def goto_here(self, target_pose):
        '''
        Both hard_robot and soft_robot will goto the position of pose_name.
        the pose_name must be avaliable in pose_diction 
        '''
        if self.__log_level > 1:
            print('[Info:][Human_level_robot.goto_here()] Robot is moving to destination...')
        # self.__hard_robot.set_joints_angle_in_degree(target_pose.IK.to_diction())

        self.__set_hard_robot_folllowing(False)
        IK_dict = target_pose.IK.to_diction()
        self.__hard_robot.set_joints_angle_in_degree(IK_dict)
        if app_config.robot_arm.enable_moveit:
            self.__soft_robot.goto_the_pose_uint_mm(target_pose.FK)

        self.current_pose.name = target_pose.name
        self.current_pose.FK.from_diction(target_pose.FK.to_diction())
        self.current_pose.IK.from_diction(IK_dict)

    def __eef_pick_up(self):
        self.__hard_robot.eef_pick_up()

    def __eef_place_down(self):
        self.__hard_robot.eef_place_down()

    def eef_pickup_placedown(self):
        if self.__at_picked_up:
            self.__eef_place_down()
        else:
            self.__eef_pick_up()
        self.__at_picked_up = not self.__at_picked_up

    def eef_sleep(self):
        self.__hard_robot.eef_sleep()

    def action_pickup_chess_from_a_cell(self, cell_name='k10'):
        print ('[Info]: action_pickup_chess_from_a_cell  %s' %cell_name)
        # pose = self.get_target_pose_by_name('VIEW')
        # self.goto_here(pose)
        pose = self.get_target_pose_by_name(cell_name.lower())
        self.goto_here(pose)
        pose = self.get_target_pose_by_name(cell_name.upper())
        self.goto_here(pose)
        self.__eef_pick_up()
        pose = self.get_target_pose_by_name(cell_name.lower())
        self.goto_here(pose)

    def action_pickup_chess_from_warehouse(self):
        print('[Info]: Action_pickup_chess_from_warehouse')
        pose_name_list_a = ['warehouse','WAREHOUSE']
        for pose_name in pose_name_list_a:
            pose = self.get_target_pose_by_name(pose_name)
            self.goto_here(pose)
        self.__eef_pick_up()
        # lift up gripper
        pose = self.get_target_pose_by_name('warehouse')
        self.goto_here(pose)

    def action_place_chess_to_trash_bin(self, park_to_view_point=True):
        print('[Info]: Action_place_chess_to_trash_bin')

        pose = self.get_target_pose_by_name('TRASH')
        self.goto_here(pose)
        self.__eef_place_down() 
        # lift up gripper
        pose = self.get_target_pose_by_name('trash')    # this is a delaying for eef_place_down()  
        self.goto_here(pose)
        self.eef_sleep()

        if park_to_view_point:
            pose = self.get_target_pose_by_name('VIEW')
            self.goto_here(pose)

    def action_place_chess_to_a_cell(self, cell_name='k10', auto_park=True):
        print('[Info]: action_place_chess_to_a_cell %s' %cell_name)
        # pose = self.get_target_pose_by_name('VIEW')
        # self.goto_here(pose)
        pose = self.get_target_pose_by_name(cell_name.lower())
        self.goto_here(pose)
        pose = self.get_target_pose_by_name(cell_name.upper())
        self.goto_here(pose)
        self.__eef_place_down()
        pose = self.get_target_pose_by_name(cell_name.lower())
        self.goto_here(pose)
        self.eef_sleep()
        if auto_park:
            pose = self.get_target_pose_by_name('VIEW')
            self.goto_here(pose)
            


if __name__ == '__main__':
    my_robot = HumanLevel_RobotArm(app_config.robot_arm.name)
    # my_robot.bridge_hard_robot_connect_to_marlin()
    # my_robot.bridge_hard_robot_home_all_joints()
    # my_robot.bridge_soft_robot_connect_to_moveit()
