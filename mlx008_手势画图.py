#####################################################
# 此程序为:mlx008 手势绘画程序
#####################################################

import cv2
import os
import numpy as np
import mediapipe as mp
import math
from PIL import Image, ImageDraw, ImageFont

# 手势检测类
class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.8, trackCon=0.8):
        self.lmList = []
        self.results = None
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.hands = None

        self.hands = mp.solutions.hands.Hands()
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
        """检测哪些手指伸出"""
        fingers = []
        if len(self.lmList) == 0:
            return [0, 0, 0, 0, 0]
            
        # 大拇指检测（水平方向）
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0]-1][1]:
            fingers.append(1)  # 大拇指伸出
        else:
            fingers.append(0)  # 大拇指弯曲
            
        # 其他四个手指检测（垂直方向）
        for id in range(1, 5):
            # 如果手指指尖y坐标小于该手指第二关节y坐标（因为y轴向下，所以小于表示指尖在上方）
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id]-2][2]:
                fingers.append(1)  # 手指伸出
            else:
                fingers.append(0)  # 手指弯曲
                
        return fingers

# 主程序
folderPath = "PainterImg/"
overlayList = []

# 创建颜色选择界面
header_height = 153
header_width = 1280
header = np.ones((header_height, header_width, 3), np.uint8) * 255

# 定义一个函数用于绘制中文文本
def draw_chinese_text(img, text, position, text_color=(0, 0, 0), text_size=30):
    # 创建一个空白的PIL图像，设置透明背景
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    # 加载一个支持中文的字体
    fontpath = os.path.join(os.environ.get('WINDIR', 'C:\Windows'), 'Fonts', 'simhei.ttf')
    font = ImageFont.truetype(fontpath, text_size)
    
    # 在图像上绘制文本
    draw.text(position, text, font=font, fill=text_color)
    
    # 转换回OpenCV格式
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

# 绘制蓝色选择区域
blue_section = np.ones((header_height, 320, 3), np.uint8) * 255
cv2.circle(blue_section, (160, 76), 40, (255, 128, 50), -1)  # 蓝色圆形
blue_section = draw_chinese_text(blue_section, "蓝色", (130, 110))

# 绘制红色选择区域
red_section = np.ones((header_height, 320, 3), np.uint8) * 255
cv2.circle(red_section, (160, 76), 40, (0, 0, 255), -1)  # 红色圆形
red_section = draw_chinese_text(red_section, "红色", (130, 110))

# 绘制绿色选择区域
green_section = np.ones((header_height, 320, 3), np.uint8) * 255
cv2.circle(green_section, (160, 76), 40, (0, 255, 0), -1)  # 绿色圆形
green_section = draw_chinese_text(green_section, "绿色", (130, 110))

# 绘制橡皮擦选择区域
eraser_section = np.ones((header_height, 320, 3), np.uint8) * 255
cv2.circle(eraser_section, (160, 76), 40, (0, 0, 0), -1)  # 黑色圆形
eraser_section = draw_chinese_text(eraser_section, "橡皮擦", (115, 110))

# 将四个区域合并到header中
header[0:header_height, 0:320] = blue_section
header[0:header_height, 320:640] = red_section
header[0:header_height, 640:960] = green_section
header[0:header_height, 960:1280] = eraser_section

# 将header添加到overlayList
overlayList.append(header.copy())  # 蓝色选择界面
overlayList.append(header.copy())  # 红色选择界面
overlayList.append(header.copy())  # 绿色选择界面
overlayList.append(header.copy())  # 橡皮擦选择界面
color = [255, 0, 0]                                 # 蓝色设定
brushThickness = 15                                 # 画笔宽度
eraserThickness = 40                                # 橡皮宽度

cap = cv2.VideoCapture(0)                           # 若使用笔记本自带摄像头则编号为0  若使用外接摄像头 则更改为1或其他编号
cap.set(3, 1280)                                    # 将系统分辨率画面捕捉框设置1300 和700的捕获框
cap.set(4, 720)

detector = handDetector()                       # 调用手势检测函数
xp, yp = 0, 0                                       #
imgCanvas = np.zeros((720, 1280, 3), np.uint8)      # 新建一个画布

while True:                                     # 1.import image
    success, img = cap.read()                       # 图片是否成功读入帧图像img
    img = cv2.flip(img, 1)                          # 翻转图像中的自己 1代表水平,0代表垂直翻转

    img = detector.findHands(img)               # 2.find hand landmarks
    lmList = detector.findPosition(img, draw=True)

    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        fingers = detector.fingersUp()          # 3. Check which fingers are up

        if fingers[1] and fingers[2]:           # 4. If Selection Mode – Two finger are up
            if y1 < 153:
                if 0 < x1 < 320:
                    header = overlayList[0]
                    color = [50, 128, 250]
                elif 320 < x1 < 640:
                    header = overlayList[1]
                    color = [0, 0, 255]
                elif 640 < x1 < 960:
                    header = overlayList[2]
                    color = [0, 255, 0]
                elif 960 < x1 < 1280:
                    header = overlayList[3]
                    color = [0, 0, 0]
            img[0:153, 0:1280] = header

        if fingers[1] and fingers[2] == False:    # 5. If Drawing Mode – Index finger is up
            cv2.circle(img, (x1, y1), 15, color, cv2.FILLED)
            print("Drawing Mode")
            if xp == 0 and yp == 0:
                xp, yp = x1, y1

            if color == [0, 0, 0]:
                cv2.line(img, (xp, yp), (x1, y1), color, eraserThickness)  # 橡皮擦
                cv2.line(imgCanvas, (xp, yp), (x1, y1), color, eraserThickness)
            else:
                cv2.line(img, (xp, yp), (x1, y1), color, brushThickness)   # 画笔
                cv2.line(imgCanvas, (xp, yp), (x1, y1), color, brushThickness)

        xp, yp = x1, y1
        # Clear Canvas when all fingers are up
        # if all (x >= 1 for x in fingers):
        #     imgCanvas = np.zeros((720, 1280, 3), np.uint8)
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)      # 实时显示画笔轨迹实现
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)
    
    # 确保header存在再赋值
    if header is not None and header.shape[0] <= img.shape[0] and header.shape[1] <= img.shape[1]:
        img[0:header.shape[0], 0:header.shape[1]] = header

    cv2.imshow("手势绘画", img)
    # cv2.imshow("Canvas", imgCanvas)
    # cv2.imshow("Inv", imgInv)
    k = cv2.waitKey(1)                      # 检测位是否按下
    if k == ord('q'):                       # 如果是键位Q键按下
        break                               # 退出循环
cap.release()                               # 退出摄像头
cv2.destroyAllWindows()                     # 关闭所有窗口