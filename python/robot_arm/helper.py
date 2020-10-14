
from robot_kinematic import Pose
import json
# from chessboard_helper import ChessboardCell

class Orientation_helper:
    '''
    This class should be a kind of static class. 
    But I don't know how to write code for a static class in Python.  :(

    '''
    def __init__(self):
        pass

    def get_w_face_up(self):
        return 1
    
    def get_w_face_down(self):
        return 0.0
        # return 1.0

    def get_w_face_left(self):
        return 0.43


class Robot_pose_helper:
    '''
    Some individual functions
    '''
    def __init__(self):
        '''
        Chessboard center position in world coordinator.
        
        All position and length are in unit mm.

        top,bottom,left,right is defined from camera view:
            
            Top-left ==> "A1"     Top-right ==> "T1"
            
            Bottom-left ==> "A19"    Bottom-right ==> "T19"   
        '''


        self.board_center_x = 0.0
        # self.board_center_y = 300.0  # Faze4
        self.board_center_y = 200.0  # Go Scara
        self.board_center_z = 63.0
        self.cell_width_x = 17.778
        self.cell_width_y = 18.0
        
        self.zero_in_world_x = self.board_center_x - self.cell_width_x * 9
        self.zero_in_world_y = self.board_center_y - self.cell_width_y * 9
        self.orientaion_helper = Orientation_helper()

        # init pose_diction from json file
        self.pose_diction= {}
        # self.pose_IK_only_diction = {'HOME','ZERO','CR1','CR2','CR3','CR5'}
        # self.pose_FK_adjust_command_diction = {'UP','DOWN','LEFT','RIGHT','FRONT','BACK'}

        self.CONFIG_FILENAME = 'poses.json'        
        self.read_json_file_to_pose_diction(self.CONFIG_FILENAME)

        print('zero in world [x,y]', self.zero_in_world_x,self.zero_in_world_y)

    def from_pose_diction(self, pose_name, copy_from_this_pose_name = None):
        '''
        Try to copy  FK,IK from pose_diction,
        If not found in diction, will create one , values is the default, or copy from a pose.
        NOTE: If found in diction, will not copy values from specified source pose. 
        '''
        target_pose = Pose()  # values is the default
        target_pose.name = pose_name
        
        if self.pose_diction.get(pose_name):
            # Found in pose_diction
            dict_FK = self.pose_diction[pose_name]['FK']
            dict_IK = self.pose_diction[pose_name]['IK']
            target_pose.FK.from_diction(dict_FK)
            target_pose.IK.from_diction(dict_IK)
            return target_pose
        else:
            return None

    def copy_pose_values(self, from_pose_name, to_pose_name):
        dict_IK = self.pose_diction[from_pose_name]['IK']
        dict_FK = self.pose_diction[from_pose_name]['FK']
        self.pose_diction[to_pose_name] = {'FK':dict_FK,'IK':dict_IK}

    def read_json_file_to_pose_diction(self, filename):
            with open(filename) as f_in:
                self.pose_diction =  json.load(f_in)

    def write_pose_diction_to_json_file(self):
        with open(self.CONFIG_FILENAME, 'w') as outfile:
            json.dump(self.pose_diction, outfile, ensure_ascii=False, indent=4)
    
    def convert_to_world_position(self,cell_name):
        '''
        Go_position instance: "Q4" as position on 2D Chessboard.
        XY_position instance: "[0.015,0.02,-0.01]" as [x,y,z] in 3D world coordinator.
        '''
        ss = "ABCDEFGHIJKLMNOPQRST"
        iCol = ss.find(cell_name[:1])
        iRow = 19 - int(cell_name[1:])
        world_x = self.zero_in_world_x +  self.cell_width_x * iCol
        world_y = self.zero_in_world_y + iRow * self.cell_width_y

        # cell = ChessboardCell()
        # cell.from_name(cell_name)

        # world_x = self.zero_in_world_x +  self.cell_width_x * cell.col_id
        # world_y = self.zero_in_world_y + cell.row_id * self.cell_width_y

        return world_x, world_y, self.board_center_z,self.orientaion_helper.get_w_face_down()


if __name__ == "__main__":
    test = Robot_pose_helper()