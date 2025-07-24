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

        self.hands = mp.solutions.hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
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

# 创建优化的颜色选择界面
header_height = 120
header_width = 1280
header = np.ones((header_height, header_width, 3), np.uint8) * 240  # 浅灰色背景

# 定义一个函数用于绘制中文文本
def draw_chinese_text(img, text, position, text_color=(0, 0, 0), text_size=24):
    # 创建一个空白的PIL图像，设置透明背景
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    # 加载一个支持中文的字体
    try:
        # Windows系统字体路径
        if os.name == 'nt':  # Windows
            fontpath = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'simhei.ttf')
            if not os.path.exists(fontpath):
                fontpath = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'msyh.ttf')
        else:  # Linux/Mac
            fontpath = '/System/Library/Fonts/Arial.ttf'  # 使用默认字体
        
        if os.path.exists(fontpath):
            font = ImageFont.truetype(fontpath, text_size)
        else:
            font = ImageFont.load_default()
    except Exception as e:
        print(f"Font loading error: {e}")
        font = ImageFont.load_default()
    
    # 在图像上绘制文本
    draw.text(position, text, font=font, fill=text_color)
    
    # 转换回OpenCV格式
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

# 创建美化的工具栏
def create_tool_section(color_bgr, text, text_color=(255, 255, 255), is_selected=False):
    section = np.ones((header_height, 320, 3), np.uint8) * 240
    
    # 绘制背景渐变效果
    if is_selected:
        cv2.rectangle(section, (10, 10), (310, 110), (220, 220, 220), -1)  # 选中状态背景
        cv2.rectangle(section, (10, 10), (310, 110), (100, 100, 100), 2)   # 边框
    else:
        cv2.rectangle(section, (15, 15), (305, 105), (250, 250, 250), -1)  # 普通状态背景
        cv2.rectangle(section, (15, 15), (305, 105), (180, 180, 180), 1)   # 边框
    
    # 绘制颜色圆形（更大更美观）
    center_x, center_y = 160, 45
    cv2.circle(section, (center_x, center_y), 25, color_bgr, -1)  # 主色圆
    cv2.circle(section, (center_x, center_y), 25, (100, 100, 100), 2)  # 圆形边框
    
    # 添加高光效果
    cv2.circle(section, (center_x - 8, center_y - 8), 8, (255, 255, 255), -1)
    cv2.circle(section, (center_x - 8, center_y - 8), 8, color_bgr, 4)
    
    # 绘制文字（居中对齐）
    text_width = len(text) * 12  # 估算文字宽度
    text_x = center_x - text_width // 2
    section = draw_chinese_text(section, text, (text_x, 75), text_color, 20)
    
    return section

# 创建各个工具区域
blue_section = create_tool_section((255, 100, 50), "蓝色画笔", (50, 50, 50))
red_section = create_tool_section((50, 50, 255), "红色画笔", (50, 50, 50))
green_section = create_tool_section((50, 200, 50), "绿色画笔", (50, 50, 50))
eraser_section = create_tool_section((80, 80, 80), "橡皮擦", (200, 200, 200))

# 将四个区域合并到header中
header[0:header_height, 0:320] = blue_section
header[0:header_height, 320:640] = red_section
header[0:header_height, 640:960] = green_section
header[0:header_height, 960:1280] = eraser_section

# 添加标题栏
title_text = "✨ 手势绘画工具 - 使用手势选择工具和绘画 ✨"
cv2.rectangle(header, (0, 0), (1280, 25), (60, 60, 60), -1)
header = draw_chinese_text(header, title_text, (320, 2), (255, 255, 255), 16)

# 将header添加到overlayList（创建选中状态的版本）
overlayList.append(header.copy())  # 默认状态

