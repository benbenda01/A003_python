#####################################################
# 此程序为:mlx05 用手势控制鼠标  单食指鼠标移动 食指和拇指碰撞为单击 长时间捏住为按压鼠标左键的功能
#####################################################
import cv2                                                 # 导入opencv-python库 同时也别忘下载msvc-runtime库文件
import mediapipe as mp                                     # 导入手势识别库
import pyautogui                                           # 导入模拟鼠标和键盘的库
import numpy as np                                         # 导入数组与矩阵运算的库
import time                                                # 导入系统时间处理库
import math                                                # 导入系统数学计算库
##############################
# 手势检测器类定义
class handDetector():                                                   # 定义手势识别的一个类
    def __init__(self, mode: bool = False, maxHands: int = 2, detectionCon: float = 0.8, trackCon: float = 0.8) -> None:  # 手势检测方法
        self.lmList = {'Left': {}, 'Right': {}}                         # 初始化左右手坐标字典
        self.results = None                                             #
        self.mode = mode                                                # 重新定义模式变量
        self.maxHands = maxHands                                        # 重新定义最大手势变量
        self.detectionCon = detectionCon                                # 重新定义检测的时间间隔
        self.trackCon = trackCon                                        # 重新定义变量
        self.hands = None                                               # 初始化hands对象

        self.hands = mp.solutions.hands.Hands()
        self.mpDraw = mp.solutions.drawing_utils                        # 重新定义制图变量
        self.tipIds = [4, 8, 12, 16, 20]                                # 重新定义指尖变量
##############################
    def findHands(self, img: np.ndarray, draw: bool = True) -> np.ndarray:
        """处理图像并识别手势
        Args:
            img: 输入图像矩阵
            draw: 是否绘制手势标记
        Returns:
            处理后的图像矩阵
        """
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        # 三重空值校验解决Pyright类型检查问题
        if self.results is not None \
            and hasattr(self.results, 'multi_hand_landmarks') \
            and self.results.multi_hand_landmarks is not None:

            for handLms in self.results.multi_hand_landmarks:
                if draw and self.mpDraw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                             mp.solutions.hands.HAND_CONNECTIONS)
        return img
##############################
    def findPosition(self, img: np.ndarray, draw: bool = True) -> dict:
        self.lmList = {'Left': {}, 'Right': {}}                         # 左右手字典结构
        if self.results is not None and self.results.multi_hand_landmarks is not None and self.results.multi_handedness is not None:
            for hand_index, hand in enumerate(self.results.multi_handedness or []):
                if not hand.classification or len(hand.classification) == 0:
                    continue
                classification = hand.classification[0]
                if classification.score >= 0.8:
                    hand_type = classification.label
                    hand_landmarks = self.results.multi_hand_landmarks or []
                    if hand_index >= len(hand_landmarks):
                        continue
                    hand_lms = hand_landmarks[hand_index]
                    for id, lm in enumerate(hand_lms.landmark):
                        h, w, c = img.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        self.lmList[hand_type][id] = (cx, cy)
                        if draw:
                            cv2.circle(img, (cx, cy), 12, (255, 0, 255), cv2.FILLED)
        return self.lmList                                              # 返回坐标字典
##############################
    def fingersUp(self) -> list:
        if not self.lmList or not hasattr(self, 'tipIds'):
            return [0]*5  # 确保返回固定长度的列表
        fingers = []                                                    # 大拇指有三节单独处理
        if self.lmList.get('Left') and self.lmList['Left'].get(self.tipIds[0]) and self.lmList['Left'].get(self.tipIds[0]-1):
            thumb_condition = self.lmList['Left'][self.tipIds[0]][1] > self.lmList['Left'][self.tipIds[0] - 1][1]
        elif self.lmList.get('Right') and self.lmList['Right'].get(self.tipIds[0]) and self.lmList['Right'].get(self.tipIds[0]-1):
            thumb_condition = self.lmList['Right'][self.tipIds[0]][1] > self.lmList['Right'][self.tipIds[0] - 1][1]
        else:
            thumb_condition = False
        if thumb_condition:
            fingers.append(1)                                           # 大拇指伸出确认
        else:
            fingers.append(0)                                           # 其余手指有四节合并一起处理
        for id in range(1, 5):                                          # 循环处理剩下4根的每一根手指
            left_hand = self.lmList.get('Left', {})
            finger_check_left = left_hand.get(self.tipIds[id]) and left_hand.get(self.tipIds[id]-2)
            right_hand = self.lmList.get('Right', {})
            finger_check_right = right_hand.get(self.tipIds[id]) and right_hand.get(self.tipIds[id]-2)
            
            if finger_check_left:
                condition = self.lmList['Left'][self.tipIds[id]][1] < self.lmList['Left'][self.tipIds[id]-2][1]
            elif finger_check_right:
                condition = self.lmList['Right'][self.tipIds[id]][1] < self.lmList['Right'][self.tipIds[id]-2][1]
            else:
                condition = False
            if condition:
                fingers.append(1)                                       # 确认手指伸出
            else:                                                       # 否则
                fingers.append(0)                                       # 手指没有伸出
        return fingers                                                  # 手指伸出信息返回
