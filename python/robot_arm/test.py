from robot_kinematic import Pose_FK
from soft_robot import Soft_robot
import rospy

if __name__ == "__main__":

    rospy.init_node('move_group_python_interface_tutorial',
                anonymous=True)
    tester = Soft_robot()
    tester.connect_to_moveit()
    
    # tester.show_current_pose()

    target_FK = Pose_FK()
    target_FK.x = 200
    target_FK.y = 330
    target_FK.z = 70
    target_FK.w = 0

    tester.goto_the_pose_uint_mm(target_FK)
    # tester.goto_the_pose({'x':0, 'y':300, 'z':200 , 'w':0})
    # tester.goto_the_pose({'x':0, 'y':0, 'z':700 , 'w':1})