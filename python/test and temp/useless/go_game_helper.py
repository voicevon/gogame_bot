#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('/home/xm/gitrepo/ros_marlin_bridge/go_gameboard')
from chessboard import ChessboardLayout


class GoGameHelper_useless():

    def __init__(self):
        pass

    def DoTiZi(self, KillBoard):

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
                # if KillBoard.get_cell_color(col,row) == 0:
                if KillBoard.get_cell_color(col,row) == 0:
                    # 空的，不做任何处理
                    # print("空的，不做任何处理")
                    continue
                elif KillBoard.get_cell_color(col,row) < 10:
                    self.DoLiveOrKill(KillBoard, row, col)
                else:
                    # continue
                    # print("该棋子已被处理")
                    continue
        # printGoBoard()
        # print("提子处理第二轮>>>>>>>>>>")
        for row in range(0, 19):
            for col in range(0, 19):

                if KillBoard.get_cell_color(col,row) < 20:
                    # 不是必死或必活
                    continue
                else:
                    self.DoLianQi(KillBoard, row, col)
        # printGoBoard()
        # print("提子处理第三轮>>>>>>>>>>")
        for row in range(0, 19):
            for col in range(0, 19):
                if KillBoard.get_cell_color(col,row) > 10 and KillBoard.get_cell_color(col,row) < 20:
                    # 上一步标记的kill点
                    value = KillBoard.get_cell_color(col,row) % 10 + 20
                    KillBoard.set_cell_value(col,row,value)
        posTions = ""
        # printGoBoard()
        # 获取提子位置，并将棋盘复原
        # print("第四轮开始获取位置并恢复棋盘：>>>>>>>>>>")
        for row in range(0, 19):
            for col in range(0, 19):
                if KillBoard.get_cell_color(col,row) > 20 and KillBoard.get_cell_color(col,row) < 30:
                    ss = "ABCDEFGHJKLMNOPQRST"
                    pos = ss[col] + str(19 - row)
                    posTions = posTions + "move " + pos + ","
                    KillBoard.set_cell_value(col,row, 0)
                value = KillBoard.get_cell_color(col,row) % 10
                KillBoard.set_cell_value(col, row, value)
        print("提子位置：" + posTions)
        return posTions

    def DoLiveOrKill(self, killBoard, row, col):
        '''
        递归处理，对棋盘进行第一轮扫描，标记必死、必活以及不确定.
        必死就是上下左右都不是自己人；必活就是上下左右任一位置有空；其他情况为不确定。
        原始值：3、8 可能死活：13、18 必死：23、28 必活：33、38
        '''
        # 默认当前为不确定
        value = killBoard.get_cell_color(col,row) % 10 + 10
        killBoard.set_cell_value(col,row,value)
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
            value = killBoard.get_cell_color(col,row) % 10 + 30
            killBoard.set_cell_value(col,row,value)
            upNoQi = False
        elif killBoard[row-1][col] % 10 != killBoard.get_cell_color(col,row) % 10:
            # 上面的棋子和当前位置不一致，假设能杀
            upNoQi = True
        else:
            upNoQi = False
            # 上面的棋子和当前位置是一样的
            if killBoard[row - 1][col] < 10:
                # 上面还没处理，递归处理
                self.DoLiveOrKill(killBoard, row - 1, col)
        # 下
        if row == 18:
            # 到底了，死的
            downNoQi = True
        elif killBoard[row+1][col] == 0:
            # 空的，必活
            value =  killBoard.get_cell_color(col,row) % 10 + 30
            killBoard.set_cell_value(col, row, value)
            downNoQi = False
        elif killBoard[row + 1][col] % 10 != killBoard.get_cell_color(col,row) % 10:
            # 下面的棋子和当前位置不一致，能杀;
            downNoQi = True
        else:
            downNoQi = False
            # 下面的棋子和当前位置是一样的
            if killBoard[row + 1][col] < 10:
                # 下面还没处理，递归处理
                self.DoLiveOrKill(killBoard, row + 1, col)
        # 左
        if (col == 0):
            # 到左了，死的
            leftNoQi = True
        elif killBoard[row][col - 1] == 0:
            # 空的，必活
            value =  killBoard.get_cell_color(col,row) % 10 + 30
            killBoard.set_cell_value(col, row, value)
            leftNoQi = False
        elif killBoard[row][col - 1] % 10 != killBoard.get_cell_color(col,row) % 10:
            # 左面的棋子和当前位置不一致，能杀;
            leftNoQi = True
        else:
            leftNoQi = False
            # 左面的棋子和当前位置是一样的
            if killBoard[row][col - 1] < 10:
                # 左面还没处理，递归处理
                self.DoLiveOrKill(killBoard, row, col - 1)
        # 右
        if (col == 18):
            # 到右了，死的
            rigntNoQi = True
        elif killBoard[row][col + 1] == 0:
            # 空的，必活
            value = killBoard.get_cell_color(col,row) % 10 + 30
            killBoard.set_cell_value(col, row, value)
            rigntNoQi = False
        elif killBoard[row][col + 1] % 10 != killBoard.get_cell_color(col,row) % 10:
            # 左面的棋子和当前位置不一致，能杀
            rigntNoQi = True
        else:
            rigntNoQi = False
            if killBoard[row][col + 1] < 10:
                # 左面还没处理，递归处理
                self.DoLiveOrKill(killBoard, row, col + 1)
        # 四面都是敌人，必死
        if (upNoQi and downNoQi and leftNoQi and rigntNoQi):
            value = killBoard.get_cell_color(col,row) % 10 + 20
            killBoard.set_cell_value(col, row, value)

    def DoLianQi(self, killBoard, row, col):
        '''
        递归处理，对棋盘进行第二轮扫描。与必死必活连气的也是必死必活。
        '''
        # 只处理未通气并且是自己人的。
        # 上
        if killBoard[row-1][col] < 20 and killBoard[row-1][col] % 10 == killBoard.get_cell_color(col,row) % 10:
            if killBoard.get_cell_color(col,row) > 30:
                killBoard[row-1][col] = killBoard[row-1][col] % 10 + 30
            else:
                killBoard[row-1][col] = killBoard[row-1][col] % 10 + 20
            self.DoLianQi(killBoard, row-1, col)
        # 下
        if killBoard[row+1][col] < 20 and killBoard[row+1][col] % 10 == killBoard.get_cell_color(col,row) % 10:
            if killBoard.get_cell_color(col,row) > 30:
                killBoard[row+1][col] = killBoard[row+1][col] % 10 + 30
            else:
                killBoard[row+1][col] = killBoard[row+1][col] % 10 + 20
            self.DoLianQi(killBoard, row+1, col)
        # 左
        if killBoard[row][col-1] < 20 and killBoard[row][col-1] % 10 == killBoard.get_cell_color(col,row) % 10:
            if killBoard.get_cell_color(col,row) > 30:
                killBoard[row][col-1] = killBoard[row][col-1] % 10 + 30
            else:
                killBoard[row][col-1] = killBoard[row][col-1] % 10 + 20
            self.DoLianQi(killBoard, row, col-1)
        # 右
        if killBoard[row][col+1] < 20 and killBoard[row][col+1] % 10 == killBoard.get_cell_color(col,row) % 10:
            if killBoard.get_cell_color(col,row) > 30:
                killBoard[row][col+1] = killBoard[row][col+1] % 10 + 30
            else:
                killBoard[row][col+1] = killBoard[row][col+1] % 10 + 20
            self.DoLianQi(killBoard, row, col-1)



if __name__ == "__main__":
    x = GoGameHelper()
    bb = ChessboardLayout('test')
    x.DoTiZi(bb)