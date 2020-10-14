#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
sys.path.append('/home/xm/gitrepo/ros_marlin_bridge/robot_eye')
from single_eye import SingleEye
myrobotEye = SingleEye()

from robot_dispacher import Robot_dispacher
my_robot_dispacher = Robot_dispacher()

print ('Manager is ready...')

import threading
import time
from go_game_client import myGoGameClient

import copy
# from arm_bridge import myarm_bridge

# 线程是否正常进行内容的条件
GoCommand = ""
RobotCommand = ""
NeedOpenCV = False

# 当前棋盘的各种状态
BeginPlay = False
GoRunning = False
HumanRunning = False
RobotRunning = False
HumanEnded = False
HumanFailed = False

# 棋盘定义。三张棋盘。0是空，3是白，8是黑
GoBoard = [([0] * 19) for i in range(19)]
CurBoard = [([0] * 19) for j in range(19)]
BefBoard = [([0] * 19) for k in range(19)]


class OpenCVThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.thread_stop = False
        
    def run(self):
        global NeedOpenCV
        global BeginPlay
        global GoCommand
        global RobotCommand
        global GoRunning
        global HumanRunning
        global RobotRunning
        global HumanEnded
        global HumanFailed
        global GoBoard
        global CurBoard
        global BefBoard

        while not self.thread_stop:
            # OpenCV处理主线程
            if NeedOpenCV:
                print(">>>>OpenCV开始处理\r\n")
                # test_cmd = raw_input("Input command: not 1 ")
                if GoRunning:
                    print(">>>>当前状态GoRunning")
                    # acmd = input("输入当前Go走的位置，模拟openCV获取的真实棋盘(position):")
                    # if acmd=="y":
                    #     print("不对当前棋盘做更改，假设没有动")
                    # else:
                    #     SetCurBoard(8, acmd)
                    # 通过openCV服务获取当前逻辑棋盘
                    IfGetBoard, CurBoard = myrobotEye.getCurBoard()
                    if IfGetBoard is False:
                        # 没有成功获取棋盘，可能是有胳膊或者其他东西挡着
                        print(">>>>没有成功获取棋盘")
                        time.sleep(5)
                        continue
                    print(">>>>比较棋盘")
                    # 比较当前棋盘与之前的棋盘有何不同
                    curBoardDif = GetCurBoardDifGoBoard()
                    if curBoardDif == "":
                        print("openCV 判断棋盘一致，Go走棋结束\r\n")
                        print("before棋盘==当前棋盘\r\n")
                        BefBoard = copy.deepcopy(CurBoard)
                        printBefBoard()
                        printCurBoard()
                        NeedOpenCV = False
                        print("openCV执行结束>>>>")
                        GoRunning = False
                        HumanRunning = True
                        time.sleep(1)
                        NeedOpenCV = True
                    elif len(curBoardDif) > 30:
                        print("****发现两个棋盘不一致的太多，很可能是不对的，需要重新识别****")
                        print(curBoardDif)
                    else:
                        print("openCV发现棋盘不一致，需要提子\r\n")

                        NeedOpenCV = False
                        print("openCV执行结束>>>>")
                        RobotCommand = curBoardDif

                if BeginPlay:
                    print(">>>>当前状态BeginPlay")
                    print(">>>>openCV判断是否开局")
                    # acmd = input("图片判断是否开局(Please input y):")
                    # 左上角放黑子，开局
                    isBegin = myrobotEye.getBeginOrEnd()

                    if (isBegin == 8):   # (acmd == 'y'):
                        print("openCV判断开局，Go执黑先行")
                        NeedOpenCV = False
                        GoRunning = True
                        GoCommand = "genmove b\n"
                        BeginPlay = False
                        print("openCV执行结束>>>>")
                    else:
                        # 没有发现开局标记，暂停5秒再进行判断
                        print(">>>>openCV没有发现开局标记，暂停5秒再进行判断")
                        time.sleep(5)
                        continue

                if HumanRunning:
                    print(">>>>当前状态HumanRunning")
                    # acmd = input("人开始走，是否结束(y):")

                    # 棋盘左上角放白子，结束棋局
                    isEnd = myrobotEye.getBeginOrEnd()
                    if isEnd == 3:  # acmd == 'y':
                        print("人结束\r\n")
                        NeedOpenCV = False
                        print("移除所有棋子：move all\r\n")
                        GoBoard = [([0] * 19) for ii in range(19)]
                        curBoardDif = GetCurBoardDifGoBoard()
                        RobotCommand = curBoardDif  # "move all"  # #############################################################
                        CurBoard = [([0] * 19) for jj in range(19)]
                        BefBoard = [([0] * 19) for kk in range(19)]
                        HumanRunning = False
                        HumanFailed = True
                        NeedOpenCV = False
                        print("openCV执行结束>>>>")
                        BeginPlay = True
                    else:
                        '''
                        print("openCV通过当前棋盘以及befor棋盘，判断人是否走了\r\n")
                        acmd = input("当前棋盘不走棋或者走棋（y or position）:")
                        if acmd == "y":
                            print("人没有走")
                        else:
                            SetCurBoard(3, acmd)
                            printCurBoard()
                            printBefBoard()
                        '''
                        IfGetBoard, CurBoard = myrobotEye.getCurBoard()
                        if IfGetBoard is False:
                            # 没有成功获取棋盘，可能是有胳膊或者其他东西挡着
                            time.sleep(5)
                            continue
                        humanMovePos = GetHumanMove()
                        if humanMovePos != "":

                            GoCommand = "play w " + humanMovePos + "\n"
                            BefBoard = copy.deepcopy(CurBoard)
                            print("go command:{0} ".format(GoCommand))
                            NeedOpenCV = False
                            print("openCV执行结束>>>>")
                        else:
                            print("人没有走，暂停1秒后继续判断")
                            time.sleep(5)
                if HumanEnded:
                    print(">>>>当前状态HumanEnded")
                    IfGetBoard, CurBoard = myrobotEye.getCurBoard()
                    curBoardDifGo = GetCurBoardDifGoBoard()
                    if curBoardDifGo == "":
                        print("棋盘一致，代表人走了，提子也完成了\r\n")
                        NeedOpenCV = False
                        HumanEnded = False
                        NeedOpenCV = False
                        GoRunning = True
                        GoCommand = "genmove b\n"
                        print("openCV执行结束>>>>")
                    elif len(curBoardDifGo) > 30:
                        print("****发现两个棋盘不一致的太多，很可能是不对的，需要重新识别****")
                        print(curBoardDif)
                    else:
                        print("当前棋盘与Go棋盘不一致，意味着人走后没有提子，需要提子；或者有其他情况，导致两个棋盘不一致\r\n")
                        # 生成robot命令，确保两个棋盘一致
                        RobotCommand = curBoardDifGo
                        NeedOpenCV = False
            time.sleep(5)

    def stop(self):
        self.thread_stop = True


class GoThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.thread_stop = False

    def run(self):
        global NeedOpenCV
        global BeginPlay
        global GoCommand
        global RobotCommand
        global GoRunning
        global HumanRunning
        global RobotRunning
        global HumanEnded
        global HumanFailed
        global GoBoard

        while not self.thread_stop:
            
            # Go处理主线程
            if HumanFailed:
                print("Go clear_board\r\n")
                # GoPlay = mygo_bridge.WriteCommand("clear_board\n")
                GoPlay = myGoGameClient.WriteCommand("clear_board\n")
                if(GoPlay.decode().count("=") > 0):
                    print("Go棋盘清空成功\r\n")
                    GoBoard = [([0] * 19) for i in range(19)]
                    printGoBoard()
                HumanFailed = False
            if GoCommand != "":
                print(">>>>Go正在处理\r\n")
                if GoRunning:
                    print("Go走一步:\r\n")
                    print(GoCommand)
                    # GoPlay = mygo_bridge.WriteCommand(GoCommand)
                    GoPlay = myGoGameClient.WriteCommand(GoCommand)
                    GoCommand = ""
                    print("生成Go棋盘，提子后\r\n")
                    pos = GoPlay.decode().replace("= ", "").replace("\n\n", "")
                    SetGoBoard(8, pos)
                    goTizi = DoTiZi(GoBoard)
                    print(">>>>>>>>>>>>>>>>>GoBoard>>>>>>>>>>>")
                    printGoBoard()
                    # print("Robot command：play black " + pos + "\r\n")
                    if goTizi == "":
                        RobotCommand = "play black " + pos
                    else:
                        RobotCommand = "play black " + pos + "," + goTizi
                    print("Go处理完成>>>>\r\n")
                if HumanRunning:
                    print("人走了一步\r\n")
                    print(GoCommand)
                    # GoPlay = mygo_bridge.WriteCommand(GoCommand)
                    GoPlay = myGoGameClient.WriteCommand(GoCommand)
                    if GoPlay.decode().count("=") > 0:
                        print("Go记录人走成功，生成新的Go棋盘，提子后\r\n")
                        pos = GoCommand.split(" ")[2].replace("\r", "")
                        SetGoBoard(3, pos)
                        DoTiZi(GoBoard)
                        printGoBoard()
                    GoCommand = ""
                    HumanRunning = False
                    HumanEnded = True
                    NeedOpenCV = True
                    print("Go处理完成>>>>\r\n")
            time.sleep(1)

    def stop(self):
        self.thread_stop = True


class RobotThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.thread_stop = False

    def run(self):
        global NeedOpenCV
        global RobotCommand

        while not self.thread_stop:
            # 机械臂处理主线程
            if RobotCommand != "":
                '''
                print(">>>>Robot正在处理\r\n")
                print(RobotCommand)
                input("等待robot执行完毕（回车结束）>>>>>>>>>>>")
                print("Robot执行完成>>>>\r\n")
                '''
                my_robot_dispacher.WriteCommand(RobotCommand)

                RobotCommand = ""
                NeedOpenCV = True
            time.sleep(1)

    def stop(self):
        self.thread_stop = True


def printGoBoard():
    global GoBoard
    print("==================printGoBoard")
    for num in range(0, 19):
        rowNum = 19-num
        rownums = "%02d" % rowNum+":" + str(GoBoard[num])
        print(rownums)


def printCurBoard():
    global CurBoard
    print("------------------printCurBoard")
    for num in range(0, 19):
        rowNum = 19 - num
        rownums = "%02d" % rowNum + ":" + str(CurBoard[num])
        print(rownums)


def printBefBoard():
    global BefBoard
    # print("printBefBoard")
    for num in range(0, 19):
        rowNum = 19 - num
        rownums = "%02d" % rowNum + ":" + str(BefBoard[num])
        print(rownums)


def SetGoBoard(clor, position):
    '''
    给当前棋盘设置某个颜色的旗子。测试用的。
    '''
    global GoBoard
    print("set go board pos:{0}".format(position))
    ss = "ABCDEFGHJKLMNOPQRST"
    iCol = ss.find(position[:1])
    iRow = int(position[1:])
    GoBoard[19 - iRow][iCol] = clor


def SetCurBoard(clor, position):
    global CurBoard
    ss = "ABCDEFGHJKLMNOPQRST"
    iCol = ss.find(position[:1])
    iRow = int(position[1:])
    CurBoard[19 - iRow][iCol] = clor

# 比较当前棋盘与之前的棋盘，确定人走的位置；没有变化返回空，有变化返回位置，如Q5。目前按照人走白来获取的。
def GetHumanMove():
    global CurBoard
    global BefBoard
    for row in range(0, 19):
        for col in range(0, 19):
            if(CurBoard[row][col] != BefBoard[row][col]) and CurBoard[row][col] == 3:
                ss = "ABCDEFGHJKLMNOPQRST"
                pos = ss[col]+str(19-row)
                return pos
    return ""


