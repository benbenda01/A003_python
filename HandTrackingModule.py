#####################################################
# 此程序为:手势库文件 用于mlx06 mlx07 mlx08 mlx09 文件运行的库调用
#####################################################
import cv2                                                              # 导入opencv-python库 同时也别忘下载msvc-runtime库文件
import mediapipe as mp                                                  # 导入手势识别库
import time                                                             # 导入系统时间处理库
import math                                                             # 导入系统数学计算库
##############################
class handDetector():                                                   # 定义手势识别的一个类
    def __init__(self, mode=False, maxHands=2, model_complexity=1, detectionCon=0.8, trackCon=0.8):  # 手势检测方法
        self.lmList = None                                              # 手势库的字典数据
        self.results = None                                             #
        self.mode = mode                                                # 重新定义模式变量
        self.maxHands = maxHands                                        # 重新定义最大手势变量
        self.model_complexity = model_complexity                        # 重新定义变量
        self.detectionCon = detectionCon                                # 重新定义检测的时间间隔
        self.trackCon = trackCon                                        # 重新定义变量

        self.mpHands = mp.solutions.hands                               # 重新定义手势方案变量

        self.hands = self.mpHands.Hands(self.mode, self.maxHands,self.model_complexity, self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils                        # 重新定义制图变量
        self.tipIds = [4, 8, 12, 16, 20]                                # 重新定义指尖变量
##############################
    def findHands(self, img, draw=True):                                # 查找手势
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)                   # 将获取的图像从BGR灰阶处理为RGB数据
        self.results = self.hands.process(imgRGB)                       # 将图像数据结果保存
        print(self.results.multi_handedness)                            # 获取检测结果中的左右手标签并打印
        if self.results.multi_hand_landmarks:                           # 获得所有手势数据
            for handLms in self.results.multi_hand_landmarks:           # 查找手势的位置字典
                if draw:                                                # 如果有画图数据
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)   # 连接手势的关键点为直线
        return img                                                      # 返回处理后图像数据
##############################
    def findPosition(self, img, draw=True):                             # 建立一个手势位置查找类
        self.lmList = []                                                # 获取手势字典
        if self.results.multi_hand_landmarks:                           # 查找手势的关键点
            for handLms in self.results.multi_hand_landmarks:           # 循环处理所有的手势关键点
                for id, lm in enumerate(handLms.landmark):              # 循环标注每个关键点的位置
                    h, w, c = img.shape                                 # 获取高宽长数据
                    cx, cy = int(lm.x * w), int(lm.y * h)               # 获取显示框的长度和高度
                    self.lmList.append([id, cx, cy])                    # 查找每个关键点
                    if draw:                                            # 获取显示框的长度和高度
                        cv2.circle(img, (cx, cy), 12, (255, 0, 255), cv2.FILLED)   # 对每个指关节都做圆点标记
        return self.lmList                                              # 返回关键点标注数据
##############################
    def fingersUp(self):                                                # 建立一个手指伸出方法
        fingers = []                                                    # 大拇指有三节单独处理
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)                                           # 大拇指伸出确认
        else:
            fingers.append(0)                                           # 其余手指有四节合并一起处理
        for id in range(1, 5):                                          # 循环处理剩下4根的每一根手指
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)                                       # 确认手指伸出
            else:                                                       # 否则
                fingers.append(0)                                       # 手指没有伸出
        return fingers                                                  # 手指伸出信息返回
##############################
    def findDistance(self, p1, p2, img, draw=True, r=15, t=3):          # 计算长度
        x1, y1 = self.lmList[p1][1:]                                    # 获得食指坐标
        x2, y2 = self.lmList[p2][1:]                                    # 获得中指坐标
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2                         # 获得食指和中指中间点坐标
        length = math.hypot(x2 - x1, y2 - y1)                       # 计算中指和食指距离
        if draw:                                                        # 如果允许处理图像
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)         # 连线中指和食指
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)     # 食指上画粉红色圆点
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)     # 中指上画粉红色圆点
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)       # 鼠标单击点上画绿色圆点
        return length, img, [x1, y1, x2, y2, cx, cy]                    # 返回距离数据,和处理后图像信息
