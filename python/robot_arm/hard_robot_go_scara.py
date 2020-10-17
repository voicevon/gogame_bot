# sudo chmod 666 /dev/ttyUSB0


from hard_robot import Hard_robot,HARD_ROBOT_ONLINE_LEVEL
import rospy 
from sensor_msgs.msg import JointState

class Hard_robot_GoScara(Hard_robot):

    def Test33_home_x(self,pause_second=0,target_position=0):
        self._my_serial.SendCommandCode('G28 X')
        self._my_serial.SendCommandCode('G1 X ' + str(target_position))
        rospy.sleep(pause_second)
        # self._my_serial.SendCommandCode('G1 X ' + str(180-40))


    def Test31_home_y(self, pause_second=0,target_position=0):
        self._my_serial.SendCommandCode('G28 Y')
        self._my_serial.SendCommandCode('G1 Y' + str(target_position))
        rospy.sleep(pause_second)
        # self._my_serial.SendCommandCode('G1 Y' + str(45))

    def Test_G1_x(self,pause_second=0,target_position=100):
        self._my_serial.SendCommandCode('G1 X' + str(target_position))
        rospy.sleep(pause_second)      
    
    def Test_G1_y(self,pause_second=0,target_position=100):
        self._my_serial.SendCommandCode('G1 Y' + str(target_position))
        rospy.sleep(pause_second)   

    def Test_G1_xy(self,x,y):
        self._my_serial.SendCommandCode('G1 X' + str(x) + ' Y'+str(y))

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

        self._my_serial.SendCommandCode('G28 X')
        self._my_serial.SendCommandCode('G28 Y')
        # self._my_serial.SendCommandCode('G1 X0 Y0 Z0 E0') 
        self.mode = HARD_ROBOT_ONLINE_LEVEL.HOMED        

    def set_z_position(self,posistion_mm):
        s_value = 0
        if posistion_mm == -1:
            s_value = 45   # degree
        if posistion_mm == -2:
            s_value = 180

        self._my_serial.SendCommandCode('M280 P0 S' + str(s_value))

    def __convert_ik_joint_z_to_servo_angle(self,joint_z_value):
        '''
        joint_z_value: unit is meter.
        '''
        k = 3.6
        c = 21.6
        servo_angle = k * joint_z_value * 1000 + c
        if servo_angle >180:
            servo_angle = 180
        elif servo_angle < 0:
            servo_angle = 0
        return int(servo_angle)

    def Convert_to_gcode_Send(self,joint_states):
        '''
        Convert ROS message::joint_states to gcode G1.
        Then, send out gCode like "G1 X11 Y22 Z33 E44" 

        '''
        # print (joint_states)
        #  [lj1, lj2, lj3, lj4, lj5, lj6, rj1, rj2, rj3, rj4, rj5, rj6]


        to_degree = 180.0 / 3.14159
        angle_x = joint_states.position[0] * to_degree
        angle_y = joint_states.position[6] * to_degree
        position_z = joint_states.position[2]
        # joint_states.position[2]  # unit from IK_solver is meter
        # print ('joint[2] for z position from joint_states is' + str(joint_states.position[2]))
        # position_z = 0
        # if joint_states.position[2] <= -0.3:
        #     position_z = 180
        # elif joint_states.position[2]<= -0.1:
        #     position_z = 100
            # print('[ERROR]: Hard_robot_go_scara::Convert_to_gcode_Send()' + str(joint_states.position[2]))


        # If all angles has no updating, just return, 
        # don't send any G1 code to Marlin 
        if self.current_pose_IK.j1_angle_in_degree == angle_x:
            if self.current_pose_IK.j2_angle_in_degree == angle_y:
                if self.current_pose_IK.j3_angle_in_degree == position_z:
                    return

                                
        self.current_pose_IK.j1_angle_in_degree = angle_x
        self.current_pose_IK.j2_angle_in_degree = angle_y
        self.current_pose_IK.j3_angle_in_degree = position_z

        if self.mode == HARD_ROBOT_ONLINE_LEVEL.OFF_LINE:
            print('[Warning: Hard_Robot.Convert_to_gcode_Send(). mode == OFF_LINE')
            return 
        firmware_angle_x = angle_x + 180
        gcode = 'G1 X' + str(round(firmware_angle_x,2)) + ' Y' + str(round(angle_y,2)) + ' F18000'
        self._my_serial.SendCommandCode(gcode)

        # position_z = joint_states.position[2] * 1000
        # print('qqqqqqqqqqqqqqqqqqqq'+ str(position_z))
        # k = 3.6
        # c = 21.6
        # position_z = k* position_z + c
        # if position_z >180:
        #     position_z = 180
        # elif position_z < 0:
        #     position_z = 0
        servo_angle = self.__convert_ik_joint_z_to_servo_angle(joint_states.position[2])
        gcode = 'M280 P0 S' + str(servo_angle)
        self._my_serial.SendCommandCode(gcode)


    def set_joints_angle_in_degree(self, IK_dict):
        self.current_pose_IK.from_diction(IK_dict)
        firmware_angle_x = IK_dict['j1'] + 180
        gcode = 'G1 X' + str(firmware_angle_x) + ' Y' + str(IK_dict['j2']) + ' F18000'
        # print(gcode)
        if self.mode == HARD_ROBOT_ONLINE_LEVEL.OFF_LINE:
            print ('[Warning]: hard_robot is offline.')
            return 
        self._my_serial.SendCommandCode(gcode)
        # k = 3.6
        # c = 21.6
        # position_z = int(k* IK_dict['j3']*1000 + c)
        
        servo_angle = self.__convert_ik_joint_z_to_servo_angle(IK_dict['j3'])
        gcode = 'M280 P0 S' + str(servo_angle)
        self._my_serial.SendCommandCode(gcode)


        
