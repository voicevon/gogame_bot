
class GoGamePose_BeyondChessboard():
    '''
    This class will not deal with any pose inside/on the chessboard.
    You can get more infomation from  chessboard_cell.py, chessboard_helper.py, chessboard_runner
    '''
    def __init__(self, robot_type):
        self.diction_IK_only = {}
        self.diction_pose_beyond_chessboard = {}

        if robot_type == 'GOSCARA':
            self.diction_IK_only = {'HOME','ZERO','PARK'}
            self.diction_pose_beyond_chessboard = {'WAREHOUSE','TRASH','VIEW'}

        if robot_type == 'FAZE4':
            self.diction_IK_only = {'HOME','ZERO','CR2','CR3','CR5'}
            self.diction_pose_beyond_chessboard = {'WAREHOUSE','TRASH','VIEW'}

    def is_IK_only_pose(self, pose_name):
        if pose_name in self.diction_IK_only:
            return True
        return False
    


