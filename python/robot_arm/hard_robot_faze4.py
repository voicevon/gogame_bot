from hard_robot import Hard_robot,HARD_ROBOT_ONLINE_LEVEL
import rospy 
from sensor_msgs.msg import JointState

class Hard_robot_Faze4(Hard_robot):

    def joint5_angle_minus(self):
        self.current_pose_IK.j5_angle_in_degree -= 1
        self.jonit5_is_following_FK = False
        self.set_joints_angle_in_degree(self.current_pose_IK.to_diction())

    def joint5_angle_plus(self):
        self.current_pose_IK.j5_angle_in_degree += 1
        self.jonit5_is_following_FK = False
        self.set_joints_angle_in_degree(self.current_pose_IK.to_diction())
    def Test31_home_y(self,home_z_first, pause_second=0,target_position=0):
        if home_z_first:
            self._my_serial.SendCommandCode('G28 Z')

        # while True:
        self._my_serial.SendCommandCode('G28 Y')
        rospy.sleep(pause_second)
        self._my_serial.SendCommandCode('G1 Y' + str(target_position))
        rospy.sleep(pause_second)

    def Test32_home_z(self,pause_second=0,target_position=0):
        # self._my_serial.SendCommandCode('G28 Y')
        # rospy.sleep(pause_second)
        # self._my_serial.SendCommandCode('G1 Y0')
        # rospy.sleep(pause_second)

        # while True:
        self._my_serial.SendCommandCode('G28 Z')
        rospy.sleep(pause_second)
        self._my_serial.SendCommandCode('G1 Z' + str(target_position))
        rospy.sleep(pause_second)

    def Test33_home_x(self,home_yz_first,pause_second=0,target_position=0):
        if home_yz_first:
            self._my_serial.SendCommandCode('G28 Y')
            rospy.sleep(pause_second)
            self._my_serial.SendCommandCode('G1 Y10 ')
            rospy.sleep(pause_second)
            self._my_serial.SendCommandCode('G28 Z')
            rospy.sleep(pause_second)
            self._my_serial.SendCommandCode('G1 Z30 ')
            rospy.sleep(pause_second)

        # while True:
        self._my_serial.SendCommandCode('G28 X')
        rospy.sleep(pause_second)
        self._my_serial.SendCommandCode('G1 X' + str(target_position))
        rospy.sleep(pause_second)

    def Test34_Home_e(self,pause_second=0,target_position=0):
        # while True:
        rospy.sleep(pause_second)
        self._my_serial.SendCommandCode('G83')
        # self._my_serial.SendCommandCode('G92 E-90')
        # rospy.sleep(pause_second)
        self._my_serial.SendCommandCode('G1 E' + str(target_position)) 
        # rospy.sleep(pause_second)    
    
    def Home_e(self,pause_second=0,target_position=0):
        # while True:
        rospy.sleep(pause_second)
        self._my_serial.SendCommandCode('G83')
        # self._my_serial.SendCommandCode('G92 E-90')
        # rospy.sleep(pause_second)
        self._my_serial.SendCommandCode('G1 E' + str(target_position)) 
        # rospy.sleep(pause_second)

    def home_all_joints(self):
        '''
        Home all joints. 
        by following a certain sequence.
        Implicated with sending gCode to Marlin.
        Because Homing is a special position for each joint
        So that after homing, move all joints to position zero. 
        The arm will be absolute a vertical line shape.
        ----------------------------------
        Please pay attention:
        Must invoke Init_Marlin before sending any gCode.
        Otherwise, some gcodes will not be executed.
        '''
        if self.mode == HARD_ROBOT_ONLINE_LEVEL.OFF_LINE:
            print('[Warning]: Robot is offline ')
            return

        self._my_serial.SendCommandCode('G83')
        self._my_serial.SendCommandCode('G28 X')
        self._my_serial.SendCommandCode('G28 Z')
        self._my_serial.SendCommandCode('G28 Y')
        self._my_serial.SendCommandCode('G1 X0 Y0 Z0 E0') 
        self.mode = HARD_ROBOT_ONLINE_LEVEL.HOMED 

    def set_joints_angle_in_degree(self, IK_dict):
        self.current_pose_IK.from_diction(IK_dict)
        gcode = 'G1 X' + str(IK_dict['j1']) + ' Y' + str(IK_dict['j2']) + ' Z' + str(IK_dict['j3']) + ' E' + str(IK_dict['j5'])
        print(gcode)

        if self.mode == HARD_ROBOT_ONLINE_LEVEL.OFF_LINE:
            print ('[Warning]: hard_robot is offline.')
            return 
        self._my_serial.SendCommandCode(gcode)
        
    def Convert_to_gcode_Send(self,joint_states):

        print(joint_states)
        '''
        Convert ROS message::joint_states to gcode G1.
        Then, send out gCode like "G1 X11 Y22 Z33 E44" 

        '''
        to_degree = 180.0 / 3.14159
        angle = [1,2,3,4,5,6]
        angle[0] = joint_states.position[0] * to_degree
        angle[1] = joint_states.position[1] * to_degree
        angle[2] = joint_states.position[2] * to_degree
        angle[3] = joint_states.position[3] * to_degree
        if self.jonit5_is_following_FK:
            angle[4] = joint_states.position[4] * to_degree
        else:
            angle[4] = self.current_pose_IK.j5_angle_in_degree
        angle[5] = joint_states.position[5] * to_degree

        # If all angles has no updating, just return, 
        # don't send any G1 code to Marlin 
        if self.current_pose_IK.j1_angle_in_degree == angle[0]:
            if self.current_pose_IK.j2_angle_in_degree == angle[1]:
                if self.current_pose_IK.j3_angle_in_degree == angle[2]:
                    # if(self.last_angle[3] == angle[3]):
                    if self.current_pose_IK.j5_angle_in_degree == angle[4]:
                            # if(self.last_angle[5] == angle[5]):
                        return

                                
        self.current_pose_IK.j1_angle_in_degree = angle[0]
        self.current_pose_IK.j2_angle_in_degree = angle[1]
        self.current_pose_IK.j3_angle_in_degree = angle[2]
        # self.last_angle[3] = angle[3]
        self.current_pose_IK.j5_angle_in_degree = angle[4]
        # self.last_angle[6] = angle[5]

        gcode = 'G1 X' + str(round(angle[0],2)) + ' Y' + str(round(angle[1],2)) + ' Z' + str(round(angle[2],2)) + ' E' + str(round(angle[4],2))
        if self.mode == HARD_ROBOT_ONLINE_LEVEL.OFF_LINE:
            print('[Warning: Hard_Robot.Convert_to_gcode_Send(). mode == OFF_LINE')
            return 
        
        self._my_serial.SendCommandCode(gcode)