##############################
    def findDistance(self, p1: int, p2: int, img, draw: bool = True, r: int = 15, t: int = 3):
        x1, y1 = self.lmList['Left'][p1] if 'Left' in self.lmList else self.lmList['Right'][p1]                                    # 获得食指坐标
        x2, y2 = self.lmList['Left'][p2] if 'Left' in self.lmList else self.lmList['Right'][p2]                                    # 获得中指坐标
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2                         # 获得食指和中指中间点坐标
        length = math.hypot(x2 - x1, y2 - y1)                       # 计算中指和食指距离
        if draw:                                                        # 如果允许处理图像
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)         # 连线中指和食指
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)     # 食指上画粉红色圆点
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)     # 中指上画粉红色圆点
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)       # 鼠标单击点上画绿色圆点
        return length, img, [x1, y1, x2, y2, cx, cy]                    # 返回距离数据,和处理后图像信息

##############################
# 获取屏幕分辨率，适配全屏
screen_width, screen_height = pyautogui.size()                          # 获得电脑屏幕的宽和高
wCam, hCam = screen_width, screen_height                               # 设置捕捉框为全屏
smoothening = 5                                                         # 降低平滑系数，提高响应速度，同时保持一定的平稳性
detectionConfidence = 0.8                                              # 手势检测置信度
clickDistance = 30                                                      # 点击距离阈值
pressThreshold = 1.0                                                    # 长按阈值时间（秒）
##############################
cap = cv2.VideoCapture(0)                                               # 若使用笔记本自带摄像头则编号为0  若使用外接摄像头 则更改为1或其他编号
cap.set(3, wCam)                                                        # 设定捕捉框的宽度
cap.set(4, hCam)                                                        # 设定捕捉框的高度
pTime = 0                                                               # 设置第一帧开始处理的起始时间
plocX, plocY = 0, 0                                                     # 前一帧的鼠标所在位置坐标xy值
clocX, clocY = 0, 0                                                     # 下一帧的鼠标所在位置坐标xy值
detector = handDetector(detectionCon=detectionConfidence)               # 创建手势检测器实例
##############################
# 创建使用说明和参数显示函数
def draw_instructions(img):
    # 设置右下角信息区域背景
    h, w, c = img.shape
    cv2.rectangle(img, (w-300, h-200), (w-10, h-10), (0, 0, 0), cv2.FILLED)  # 黑色背景
    cv2.rectangle(img, (w-300, h-200), (w-10, h-10), (255, 255, 255), 2)     # 白色边框
    
    # 添加使用说明
    cv2.putText(img, "使用说明:", (w-290, h-170), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(img, "1. 食指竖起: 移动鼠标", (w-290, h-140), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    cv2.putText(img, "2. 食指+拇指捏合: 单击", (w-290, h-120), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    cv2.putText(img, "3. 食指+拇指长时间捏合: 按住左键", (w-290, h-100), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    cv2.putText(img, "4. 按'q'键退出", (w-290, h-80), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    
    # 添加关键参数
    cv2.putText(img, "关键参数:", (w-290, h-50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(img, f"FPS: {int(fps)}", (w-290, h-30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)
    cv2.putText(img, f"检测置信度: {detectionConfidence}", (w-200, h-30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)
    cv2.putText(img, f"点击距离: {clickDistance}px", (w-290, h-15), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)
    cv2.putText(img, f"长按阈值: {pressThreshold}秒", (w-200, h-15), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)
    
    return img
##############################
# 初始化长按相关变量
pinch_start_time = 0                                                  # 捏合开始时间
is_pressing = False                                                   # 是否正在按压鼠标

##############################
while True:                                                        # 1. 循环检测手部 得到手指关键点坐标
    success, img = cap.read()                                           # 图片是否成功接收帧图像img
    if not success:
        print("无法获取摄像头画面")
        continue
        
    img = cv2.flip(img, 1)                                             # 水平翻转图像，解决镜像问题
    img = detector.findHands(img)                                       # 获得画面中手势数据
    lmList = detector.findPosition(img, draw=False)                     # 传入每帧图像, 返回手部关键点的坐标信息(字典构成的列表hands)
    
    # 初始化fingers变量，避免未定义错误
    fingers = [0, 0, 0, 0, 0]  # 默认所有手指都是弯曲状态
##############################
    if len(lmList) != 0:                                           # 2. 如果采集到到手势关键点
        # 检查左手或右手是否存在，以及食指关键点(8)是否存在
        has_left_index = 'Left' in lmList and 8 in lmList['Left']
        has_right_index = 'Right' in lmList and 8 in lmList['Right']
        has_left_thumb = 'Left' in lmList and 4 in lmList['Left']
        has_right_thumb = 'Right' in lmList and 4 in lmList['Right']
        
        # 只有当至少有一只手的食指和拇指都被检测到时才继续
        if (has_left_index and has_left_thumb) or (has_right_index and has_right_thumb):
            x1, y1 = lmList['Left'][8] if has_left_index else lmList['Right'][8]    # 获取食指坐标
            x2, y2 = lmList['Left'][4] if has_left_thumb else lmList['Right'][4]    # 获取拇指坐标
##############################
            fingers = detector.fingersUp()                             # 3. 检测五个手指是竖起方法,返回值为[0,1,1,0,0]1该手指竖起,0该手指弯下
##############################
            if fingers[1] and fingers[0] == False:                     # 4. 如果食指竖起但拇指没有竖起
                # 如果之前在按压鼠标，现在松开了捏合姿势，释放鼠标
                if is_pressing:
                    pyautogui.mouseUp()
                    is_pressing = False
                
            # 由于已经翻转了图像，坐标映射不需要再做额外处理
            x3 = np.interp(x1, (0, wCam), (0, screen_width))             # 将食指x坐标映射到屏幕宽度范围
            y3 = np.interp(y1, (0, hCam), (0, screen_height))            # 将食指y坐标映射到屏幕高度范围
            # 添加边界检查，确保鼠标不会超出屏幕范围
            x3 = max(0, min(screen_width - 1, x3))
            y3 = max(0, min(screen_height - 1, y3))
            clocX = plocX + (x3 - plocX) / smoothening                   # 使手指在移动鼠标时,鼠标箭头x不会一直晃动
            clocY = plocY + (y3 - plocY) / smoothening                   # 使手指在移动鼠标时,鼠标箭头y不会一直晃动
            pyautogui.moveTo(clocX, clocY)                              # 给出鼠标移动位置坐标
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)     # 给食指之间画个粉红色移动追踪点
            plocX, plocY = clocX, clocY                                  # 更新鼠标所在位置，将当前帧鼠标位置，变成下一帧鼠标位置
##############################
        if fingers[1] and fingers[0] and ((has_left_index and has_left_thumb) or (has_right_index and has_right_thumb)):                                 # 5. 如果食指和拇指同时竖起
            length, img, pointInfo = detector.findDistance(8, 4, img)   # 计算食指尖和拇指尖间的距离
            if length < clickDistance:                                   # 且食指尖和拇指尖距离小于设定阈值
                cv2.circle(img, (pointInfo[4], pointInfo[5]), 15, (0, 255, 0), cv2.FILLED)   # 食指尖和拇指尖画绿色圆
                
                # 长按功能实现
                current_time = time.time()
                if not is_pressing:
                    # 如果是新的捏合动作，记录开始时间
                    if pinch_start_time == 0:
                        pinch_start_time = current_time
                    
                    # 检查是否达到长按阈值
                    if current_time - pinch_start_time >= pressThreshold:
                        # 达到长按阈值，按下鼠标左键
                        pyautogui.mouseDown()
                        is_pressing = True
                        # 在图像上显示长按状态
                        cv2.putText(img, "长按中", (pointInfo[4]-50, pointInfo[5]-20), 
                                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
                    else:
                        # 未达到长按阈值，显示单击
                        pyautogui.click()
                        # 在图像上显示单击状态
                        cv2.putText(img, "单击", (pointInfo[4]-30, pointInfo[5]-20), 
                                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
            else:
                # 如果手指分开，重置捏合开始时间
                pinch_start_time = 0
                # 如果之前在按压鼠标，现在松开了捏合姿势，释放鼠标
                if is_pressing:
                    pyautogui.mouseUp()
                    is_pressing = False
    cTime = time.time()                                                  # 处理完一帧图像的时间
    fps = 1 / (cTime - pTime)                                            # 计算1秒内处理的帧个数
    pTime = cTime                                                        # 重置起始时间
    
    # 在左上角显示FPS
    cv2.putText(img, f'FPS: {int(fps)}', (15, 25), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)  # 文本显示fps信息
    
    # 添加使用说明和参数显示
    img = draw_instructions(img)
    
    # 全屏显示
    cv2.namedWindow("手势控制鼠标", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("手势控制鼠标", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("手势控制鼠标", img)                                      # 显示图像,输入窗口名及图像数据
##############################
    k = cv2.waitKey(1)                                                   # 检测键位是否按下
    if k == ord('q'):                                                    # 如果是键位Q键按下
        break                                                            # 退出循环
cap.release()                                                            # 退出摄像头
cv2.destroyAllWindows()                                                  # 关闭所有视窗