def GetCurBoardDifGoBoard():
    '''
    获取当前棋盘与Go棋盘的不同，并返回robot指令。空则表示两者一致。
    '''
    printGoBoard()
    printCurBoard()
    global CurBoard
    global GoBoard
    difrentPos = ""
    for row in range(0, 19):
        for col in range(0, 19):
            if (CurBoard[row][col] != GoBoard[row][col]):
                ss = "ABCDEFGHJKLMNOPQRST"
                pos = ss[col] + str(19 - row)
                # 根据两个棋盘的情况，生成robot指令。如果当前棋盘有子，就移除；如果go棋盘有子，就放一个。
                if CurBoard[row][col] != 0:
                    # go棋盘没有子，移除当前棋盘的子
                    difrentPos = difrentPos+"move " + pos + ","
                # Go棋盘有子，就放上去
                if GoBoard[row][col] == 3:
                    difrentPos = difrentPos + "play white " + pos + ","
                if GoBoard[row][col] == 8:
                    difrentPos = difrentPos + "play black " + pos + ","
    print("difrentPos:{0}".format(difrentPos))
    return difrentPos


'''
原来的思路，有死循环不用了。
def DoTiZi(KillBoard):
    print("提子处理…………")
    # ==遍历棋盘的每一个格，对每个棋子进行处理
    # ==13、18表示处理过；23、28表示提子
    print("提子处理第一轮>>>>>>>>>>")
    for row in range(0, 19):
        for col in range(0, 19):

            if KillBoard[row][col] == 0:
                # 空的，不做任何处理
                # print("空的，不做任何处理")
                continue
            elif KillBoard[row][col] < 10:
                KillBoard[row][col] = KillBoard[row][col]+10
                if CanKill(KillBoard, row, col):
                    KillBoard[row][col] = KillBoard[row][col] + 10
            else:
                # continue
                # print("该棋子已被处理")
                continue
    # 棋盘处理完成，就需要把所有的kill处理掉，因为上一步的处理，对“块”只标记了一个，这里就是为了把所有块标记为kill。kill标记后，每个位置>30，为33或者38
    print("开始标记kill：>>>>>>>>>>")
    for row in range(0, 19):
        for col in range(0, 19):
            if KillBoard[row][col] > 20 and KillBoard[row][col] < 30:
                # 上一步标记的kill点
                KillBoard[row][col] = KillBoard[row][col]+10
                MakeKillMark(KillBoard, row, col)
    posTions = ""
    # 获取提子位置，并将棋盘复原
    print("开始获取位置并恢复棋盘：>>>>>>>>>>")
    for row in range(0, 19):
        for col in range(0, 19):
            if KillBoard[row][col] > 30:
                ss = "ABCDEFGHJKLMNOPQRST"
                pos = ss[col] + str(19 - row)
                posTions = posTions + pos + ","
                KillBoard[row][col] = 0
            KillBoard[row][col] = KillBoard[row][col] % 10
    return posTions
'''