# 创建选中状态的headers
for i in range(4):
    selected_header = header.copy()
    if i == 0:  # 蓝色选中
        selected_section = create_tool_section((255, 100, 50), "蓝色画笔", (50, 50, 50), True)
        selected_header[0:header_height, 0:320] = selected_section
    elif i == 1:  # 红色选中
        selected_section = create_tool_section((50, 50, 255), "红色画笔", (50, 50, 50), True)
        selected_header[0:header_height, 320:640] = selected_section
    elif i == 2:  # 绿色选中
        selected_section = create_tool_section((50, 200, 50), "绿色画笔", (50, 50, 50), True)
        selected_header[0:header_height, 640:960] = selected_section
    elif i == 3:  # 橡皮擦选中
        selected_section = create_tool_section((80, 80, 80), "橡皮擦", (200, 200, 200), True)
        selected_header[0:header_height, 960:1280] = selected_section
    overlayList.append(selected_header)

# 初始化变量
color = [255, 100, 50]                             # 默认蓝色设定
brushThickness = 12                                 # 画笔宽度
eraserThickness = 35                                # 橡皮宽度
current_tool = 0                                    # 当前选中的工具 (0=蓝色, 1=红色, 2=绿色, 3=橡皮擦)

# 初始化摄像头
cap = None
print("正在尝试打开摄像头...")
for i in range(3):  # 尝试摄像头索引 0, 1, 2
    print(f"尝试摄像头索引: {i}")
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # 使用DirectShow后端
    if cap.isOpened():
        # 测试是否能读取帧
        ret, test_frame = cap.read()
        if ret:
            print(f"成功打开摄像头，索引: {i}")
            break
        else:
            print(f"摄像头 {i} 打开但无法读取画面")
            cap.release()
    else:
        print(f"无法打开摄像头索引: {i}")
        cap.release()

if cap is None or not cap.isOpened():
    print("错误：无法打开任何摄像头")
    print("请检查：")
    print("1. 摄像头是否被其他程序占用")
    print("2. 摄像头权限设置") 
    print("3. 摄像头驱动是否正常")
    print("4. 尝试重启计算机")
    exit()

# 设置摄像头参数
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 减少缓冲区大小
print(f"摄像头分辨率设置为: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")

detector = handDetector()                       # 调用手势检测函数
xp, yp = 0, 0                                       # 前一帧的坐标
imgCanvas = np.zeros((720, 1280, 3), np.uint8)      # 新建一个画布

