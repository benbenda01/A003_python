#####################################################
# 此程序为:mlx006 手指个数识别程序
#####################################################
import cv2                                                 # 导入opencv-python库 同时也别忘下载msvc-runtime库文件
import numpy as np                                         # 导入数组与矩阵运算的库
import mediapipe as mp                                     # 导入手势识别库
import time                                                # 导入系统时间处理库
import os                                                  # 导入操作系统功能库

#############################
# 手势检测类
#############################
class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.8, trackCon=0.8):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.results = None
        self.lmList = []
        self.previousFingers = [0, 0, 0, 0, 0]  # 用于平滑处理的上一帧手指状态
        self.fingerHistory = []  # 存储最近几帧的手指状态
        self.historyLength = 3  # 历史记录长度
        
       # 初始化mediapipe手部检测
        self.hands = mp.solutions.hands.Hands(min_detection_confidence=detectionCon, min_tracking_confidence=trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]  # 指尖ID列表
    
    def findHands(self, img, draw=True):
        """处理图像并识别手势"""
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        
        # 检测到手部时绘制标记
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, mp.solutions.hands.HAND_CONNECTIONS)
        return img
    
    def findPosition(self, img, draw=False):
        """获取手部关键点位置"""
        self.lmList = []
        if self.results.multi_hand_landmarks:
            # 使用第一只检测到的手
            myHand = self.results.multi_hand_landmarks[0]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 7, (255, 0, 255), cv2.FILLED)
        return self.lmList
        
    def fingersUp(self):
        """检测哪些手指伸出，并进行平滑处理"""
        fingers = []
        if len(self.lmList) == 0:
            return self.previousFingers  # 如果没有检测到手，返回上一帧的状态
            
        # 大拇指检测（水平方向）- 改进检测逻辑
        # 使用大拇指指尖与第一关节和指根形成的角度来判断
        thumb_tip = self.lmList[self.tipIds[0]]  # 大拇指指尖
        thumb_ip = self.lmList[self.tipIds[0]-1]  # 大拇指第二关节
        thumb_mcp = self.lmList[self.tipIds[0]-2]  # 大拇指指根
        
        # 计算大拇指弯曲的角度
        # 如果大拇指指尖x坐标明显大于第二关节x坐标，则认为大拇指伸出
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0]-1][1] + 20:  # 添加阈值
            fingers.append(1)  # 大拇指伸出
        else:
            fingers.append(0)  # 大拇指弯曲
            
        # 其他四个手指检测（垂直方向）- 改进检测逻辑
        for id in range(1, 5):
            # 使用更大的阈值来判断手指是否伸出
            # 如果手指指尖y坐标小于该手指第二关节y坐标一定阈值，则认为手指伸出
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id]-2][2] - 15:  # 添加阈值
                fingers.append(1)  # 手指伸出
            else:
                fingers.append(0)  # 手指弯曲
        
        # 平滑处理：将当前检测结果添加到历史记录中
        self.fingerHistory.append(fingers)
        if len(self.fingerHistory) > self.historyLength:
            self.fingerHistory.pop(0)  # 保持历史记录长度
        
        # 对历史记录进行投票，确定最终的手指状态
        smoothedFingers = []
        for i in range(5):  # 对每个手指
            # 计算历史记录中该手指伸出状态的次数
            count = sum(frame[i] for frame in self.fingerHistory)
            # 如果大多数帧中该手指是伸出的，则认为该手指伸出
            if count > len(self.fingerHistory) / 2:
                smoothedFingers.append(1)
            else:
                smoothedFingers.append(0)
        
        self.previousFingers = smoothedFingers  # 更新上一帧的状态
        return smoothedFingers

##############################
wCam, hCam = 1280, 720                                     # 设置摄像头捕捉画面的宽度和高度
##############################
cap = cv2.VideoCapture(0)                                  # 若使用笔记本自带摄像头则编号为0  若使用外接摄像头 则更改为1或其他编号
cap.set(3, wCam)                                           # 设定捕捉框的宽度
cap.set(4, hCam)                                           # 设定捕捉框的高度

# 导入手指图片
folderPath = "FingerImg"                                   # 设置手指图片文件夹路径
if not os.path.exists(folderPath):                         # 检查文件夹是否存在
    os.makedirs(folderPath)                                # 如果不存在则创建

fingerImgList = os.listdir(folderPath)                     # 获取文件夹中的所有文件
fingerImgList.sort()                                       # 对文件名进行排序

# 加载所有手指图片
overLayList = []
for imgPath in fingerImgList:
    image = cv2.imread(f'{folderPath}/{imgPath}')          # 读取图片
    if image is not None:                                  # 确保图片成功加载
        overLayList.append(image)                          # 将图片添加到列表中

pTime = 0                                                  # 设置第一帧开始处理的起始时间
detector = handDetector(detectionCon=0.75)                 # 创建手势检测器实例，设置检测置信度为0.75

# 指尖ID列表，分别对应大拇指、食指、中指、无名指和小指的指尖
tipIds = [4, 8, 12, 16, 20]                                

while True:
    success, img = cap.read()                              # 读取摄像头画面
    if not success:
        print("无法获取摄像头画面")
        break
    
    img = cv2.flip(img, 1)                                  # 水平翻转图像，使其更符合用户直觉
        
    img = detector.findHands(img)                          # 检测手部并在图像上绘制手部关键点
    lmList = detector.findPosition(img, draw=False)         # 获取手部关键点位置，但不在图像上绘制
    
    if len(lmList) != 0:                                   # 如果检测到手部关键点
        # 使用改进的fingersUp方法检测手指状态
        fingers = detector.fingersUp()
                
        # 计算伸出的手指数量
        totalFingers = fingers.count(1)
        print(f"手指状态: {fingers}, 伸出手指数: {totalFingers}")  # 打印更详细的信息
        
        # 在图像上显示对应的手指图片
        if 0 <= totalFingers < len(overLayList):
            h, w, c = overLayList[totalFingers].shape
            img[0:h, 0:w] = overLayList[totalFingers]       # 在图像左上角显示对应的手指图片
            
        # 在图像上显示伸出的手指数量
        cv2.rectangle(img, (20, 225), (170, 425), (0, 255, 0), cv2.FILLED)  # 绘制绿色矩形
        cv2.putText(img, str(totalFingers), (45, 375), cv2.FONT_HERSHEY_PLAIN, 10, (255, 0, 0), 25)  # 显示手指数量
    
    # 计算并显示FPS
    cTime = time.time()                                     # 获取当前时间
    fps = 1 / (cTime - pTime)                               # 计算FPS
    pTime = cTime                                           # 更新上一帧时间
    
    cv2.putText(img, f'FPS: {int(fps)}', (400, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)  # 显示FPS
    
    cv2.imshow("手势识别", img)                              # 显示处理后的图像
    
    # 按下'q'键退出程序
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()                                               # 释放摄像头
cv2.destroyAllWindows()                                     # 关闭所有窗口