def DoTiZi(KillBoard):
    print("提子处理…………")
    #  新思路：原始值：3、8 可能死活：13、18 必死：23、28 必活：33、38
    # 提子分四步走：
    # 第一步，对棋盘进行第一轮扫描，标记必死、必活以及不确定。
    # 第二步，对必死以及必活相关联的进行处理。理论上，连接必活的必活；连接必死的必死（不存在）
    # 第三步，对不确定的进行处理（没有必活的联通，必死）
    # 第四步，查找所有必死，返回提子列表
    # print("提子处理第一轮>>>>>>>>>>")
    for row in range(0, 19):
        for col in range(0, 19):

            if KillBoard[row][col] == 0:
                # 空的，不做任何处理
                # print("空的，不做任何处理")
                continue
            elif KillBoard[row][col] < 10:
                DoLiveOrKill(KillBoard, row, col)
            else:
                # continue
                # print("该棋子已被处理")
                continue
    # printGoBoard()
    # print("提子处理第二轮>>>>>>>>>>")
    for row in range(0, 19):
        for col in range(0, 19):

            if KillBoard[row][col] < 20:
                # 不是必死或必活
                continue
            else:
                DoLianQi(KillBoard, row, col)
    # printGoBoard()
    # print("提子处理第三轮>>>>>>>>>>")
    for row in range(0, 19):
        for col in range(0, 19):
            if KillBoard[row][col] > 10 and KillBoard[row][col] < 20:
                # 上一步标记的kill点
                KillBoard[row][col] = KillBoard[row][col] % 10 + 20
    posTions = ""
    # printGoBoard()
    # 获取提子位置，并将棋盘复原
    # print("第四轮开始获取位置并恢复棋盘：>>>>>>>>>>")
    for row in range(0, 19):
        for col in range(0, 19):
            if KillBoard[row][col] > 20 and KillBoard[row][col] < 30:
                ss = "ABCDEFGHJKLMNOPQRST"
                pos = ss[col] + str(19 - row)
                posTions = posTions + "move " + pos + ","
                KillBoard[row][col] = 0
            KillBoard[row][col] = KillBoard[row][col] % 10
    print("提子位置：" + posTions)
    return posTions


def DoLianQi(killBoard, row, col):
    '''
    递归处理，对棋盘进行第二轮扫描。与必死必活连气的也是必死必活。
    '''
    # 只处理未通气并且是自己人的。
    # 上
    if killBoard[row-1][col] < 20 and killBoard[row-1][col] % 10 == killBoard[row][col] % 10:
        if killBoard[row][col] > 30:
            killBoard[row-1][col] = killBoard[row-1][col] % 10 + 30
        else:
            killBoard[row-1][col] = killBoard[row-1][col] % 10 + 20
        DoLianQi(killBoard, row-1, col)
    # 下
    if killBoard[row+1][col] < 20 and killBoard[row+1][col] % 10 == killBoard[row][col] % 10:
        if killBoard[row][col] > 30:
            killBoard[row+1][col] = killBoard[row+1][col] % 10 + 30
        else:
            killBoard[row+1][col] = killBoard[row+1][col] % 10 + 20
        DoLianQi(killBoard, row+1, col)
    # 左
    if killBoard[row][col-1] < 20 and killBoard[row][col-1] % 10 == killBoard[row][col] % 10:
        if killBoard[row][col] > 30:
            killBoard[row][col-1] = killBoard[row][col-1] % 10 + 30
        else:
            killBoard[row][col-1] = killBoard[row][col-1] % 10 + 20
        DoLianQi(killBoard, row, col-1)
    # 右
    if killBoard[row][col+1] < 20 and killBoard[row][col+1] % 10 == killBoard[row][col] % 10:
        if killBoard[row][col] > 30:
            killBoard[row][col+1] = killBoard[row][col+1] % 10 + 30
        else:
            killBoard[row][col+1] = killBoard[row][col+1] % 10 + 20
        DoLianQi(killBoard, row, col-1)