if __name__ == "__main__":
    # mode = 'calibration'    # To calibrate home position. Those are a group of const numbers for each joint.
    # mode = 'offline'        # Do not connect to Marlin, The messages from MoveIt will be ignored.
    # mode = 'release'
    mode = 'fan'
    
    myFaze4 = Hard_robot_Faze4()
    myFaze4.connect_to_marlin()
    if mode == 'calibration':
        '''
        '''
        # myFaze4.Test33_home_x(False, pause_second=0, target_position=0)
        # myFaze4.Test31_home_y(True, pause_second=15, target_position=0)
        # myFaze4.Test32_home_z(pause_second=0, target_position=0)
        # myFaze4.Test34_Home_e(pause_second=10,target_position=0)
        # myFaze4.Home()

        while True: 
            myFaze4.Test2_home_sensor()
            # pass  
            # myFaze4.Home()
            # myFaze4._my_serial.SendCommandCode('G1 X0 Y0 Z0 E45')
            # rospy.sleep(5)     
            # myFaze4._my_serial.SendCommandCode('G1 E0')
            # rospy.sleep(5)
            # myFaze4._my_serial.SendCommandCode('G1 E30')
            # rospy.sleep(5)
            # myFaze4._my_serial.SendCommandCode('G1 E-45')
            # rospy.sleep(5)

        # while True:
        #     rospy.sleep(10)
        #     myFaze4.Convert_to_gcode_Send('G1 X90 Y30 Z20 E50')
        #     rospy.sleep(10)
        #     myFaze4.Convert_to_gcode_Send('G1 X0 Y0 Z0 E0')
    if mode == 'offline':
        rospy.init_node("faze4_node")
        rospy.Subscriber('joint_states',JointState,myFaze4.Convert_to_gcode_Send)
        rospy.spin()  # will fall into the insde forever loop

    if mode == 'release':
        myFaze4.home_all_joints()
        # ROS topic Subscriber 
        rospy.init_node("faze4_node")
        rospy.Subscriber('joint_states',JointState,myFaze4.Convert_to_gcode_Send)

        # rospy.Subscriber('move_group/fake_controller_joint_states',JointState,converte_to_gcode)
        # rospy.Subscriber('move_group/display_planned_path',String,converte_to_gcode)
        # rospy.Subscriber('execute_trajectory/action_topics',String,converte_to_gcode)
        # rospy.Subscriber('trajectory_execution_event',String,converte_to_gcode)
        # rospy.Subscriber('chatter',String,converte_to_gcode)
        rospy.spin()  # will fall into the insde forever loop

    if mode == 'fan':
        while True:
            ss = input ("Input fan speed        ")
            myFaze4.set_fan_speed(ss)
