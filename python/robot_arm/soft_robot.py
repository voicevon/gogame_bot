#!/usr/bin/env python
# coding=utf-8

#  The exlaination is here:
#  http://docs.ros.org/kinetic/api/moveit_tutorials/html/doc/move_group_python_interface/move_group_python_interface_tutorial.html
import sys
import copy
import rospy
import logging
import geometry_msgs.msg
from std_msgs.msg import String

import moveit_commander
import moveit_msgs.msg
from moveit_commander.conversions import pose_to_list

from math import pi
import random
import threading
import time

from robot_kinematic import Pose

class Soft_robot:
    '''
    Actrually, a soft_robot is MoveIt client.
    The instance will control the moveit to do some action, like arm_movement and hand_actions
    '''
    def __init__(self):
        print('Moveit __init__() is begin')
        # self.__group_name = "arm"
        self.__gourp_names = ['arm1','arm2']
        # self.__gourp_names = ['arm2']
        print('Moveit __init() is finished')
        self.__log_level = 0 

    def connect_to_moveit(self):
        moveit_commander.roscpp_initialize(sys.argv)
        # rospy.init_node('move_group_python_interface_tutorial',
        #                 anonymous=True)
        self.__robot = moveit_commander.RobotCommander()
        self.__scene = moveit_commander.PlanningSceneInterface()

        # self.__robot_arm = moveit_commander.MoveGroupCommander(self.__group_name)
        self.__robot_arms = []
        for this_group in self.__gourp_names:
             this_arm = moveit_commander.MoveGroupCommander(this_group)
             self.__robot_arms.append(this_arm)

        self.__display_trajectory_publisher = rospy.Publisher('/move_group/display_planned_path',
                                                    moveit_msgs.msg.DisplayTrajectory,
                                                    queue_size=20)   

    # def go_joint(self):
    #     joint_goal = self.group.get_current_joint_values()
    #     joint_goal[0] = 1
    #     self.group.go(joint_goal, wait=True)
    
    def __new_threading_moveit_go(self,this_arm,pose_goal):
        this_arm.set_pose_target(pose_goal)
        this_arm.go()

    def goto_the_pose_uint_mm(self, target_FK):
        '''
        Robot arm will goto a position at (x,y,z) , unit is mm
        The target orientation is always face down.
        '''
        pose_goal = geometry_msgs.msg.Pose()
        
        # for Go_Scara
        pose_goal.position.x = 0.001 * target_FK.x  
        pose_goal.position.y = 0.001 * target_FK.y
        pose_goal.position.z = 0.001 * target_FK.z
        # self.__robot_arm.set_pose_target(pose_goal)
        # self.__robot_arm.go()  
        ts=[]   
        for this_arm in self.__robot_arms:  # if havn't connected to moveit, will cause exception
            # Single thread
            this_arm.set_pose_target(pose_goal)
            this_arm.go()

            # Multi threads to run arms movement parallelly.
            # t = threading.Thread(target=self.__new_threading_moveit_go,args=[this_arm, pose_goal])
            # t.start()
            # ts.append(t)

        for t in ts:
            t.join()
    # Methods with the same name in one class in python?
    # https://st  target_FK.y = 0.4ckoverflow.com/questions/5079609/methods-with-the-same-name-in-one-class-in-python
    # def goto_pose(self, pose_FK):
    #     self.__goto_pose_details(pose_FK['x'], pose_FK['y'], pose_FK['z'], pose_FK['w'])

    def show_current_pose(self):
        ccc = self.__robot_arms[0].get_current_pose('ll6')
        if self.__log_level == 5:
            print('current pose  ',ccc)

    def __goto_pose_details(self, x, y, z, w):
        '''
        Robot arm will goto a position at (x,y,z) , unit is mm
        The target orientation is always face down.
        '''
        # print('MoveIt_Client::goto_pose(), unit is mm',x,y,z)
        pose_goal = geometry_msgs.msg.Pose()
        # ccc = self.__robot_arm.get_current_pose()
        # print('current pose  ',ccc)
        pose_goal.orientation.x = 0
        pose_goal.orientation.y = w
        # positin unit is meter, input unit is mm
        pose_goal.position.x = 0.001 * x  
        pose_goal.position.y = 0.001 * y
        pose_goal.position.z = 0.001 * z

        # print('*****************************************')
        # print('pose_goal.position',pose_goal)
        # print('-------------------------------------')

        self.__robot_arm.set_pose_target(pose_goal)
        self.__robot_arm.go()
        # xxx = self.__robot_arm.get_current_pose("Link6")
        # print(xxx)


if __name__ == "__main__":
    test = Soft_robot()
    test.connect_to_moveit()