def DoLiveOrKill(killBoard, row, col):
    '''
    递归处理，对棋盘进行第一轮扫描，标记必死、必活以及不确定.
    必死就是上下左右都不是自己人；必活就是上下左右任一位置有空；其他情况为不确定。
    原始值：3、8 可能死活：13、18 必死：23、28 必活：33、38
    '''
    # 默认当前为不确定
    killBoard[row][col] = killBoard[row][col] % 10 + 10
    upNoQi = True
    downNoQi = True
    leftNoQi = True
    rigntNoQi = True
    # 上
    if(row == 0):
        # 到顶了，死的
        upNoQi = True
    elif killBoard[row-1][col] == 0:
        # 空的，必活
        killBoard[row][col] = killBoard[row][col] % 10 + 30
        upNoQi = False
    elif killBoard[row-1][col] % 10 != killBoard[row][col] % 10:
        # 上面的棋子和当前位置不一致，假设能杀
        upNoQi = True
    else:
        upNoQi = False
        # 上面的棋子和当前位置是一样的
        if killBoard[row - 1][col] < 10:
            # 上面还没处理，递归处理
            DoLiveOrKill(killBoard, row - 1, col)
    # 下
    if row == 18:
        # 到底了，死的
        downNoQi = True
    elif killBoard[row+1][col] == 0:
        # 空的，必活
        killBoard[row][col] = killBoard[row][col] % 10 + 30
        downNoQi = False
    elif killBoard[row + 1][col] % 10 != killBoard[row][col] % 10:
        # 下面的棋子和当前位置不一致，能杀;
        downNoQi = True
    else:
        downNoQi = False
        # 下面的棋子和当前位置是一样的
        if killBoard[row + 1][col] < 10:
            # 下面还没处理，递归处理
            DoLiveOrKill(killBoard, row + 1, col)
    # 左
    if (col == 0):
        # 到左了，死的
        leftNoQi = True
    elif killBoard[row][col - 1] == 0:
        # 空的，必活
        killBoard[row][col] = killBoard[row][col] % 10 + 30
        leftNoQi = False
    elif killBoard[row][col - 1] % 10 != killBoard[row][col] % 10:
        # 左面的棋子和当前位置不一致，能杀;
        leftNoQi = True
    else:
        leftNoQi = False
        # 左面的棋子和当前位置是一样的
        if killBoard[row][col - 1] < 10:
            # 左面还没处理，递归处理
            DoLiveOrKill(killBoard, row, col - 1)
    # 右
    if (col == 18):
        # 到右了，死的
        rigntNoQi = True
    elif killBoard[row][col + 1] == 0:
        # 空的，必活
        killBoard[row][col] = killBoard[row][col] % 10 + 30
        rigntNoQi = False
    elif killBoard[row][col + 1] % 10 != killBoard[row][col] % 10:
        # 左面的棋子和当前位置不一致，能杀
        rigntNoQi = True
    else:
        rigntNoQi = False
        if killBoard[row][col + 1] < 10:
            # 左面还没处理，递归处理
            DoLiveOrKill(killBoard, row, col + 1)
    # 四面都是敌人，必死
    if (upNoQi and downNoQi and leftNoQi and rigntNoQi):
        killBoard[row][col] = killBoard[row][col] % 10 + 20


def MakeKillMark(killBoard, row, col):
    '''
    按块对kill棋子进行标记
    '''
    # 同样要上下左右一起处理，采用递归
    if row > 0 and killBoard[row-1][col] < 20 and killBoard[row-1][col] % 10 == killBoard[row][col] % 10:
        killBoard[row - 1][col] = killBoard[row-1][col]+20
        MakeKillMark(killBoard, row-1, col)
    if row < 18 and killBoard[row+1][col] < 20 and killBoard[row+1][col] % 10 == killBoard[row][col] % 10:
        killBoard[row + 1][col] = killBoard[row+1][col]+20
        MakeKillMark(killBoard, row+1, col)
    if col > 0 and killBoard[row][col-1] < 20 and killBoard[row][col-1] % 10 == killBoard[row][col] % 10:
        killBoard[row][col - 1] = killBoard[row][col-1]+20
        MakeKillMark(killBoard, row, col-1)
    if col < 18 and killBoard[row][col+1] < 20 and killBoard[row][col+1] % 10 == killBoard[row][col] % 10:
        killBoard[row][col + 1] = killBoard[row][col+1]+20
        MakeKillMark(killBoard, row, col+1)


