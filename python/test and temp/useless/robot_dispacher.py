#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import socket
import time
# from faze4_controller import robotController
# from moveit_client import MoveIt_client
import sys
sys.path.append('/home/xm/gitrepo/ros_marlin_bridge/robot_arm')
# sys.path.append('/home/xm/gitrepo/ros_marlin_bridge/robot_eye')
from robot_arm.Human_level_robot import Human_level_robot
sys.path.append('/home/xm/gitrepo/ros_marlin_bridge/go_gameboard')
# print(sys.path)
from chessboard_cell import ChessboardCell

class Robot_dispacher:
    '''
    Deal with Go-command with Go-coordinator ,
    Convert to world coordinator, 
    Send to MoveIt.
    '''
    def __init__(self, connect_to_hard_robot=True):
        # self.my_moveit = MoveIt_client()
        self.thread_stop = False
        # self.HOST = '127.0.0.1'
        # self.PORT = 50008
        # self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # 定义socket类型，网络通信，TCP
        '''
        定义几个坐标原点：
        中心点：机器手臂的默认坐标，位于棋盘中心上方.#############此点回复功能.
        棋盘零点：对应棋盘的A19
        棋盘原点：棋盘中心上方的位置，正常应该退回到这里（假设摄像头在上面，需要随时图像识别）
        黑子点：取黑子的位置
        白子点：取白字的位置
        垃圾点：放置提子或其他取回来的棋子的点
        棋盘单元格大小：棋盘每个单元格的宽度/高度
        单位：毫米
        '''
        self.ArmCenterX = -10
        self.ArmCenterY = -10
        self.ArmCenterZ = -10
        self.QiZeroX = -10
        self.QiZeroY = -10
        self.QiZeroZ = -10
        self.BlackX = 5
        self.BlackY = 5
        self.BlackZ = 5
        self.WhiteX = 15
        self.WhiteY = 15
        self.WhiteZ = 15
        self.RefuseX = 20
        self.RefuseY = 20
        self.RefuseZ = 20
        self.QiWidth = 18   # Cell length in Chessboard.unit is mm 
        self.ZMove = 10
        # self.chessboard_helper = Chessboard_helper()
        # init robot
        self.robot = Human_level_robot('GOSCARA')
        if connect_to_hard_robot:
            self.robot.bridge_hard_robot_connect_to_marlin()
            self.robot.bridge_hard_robot_home_all_joints()
        self.robot.bridge_soft_robot_connect_to_moveit()



    def useless_setOriginPoint_chessboard_center_in_world_coordinator(self, xp, yp, zp):
        '''
        设置当前的棋盘中心点(Go系统的原点).
        同时计算其他的点
        '''
        self.QiCenterX = xp
        self.QiCenterY = yp
        self.QiCenterZ = zp
        self.BlackX = xp + 10
        self.BlackY = yp + 10
        self.BlackZ = zp + 10
        self.WhiteX = xp + 50
        self.WhiteY = yp + 50
        self.WhiteZ = zp + 50
        self.RefuseX = xp + 100
        self.RefuseY = yp + 100
        self.RefuseZ = zp + 100
        self.QiZeroX = xp + 500
        self.QiZeroY = yp + 500
        self.QiZeroZ = zp + 500

    # def openSocket(self):
    #     try:
    #         self.s.connect((self.HOST, self.PORT))       # 要连接的IP与端口
    #         return True
    #     except ConnectionRefusedError:
    #         print("Arm_Bridge Socket打开失败")
    #         return False

    def WriteCommand(self, command):
        '''
        本函数接收的是逻辑命令
        类型上，可以分为两类：
        第一类：play,即向棋盘放一个棋子,形如 play white H5。可分解为动作：moveto(x,y,z)棋盒位置;hand(pick)拾取;moveto(x,y,z)棋子位置;hand(place)丢弃;moveto(x,y,z)原点位置
        第二类：move,即取走棋盘上的某个棋子，形如 move Q4。
                            可分解为动作：moveto（x,y,z）棋子位置;
                            hand(pick)拾取;moveto(x,y,z)垃圾区;
                            hand(place)丢弃;
                            moveto(x,y,z)原点位置
        command命令的可能是组合的，如move Q3,move Q4,play black Q3
        因此，整体思路上是，现将多个逻辑命令，分解为单个的逻辑命令。然后，再将单个的逻辑命令分成robot动作命令。
        现在，不考虑多个动作中，如果有动作执行失败怎么办；也就是说，不考虑动作执行到一半，出错后的后续处理，比如复位等。
        :param command:逻辑命令，可能是多个的组合
        :return:执行结果（True OR False）
        '''
        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        # print("arm_bridge write command:"+command)
        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        # time.sleep(5)
        # return
        # 第一步：现将多个逻辑命令。根据maingocontroller的逻辑，给出的都是“,”分割的
        commands = command.split(",")
        for oneCommand in commands:
            print(oneCommand)
            if len(oneCommand) > 5:  # 主要是为了过滤最后一个“,”
                # oneCommand=oneCommand.replace("move move","move")# 命令不知道为什么会连着两个move，先这样吧
                # 第二步：开始分析逻辑命令，准备分解为动作命令
                doCommand = oneCommand.split(" ")
                if len(doCommand) > 0:
                    if doCommand[0] == "play":
                        # play命令，要区分黑白的。代码有重复，稍后优化。
                        if doCommand[1] == "black":
                            # 放黑子，因此需要分解为：到1黑子区，2取子，3到目标区，4放子，5返回初始位置
                            # ###########################################################################
                            # print("==========到黑子区域上方==========")
                            # self.moveto(self.BlackX, self.BlackY, self.BlackZ + self.ZMove)
                            # self.moveto(self.BlackX, self.BlackY, self.BlackZ)

                            # ############################################################################
                            # print("==========取子==========")
                            # self.hand(1)   # RobbotCommand2 = "hand:1"  # 取子
                            # self.moveto(self.BlackX, self.BlackY, self.BlackZ + self.ZMove)
                            # #############################################################################
                            # print("==========到目标区域上方==========")
                            # LuoJiPos = doCommand[2]  # Q4
                            # targetX, targetY = self.getXY(LuoJiPos)
                            # self.moveto(targetX, targetY, self.QiZeroZ + self.ZMove)
                            # self.moveto(targetX, targetY, self.QiZeroZ)

                            # ############################################################################
                            # print("==========放子==========")
                            # self.hand(0)   # RobbotCommand4 = "hand:0"  # 放子
                            # self.hand(3)   # RobbotCommand4 = "hand:3"  # 断电
                            # self.moveto(targetX, targetY, self.QiZeroZ + self.ZMove)
                            # ############################################################################
                            # print("==========到前盘区域正上方==========")
                            # self.moveto(self.ArmCenterX, self.ArmCenterY, self.ArmCenterZ)
                            repos = self.getDp(doCommand[2])
                            print("position  {0}  to  {1}".format(doCommand[2], repos))
                            # return
                            self.robot.action_pickup_chess_from_warehouse()
                            self.robot.action_place_chess_to_a_cell(repos)
                            target_pose  =  self.robot.get_target_pose_by_name('VIEW')
                            self.robot.goto_here(target_pose)

                        else:
                            # # 放白子，因此需要分解为：到1白子区，2取子，3到目标区，4放子，5返回初始位置
                            # ###########################################################################
                            # print("==========到白子区域上方==========")
                            # self.moveto(self.WhiteX, self.WhiteY, self.WhiteZ + self.ZMove)
                            # self.moveto(self.WhiteX, self.WhiteY, self.WhiteZ)

                            # ############################################################################
                            # print("==========取子==========")
                            # self.hand(1)   # RobbotCommand2 = "hand:1"  # 取子
                            # self.moveto(self.WhiteX, self.WhiteY, self.WhiteZ + self.ZMove)
                            # #############################################################################
                            # print("==========到目标区域上方==========")
                            # LuoJiPos = doCommand[2]  # Q4
                            # targetX, targetY = self.getXY(LuoJiPos)
                            # self.moveto(targetX, targetY, self.QiZeroZ + self.ZMove)
                            # self.moveto(targetX, targetY, self.QiZeroZ)

                            # ############################################################################
                            # print("==========放子==========")
                            # self.hand(0)   # RobbotCommand4 = "hand:0"  # 放子
                            # self.hand(3)   # RobbotCommand4 = "hand:3"  # 断电
                            # self.moveto(targetX, targetY, self.QiZeroZ + self.ZMove)
                            # ############################################################################
                            # print("==========到棋盘区域正上方==========")
                            # self.moveto(self.ArmCenterX, self.ArmCenterY, self.ArmCenterZ)
                            self.robot.action_pickup_chess_from_warehouse()
                            repos = self.getDp(doCommand[2])
                            print("position  {0}  to  {1}".format(doCommand[2], repos))
                            
                            self.robot.action_place_chess_to_a_cell(repos)
                            target_pose  =  self.robot.get_target_pose_by_name('VIEW')
                            self.robot.goto_here(target_pose)

                    elif doCommand[0] == "move":
                        # 移走棋子，因此需要分解为：到1目标区，2取子，3到垃圾区，4放子，5返回初始位置

                        # ###########################################################################
                        # print("==========到目标区域上方==========")
                        # LuoJiPos = doCommand[1]  # Q4
                        # targetX, targetY = self.getXY(LuoJiPos)

                        # self.moveto(targetX, targetY, self.QiZeroZ + self.ZMove)
                        # self.moveto(targetX, targetY, self.QiZeroZ)

                        # ############################################################################
                        # print("==========取子==========")
                        # self.hand(1)   # RobbotCommand2 = "hand:1"  # 取子
                        # #############################################################################
                        # print("==========到垃圾回收区域上方==========")
                        # self.moveto(self.RefuseX, self.RefuseY, self.RefuseZ + self.ZMove)

                        # ############################################################################
                        # print("==========弃子==========")
                        # self.hand(0)   # RobbotCommand4 = "hand:0"  # 放子
                        # self.hand(3)   # RobbotCommand4 = "hand:3"  #断电
                        # ############################################################################
                        # print("==========到棋盘区域正上方==========")
                        # self.moveto(self.ArmCenterX, self.ArmCenterY, self.ArmCenterZ)
                        repos = self.getDp(doCommand[1])
                        print("position  {0}  to  {1}".format(doCommand[1], repos))
                        
                        self.robot.action_pickup_chess_from_a_cell(repos)
                        self.robot.action_place_chess_to_trash_bin()

                    # elif doCommand[0] == "moveto":
                    #     # 移动到某个位置，一般这个位置是原点，也就是棋盘的正中心上方
                    #     self.moveto(int(doCommand[1]), int(doCommand[2]), int(doCommand[3]), False, False)
                    #     time.sleep(1)
                    else:
                        # 应该是非法命令，不用管理
                        print(">>>>>收到非法命令，不能解析。跳过")
                        print(doCommand[0])
                        time.sleep(1)

    # def colseSocket(self):
    #     self.s.close()   # 关闭连接
    # def moveit_goto_xm(self,go_position):
    #     '''
        
    #     '''
    #     if self.poses_helper.is_pose_name(go_position):
    #         x,y,z,w = self.poses_helper.get_pose(go_position)
    #     else:
    #         x,y,z,w = self.chessboard_helper.convert_to_world_position(go_position)
        
    #     self.my_moveit.goto_pose(x,y,z,w)


    def moveto(self, x, y, z):
        '''
        moveto函数改进
        1.增加是否提升，是否降落标识，利用这两个标识，确定移动之前是否要升，以及移动之后是否要降。
        '''
        MoveCommand1 = "moveto:" + str(x) + "," + str(y) + "," + str(z)
        print(MoveCommand1)
        # set command
        # self.my_moveit.goto_pose(x, y, z)
        time.sleep(1)
        # wait for ended
        # my_GetCurPosition = True
        # while my_GetCurPosition:
        #     if 'idle' == self.my_moveit.getState():
        #         my_GetCurPosition = False

    def hand(self, state):
        '''
        state,电磁铁状态，1表示吸，0表示斥，3表示没电
        '''
        # robotController.pick_place(state)   # 
        # my_moveit.pick()
        time.sleep(2)  # 等待2秒，不再判断是否执行

    def getXY(self, pos):
        '''
        input = Q4
        return = 
        '''
        # Q4
        ss = "ABCDEFGHJKLMNOPQRST"
        iCol = ss.find(pos[:1])
        iRow = 19 - int(pos[1:])
        targetX = self.QiZeroX + (iCol * self.QiWidth)
        targetY = self.QiZeroY - (iRow * self.QiWidth)
        print('ttttttttttttttttttttttttttttttttttt')
        print targetX,targetY
        return targetX, targetY
    
    def getDp(self, pos):
        '''
        ==========================
        return pos
        '''
        # ss = "ABCDEFGHJKLMNOPQRST"
        # iCol =ss.find(pos[:1])
        # iRow = 20 - int(pos[1:])
        # return ss[20-iRow-1:20-iRow]+str(19-iCol)
        return pos


if __name__ == '__main__':
    tester = Robot_dispacher()
    while True:
        print("Testing Robot_dispacher, command like 'play black Q4' 'move Q4',1 to break")
        # input() vs raw_input()
        # https://stackoverflow.com/questions/4960208/python-2-7-getting-user-input-and-manipulating-as-string-without-quotations
        # test_cmd = raw_input("Input Go_dipacher command: like 'move q4' ")
        # tester.WriteCommand(test_cmd)
        test_cmd = raw_input("Input command: like 'play black Q4' ")
        print(test_cmd)
        if test_cmd == "1":
            break
        tester.WriteCommand(test_cmd)