if __name__ == "__main__":
    mode = 'calibration'    # To calibrate home position. Those are a group of const numbers for each joint.
    # mode = 'offline'        # Do not connect to Marlin, The messages from MoveIt will be ignored.
    # mode = 'release'
    # mode = 'fan'
    
    myGoScara = Hard_robot_GoScara()
    myGoScara.connect_to_marlin()
    if mode == 'calibration':
        '''
        '''
        # target_xy = 20
        # myGoScara.Test_G1_x(target_position=target_xy)
        # myGoScara.Test_G1_y(target_position=target_xy)
        # myGoScara.Test33_home_x(pause_second=5, target_position=180)
        # myGoScara.Test31_home_y(pause_second=15, target_position=0)
        # myGoScara._my_serial.SendCommandCode('G1 X135 Y45')

        while True: 
        #     myGoScara.Test2_home_sensor()

            myGoScara.set_z_position(0)
            rospy.sleep(1)
            myGoScara.set_z_position(-1)
            rospy.sleep(1)
            myGoScara.set_z_position(-2)
            rospy.sleep(3)


            # X_HOME = 180
            # Y_HOME = 0
            # myGoScara.Test_G1_xy(X_HOME - 70, Y_HOME + 70)
            # myGoScara.Test_G1_xy(X_HOME - 50, Y_HOME + 50)

        # while True:
        #     rospy.sleep(10)
        #     myGoScara.Convert_to_gcode_Send('G1 X90 Y30 Z20 E50')
        #     rospy.sleep(10)
        #     myGoScara.Convert_to_gcode_Send('G1 X0 Y0 Z0 E0')
    if mode == 'offline':
        rospy.init_node("faze4_node")
        rospy.Subscriber('joint_states',JointState,myGoScara.Convert_to_gcode_Send)
        rospy.spin()  # will fall into the insde forever loop

    if mode == 'release':
        myGoScara.home_all_joints()
        # ROS topic Subscriber 
        rospy.init_node("faze4_node")
        rospy.Subscriber('joint_states',JointState,myGoScara.Convert_to_gcode_Send)

        # rospy.Subscriber('move_group/fake_controller_joint_states',JointState,converte_to_gcode)
        # rospy.Subscriber('move_group/display_planned_path',String,converte_to_gcode)
        # rospy.Subscriber('execute_trajectory/action_topics',String,converte_to_gcode)
        # rospy.Subscriber('trajectory_execution_event',String,converte_to_gcode)
        # rospy.Subscriber('chatter',String,converte_to_gcode)
        rospy.spin()  # will fall into the insde forever loop

    if mode == 'fan':
        while True:
            ss = input ("Input fan speed        ")
            myGoScara.set_fan_speed(ss)
