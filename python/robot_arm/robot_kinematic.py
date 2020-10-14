class Pose_FK:
    def __init__(self):
        '''
        default at camera view_point.
        unit is mm
        '''
        self.x = 0
        self.y = 300
        self.z = 200
        self.w = 0     # Face down ??
    
    def from_values(self,x,y,z,w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def to_diction(self):
        return {'x':self.x, 'y':self.y, 'z':self.z, 'w':self.w}

    def from_diction(self,FK_diction):
        self.x = FK_diction['x']
        self.y = FK_diction['y']
        self.z = FK_diction['z']
        self.w = FK_diction['w']
        return self


class Pose_IK:

    def __init__(self):
        '''
        default at camera view_point
        '''
        self.j1_angle_in_degree = 0.0
        self.j2_angle_in_degree = 0.0
        self.j3_angle_in_degree = 0.0
        self.j4_angle_in_degree = 0.0
        self.j5_angle_in_degree = 0.0
        self.j6_angle_in_degree = 0.0
    
    def set_values(self, j1, j2, j3, j5):
        self.j1_angle_in_degree = j1
        self.j2_angle_in_degree = j2
        self.j3_angle_in_degree = j3
        self.j5_angle_in_degree = j5

    def from_rad_to_degree(self):
        self.j1_angle_in_degree = self.__to_degree(self.j1_angle_in_degree)
        self.j2_angle_in_degree = self.__to_degree(self.j2_angle_in_degree)
        self.j3_angle_in_degree = self.__to_degree(self.j3_angle_in_degree)
        self.j5_angle_in_degree = self.__to_degree(self.j5_angle_in_degree)


    # @staticmethod
    def __to_degree(self, rad_value):
        return rad_value * 180 /3.1416

    def to_diction(self):
        return {'j1':self.j1_angle_in_degree, 'j2':self.j2_angle_in_degree, 'j3':self.j3_angle_in_degree,'j5':self.j5_angle_in_degree}

    def from_diction(self,IK_diction):
        self.j1_angle_in_degree = IK_diction['j1']
        self.j2_angle_in_degree = IK_diction['j2']
        self.j3_angle_in_degree = IK_diction['j3']
        self.j5_angle_in_degree = IK_diction['j5']
        return self


class Pose():

    def __init__(self):
        self.name = 'VIEW'
        self.FK = Pose_FK()
        self.IK = Pose_IK()
    
    def from_pair(self, name, dict_FK, dict_IK):
        self.name = name
        self.FK = self.FK.from_diction(dict_FK)
        self.IK = self.IK.from_diction(dict_IK)

    def clone(self,new_pose_name):
        target = Pose()
        target.name = new_pose_name
        target.FK.from_diction(self.FK.to_diction())
        target.IK.from_diction(self.IK.to_diction())
        return target
        
if __name__ == "__main__":
    pose = Pose()