def CanKill(killBoard, row, col):
    '''
    递归处理，当前棋子的上下左右都没有位置了，就可以kill，否则就是活的，不能Kill
    '''
    upNoQi = True
    downNoQi = True
    leftNoQi = True
    rigntNoQi = True
    # 上
    if(row == 0):
        # 到顶了，死的
        upNoQi = True
    elif killBoard[row-1][col] == 0:
        # 空的，不能杀
        upNoQi = False
    elif killBoard[row-1][col] % 10 != killBoard[row][col] % 10 or killBoard[row-1][col] == killBoard[row][col]:
        # 上面的棋子和当前位置不一致，能杀;已处理过的，也假设能杀
        upNoQi = True
    else:
        killBoard[row - 1][col] = killBoard[row - 1][col]+10
        upNoQi = CanKill(killBoard, row-1, col)
    # 下
    if row == 18:
        # 到底了，死的
        downNoQi = True
    elif killBoard[row+1][col] == 0:
        # 空的，不能杀
        downNoQi = False
    elif killBoard[row + 1][col] % 10 != killBoard[row][col] % 10 or killBoard[row + 1][col] == killBoard[row][col]:
        # 下面的棋子和当前位置不一致，能杀;已处理过的，也假设能杀
        downNoQi = True
    else:
        killBoard[row + 1][col] = killBoard[row + 1][col] + 10
        downNoQi = CanKill(killBoard, row + 1, col)
    # 左
    if (col == 0):
        # 到左了，死的
        leftNoQi = True
    elif killBoard[row][col - 1] == 0:
        # 空的，不能杀
        leftNoQi = False
    elif killBoard[row][col - 1] % 10 != killBoard[row][col] % 10 or killBoard[row][col - 1] == killBoard[row][col]:
        # 左面的棋子和当前位置不一致，能杀;已处理过的，也假设能杀
        leftNoQi = True
    else:
        killBoard[row][col - 1] = killBoard[row][col - 1] + 10
        leftNoQi = CanKill(killBoard, row, col - 1)
    # 右
    if (col == 18):
        # 到右了，死的
        rigntNoQi = True
    elif killBoard[row][col + 1] == 0:
        # 空的，不能杀
        rigntNoQi = False
    elif killBoard[row][col + 1] % 10 != killBoard[row][col] % 10:
        # 左面的棋子和当前位置不一致，能杀
        rigntNoQi = True
    else:
        killBoard[row][col + 1] = killBoard[row][col + 1] + 10
        rigntNoQi = CanKill(killBoard, row, col + 1)
    return (upNoQi and downNoQi and leftNoQi and rigntNoQi)


def testRun():
    threadOpenCV = OpenCVThread()
    threadGo = GoThread()
    threadRobot = RobotThread()
    threadOpenCV.start()
    threadGo.start()
    threadRobot.start()
    time.sleep(10)
    # threadOpenCV.stop()
    # threadGo.stop()
    # threadRobot.stop()
    return


if __name__ == '__main__':
    '''
    SetGoBoard(8, "D16")
    SetGoBoard(8, "D15")
    SetGoBoard(3, "D14")
    SetGoBoard(3, "C15")
    SetGoBoard(3, "E15")
    SetGoBoard(8, "E14")
    # SetGoBoard(8, "E3")
    # SetGoBoard(8, "D3")
    # SetGoBoard(8, "D5")
    printGoBoard()
    tizi = DoTiZi(GoBoard)
    print(tizi)
    printGoBoard()
    if(myarm_bridge.openSocket()):
        while True:
            acmdd=input("输入发送的Robot命令:")
            myarm_bridge.WriteCommand(acmdd)
    else:
        print("myarm_bridge 打开失败")
    '''
    # >>>>>>>>>board test>>>>>>>>>>>>>>
    '''
    '''
    # print("111111111")
    # ss = "ABCDEFGHJKLMNOPQRST"
    # armCommand = "play black "
    # for le in range(0, 1):
    #     for num in range(1, 2):
    #         sendarmCommand = armCommand + ss[le] + str(num)
    #         print(sendarmCommand)
            # my_robot_dispacher.WriteCommand(sendarmCommand)
    # >>>>>>>>>>play game>>>>>>>>>>>>>>>>>>>>>>>
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>111111111")
    if(myGoGameClient.openSocket()):  # and myarm_bridge.openSocket()
        NeedOpenCV = True
        BeginPlay = True
        testRun()
    else:
        print("myGoGameClient 打开失败")
