
# sudo chmod 666 /dev/ttyUSB0
# roslaunch faze4_moveit demo.launch rviz_tutorial:=true
from abc import abstractmethod
import serial, time

import sys
sys.path.append("../")
from app_global.gogame_config import app_config
if app_config.platform == "ubuntu_gui":
    import rospy 
    from std_msgs.msg import String
    from sensor_msgs.msg import JointState


class _Reprap_serial:
    '''
    Hand shaking with controller through serial port.
    '''
    def __init__(self, portname, baudrate):
        self.__serialport = serial.Serial()
        self.__serialport.port = portname
        self.__serialport.baudrate  = baudrate
        self.__serialport.timeout = 1
        self.__serialport.writeTimeout = 2
        
        self.__counter = 0
        self.__echo_is_on = False

    def Connect(self):
        self.__serialport.open()
        if self.__echo_is_on:
            print ('Reprap_host::Serial port is opened.')
        while True:
            xx = self.__serialport.readline()
            mm = bytes.decode(xx)
            if (mm == ''):
                break

    def set_echo_on(self, is_on):
        self.__echo_is_on = is_on

    def SendCommandCode(self, raw_gcode):
        self.__counter += 1
        self.__serialport.write(str.encode(raw_gcode +'\r\n'))
        if self.__echo_is_on:
            print ('>>> %s' % raw_gcode)
        got_ok = False
        while not got_ok:
            response_a = self.__serialport.readline()
            response = bytes.decode(response_a)
            if(response == 'ok\n'):
                got_ok = True
                if self.__echo_is_on:
                    print ('OK')
            elif (response ==''):
                rospy.sleep(0.1)
            elif self.__echo_is_on:
                print("<<< " + response)


from enum import Enum
class HARD_ROBOT_ONLINE_LEVEL(Enum):
    OFF_LINE = 1
    ONLINE_AS_REPRAP = 2
    ONLINE_AS_FAZE4 = 3
    HOMED = 4

from robot_arm.robot_kinematic import Pose_IK



class Hard_robot:
    '''
    Subscribe ROS message(JointState) from moveit.
    Convert JointState to gcode
    Send gcode to serial, confirm Reprap got the gcode correctly.
    '''
    def __init__(self):
        '''
        This will create an object, But will not connect to Marlin
        '''
        self.__sleep_time = 5
        self.current_pose_IK = Pose_IK()
        self.mode = HARD_ROBOT_ONLINE_LEVEL.OFF_LINE
        self.jonit5_is_following_FK = True
        self.__log_level = 0

    def connect_to_marlin(self):
        '''
        This function will set mode to ONLINE_AS_FAZE4
        '''
        self._my_serial = _Reprap_serial('/dev/ttyUSB0',115200)
        self._my_serial.Connect()
        self.Init_Marlin()
        self.mode = HARD_ROBOT_ONLINE_LEVEL.ONLINE_AS_FAZE4

    def Init_Marlin(self):
        '''
        Please pay attention:
        Must invoke Init_Marlin before sending any gCode.
        Otherwise, some gcodes will not be executed.
        '''
        self._my_serial.SendCommandCode('M302 S0')  # Allow extrusion at any temperature
        # self._my_serial.SendCommandCode('T1')    # Joint5 as Extruder
        self._my_serial.SendCommandCode('M84 S0')  #Disable sleep
        self._my_serial.SendCommandCode('M17 X Y Z E') #enable all steppers
        self._my_serial.SendCommandCode('M111 S255') # https://marlinfw.org/docs/gcode/M111.html
        self.set_fan_speed(180)    

        self._my_serial.SendCommandCode('G83')   #M83: Set extruder to relative mode
        self._my_serial.SendCommandCode('M201 X500 Y500')    # Set acceleration
        self._my_serial.SendCommandCode('M503')
        self._my_serial.SendCommandCode('M92 X64 Y64')    # Set setps_per_unit
        self._my_serial.SendCommandCode('M503')
        self._my_serial.SendCommandCode('M280 P0 S0')   # Servo lift up
        # _my_serial.SendCommandCode('M160 2') # Color mixing  
        
        # under relative position and move arms togeth around 45 degree
        self._my_serial.SendCommandCode('G91')
        self._my_serial.SendCommandCode('G1 X-45 Y45')

        # Work under absolute coordinator
        self._my_serial.SendCommandCode('G90')
        
        self.mode = HARD_ROBOT_ONLINE_LEVEL.ONLINE_AS_REPRAP

    

    @abstractmethod
    def set_joints_angle_in_degree(self, IK_dict):
        print('set_joints_angle_in_degree not implatemented')

    def set_fan_speed(self, speed):
        '''
        speed from 0 to 255
        '''
        self._my_serial.SendCommandCode('M106 S' + str(speed))

    def Test1_G1(self):
        while True:
            # _my_serial.SendCommandCode('G1 E 45 E1 45')
            self._my_serial.SendCommandCode('G1 E 45')
            rospy.sleep(5)
            # _my_serial.SendCommandCode('G1 E 90 E1 90')
            self._my_serial.SendCommandCode('G1 E 90')
            rospy.sleep(5)
            # _my_serial.SendCommandCode('G1 E 0 0 E1 0')
            self._my_serial.SendCommandCode('G1 E 0')
            rospy.sleep(3)
    
    def Test2_home_sensor(self):
        '''
        print out status of all joints home sensor.
        include joint5? I forgot it, depend on Marlin firmware. 
        '''
        self._my_serial.SendCommandCode('M84')
        while True:
            self._my_serial.SendCommandCode('M119')
            rospy.sleep(1)


    
    def eef_pick_up(self):
        if self.mode == HARD_ROBOT_ONLINE_LEVEL.OFF_LINE:
            print('[Warning]: Robot is offline ')
            return

        self._my_serial.SendCommandCode('M183 S1')

    def eef_place_down(self):
        if self.mode == HARD_ROBOT_ONLINE_LEVEL.OFF_LINE:
            print('[Warning]: Robot is offline ')
            return

        self._my_serial.SendCommandCode('M183 S2')
    
    def eef_sleep(self):
        if self.mode == HARD_ROBOT_ONLINE_LEVEL.OFF_LINE:
            print('[Warning]: Robot is offline ')
            return

        self._my_serial.SendCommandCode('M183 S0')

    @abstractmethod
    def joint5_angle_minus(self):
        print('[Warning] joint5_angle_minus: This is an abstract method')

    @abstractmethod
    def joint5_angle_plus(self):
        print('[Warning] joint5_angle_plus: This is an abstract method')

    @abstractmethod
    def home_all_joints(self):
        print('[Warning] This is an abstract method')
        