frame_count = 0
while True:                                     # 1.import image
    success, img = cap.read()                       # 图片是否成功读入帧图像img
    if not success:
        frame_count += 1
        if frame_count > 10:  # 连续10次失败后退出
            print("连续多次无法读取摄像头画面，程序退出")
            break
        continue
    
    frame_count = 0  # 重置失败计数器
        
    img = cv2.flip(img, 1)                          # 翻转图像中的自己 1代表水平,0代表垂直翻转

    img = detector.findHands(img)               # 2.find hand landmarks
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        fingers = detector.fingersUp()          # 3. Check which fingers are up

        if fingers[1] and fingers[2]:           # 4. 选择模式 - 两根手指伸出
            xp, yp = 0, 0  # 重置绘画坐标
            
            # 绘制选择指示器（更美观的双指选择提示）
            cv2.circle(img, (x1, y1), 12, (255, 255, 255), -1)
            cv2.circle(img, (x1, y1), 12, (100, 100, 100), 2)
            cv2.circle(img, (x2, y2), 12, (255, 255, 255), -1)
            cv2.circle(img, (x2, y2), 12, (100, 100, 100), 2)
            cv2.line(img, (x1, y1), (x2, y2), (150, 150, 150), 2)
            
            # 工具选择逻辑
            if y1 < header_height:
                if 0 < x1 < 320:
                    current_tool = 0
                    header = overlayList[1]  # 蓝色选中状态
                    color = [255, 100, 50]
                elif 320 < x1 < 640:
                    current_tool = 1
                    header = overlayList[2]  # 红色选中状态
                    color = [50, 50, 255]
                elif 640 < x1 < 960:
                    current_tool = 2
                    header = overlayList[3]  # 绿色选中状态
                    color = [50, 200, 50]
                elif 960 < x1 < 1280:
                    current_tool = 3
                    header = overlayList[4]  # 橡皮擦选中状态
                    color = [80, 80, 80]
            
            # 显示选择提示
            cv2.putText(img, "Selection Mode", (x1 + 20, y1 - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        elif fingers[1] and not fingers[2]:    # 5. 绘画模式 - 只有食指伸出
            # 绘制画笔预览（根据当前工具显示不同样式）
            if current_tool == 3:  # 橡皮擦模式
                cv2.circle(img, (x1, y1), eraserThickness//2, (200, 200, 200), 2)
                cv2.circle(img, (x1, y1), 8, (100, 100, 100), -1)
                cv2.putText(img, "Eraser", (x1 + 25, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
            else:  # 画笔模式
                cv2.circle(img, (x1, y1), brushThickness//2, color, -1)
                cv2.circle(img, (x1, y1), brushThickness//2 + 2, (255, 255, 255), 2)
                cv2.putText(img, "Drawing", (x1 + 20, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # 绘画逻辑
            if xp == 0 and yp == 0:
                xp, yp = x1, y1

            if current_tool == 3:  # 橡皮擦
                cv2.line(img, (xp, yp), (x1, y1), (0, 0, 0), eraserThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), (0, 0, 0), eraserThickness)
            else:  # 画笔
                cv2.line(img, (xp, yp), (x1, y1), color, brushThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), color, brushThickness)

            xp, yp = x1, y1
        else:
            xp, yp = 0, 0
            
        # 清除画布 - 所有手指伸出
        if all(x >= 1 for x in fingers):
            imgCanvas = np.zeros((720, 1280, 3), np.uint8)
            # 显示清除提示
            cv2.putText(img, "Canvas Cleared!", (500, 400), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            
    # 实时显示画笔轨迹实现
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)      
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)
    
    # 添加header到图像顶部
    if 'header' in locals() and header is not None:
        img[0:header.shape[0], 0:header.shape[1]] = header
    else:
        # 如果header未定义，使用默认的overlayList[0]
        img[0:overlayList[0].shape[0], 0:overlayList[0].shape[1]] = overlayList[0]
    
    # 添加状态栏（底部信息显示）
    status_height = 40
    status_bar = np.ones((status_height, 1280, 3), np.uint8) * 50
    
    # 显示当前工具信息
    tool_names = ["蓝色画笔", "红色画笔", "绿色画笔", "橡皮擦"]
    status_text = f"当前工具: {tool_names[current_tool]} | 画笔大小: {brushThickness if current_tool != 3 else eraserThickness}"
    cv2.putText(status_bar, status_text, (20, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # 显示操作提示
    help_text = "双指选择工具 | 单指绘画 | 五指清除画布 | 按Q退出"
    cv2.putText(status_bar, help_text, (600, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    # 将状态栏添加到图像底部
    img[680:720, 0:1280] = status_bar
    
    # 添加手势识别状态指示
    if len(lmList) != 0:
        # 显示手势状态
        fingers_status = detector.fingersUp()
        finger_names = ["拇指", "食指", "中指", "无名指", "小指"]
        active_fingers = [finger_names[i] for i, status in enumerate(fingers_status) if status == 1]
        
        if active_fingers:
            finger_text = "检测到: " + ", ".join(active_fingers)
            cv2.putText(img, finger_text, (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    else:
        cv2.putText(img, "请将手放在摄像头前", (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("✨ 智能手势绘画工具 ✨", img)
            
    k = cv2.waitKey(1) & 0xFF                      # 检测键位是否按下
    if k == ord('q'):                       # 如果是键位Q键按下
        break                               # 退出循环

cap.release()                               # 退出摄像头
cv2.destroyAllWindows()                     # 关闭所有窗口