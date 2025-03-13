#####################################################
# 此程序为:06 用手势控制鼠标  单食指鼠标移动  食指和拇指碰撞为单击
# 修复了指尖与鼠标位置追踪不准确及方向相反的问题
#####################################################
import cv2                                                 # 导入opencv-python库 同时也别忘下载msvc-runtime库文件
import HandTrackingModule as htm                           # 导入手部追踪方法HandTrackingModule单元
import pyautogui                                           # 导入模拟鼠标和键盘的库
import numpy as np                                         # 导入数组与矩阵运算的库
import time                                                # 导入系统时间处理库
##############################
# 获取屏幕分辨率，适配全屏
screen_width, screen_height = pyautogui.size()                          # 获得电脑屏幕的宽和高
wCam, hCam = screen_width, screen_height                               # 设置捕捉框为全屏
smoothening = 5                                                         # 降低平滑系数，提高响应速度，同时保持一定的平稳性
detectionConfidence = 0.8                                              # 手势检测置信度
clickDistance = 30                                                      # 点击距离阈值
##############################
cap = cv2.VideoCapture(0)                                               # 若使用笔记本自带摄像头则编号为0  若使用外接摄像头 则更改为1或其他编号
cap.set(3, wCam)                                                        # 设定捕捉框的宽度
cap.set(4, hCam)                                                        # 设定捕捉框的高度
pTime = 0                                                               # 设置第一帧开始处理的起始时间
plocX, plocY = 0, 0                                                     # 前一帧的鼠标所在位置坐标xy值
clocX, clocY = 0, 0                                                     # 下一帧的鼠标所在位置坐标xy值
detector = htm.handDetector(detectionCon=detectionConfidence)           # 引入手势模型文件的手势检测方法
##############################
# 创建使用说明和参数显示函数
def draw_instructions(img):
    # 设置右下角信息区域背景
    h, w, c = img.shape
    cv2.rectangle(img, (w-300, h-180), (w-10, h-10), (0, 0, 0), cv2.FILLED)  # 黑色背景
    cv2.rectangle(img, (w-300, h-180), (w-10, h-10), (255, 255, 255), 2)     # 白色边框
    
    # 添加使用说明
    cv2.putText(img, "使用说明:", (w-290, h-150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(img, "1. 食指竖起: 移动鼠标", (w-290, h-120), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    cv2.putText(img, "2. 食指+拇指捏合: 单击", (w-290, h-100), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    cv2.putText(img, "3. 按'q'键退出", (w-290, h-80), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    
    # 添加关键参数
    cv2.putText(img, "关键参数:", (w-290, h-50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(img, f"FPS: {int(fps)}", (w-290, h-30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)
    cv2.putText(img, f"检测置信度: {detectionConfidence}", (w-200, h-30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)
    cv2.putText(img, f"点击距离: {clickDistance}px", (w-290, h-15), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)
    
    return img
##############################
while True:                                                        # 1. 循环检测手部 得到手指关键点坐标
    success, img = cap.read()                                           # 图片是否成功接收帧图像img
    if not success:
        print("无法获取摄像头画面")
        continue
        
    img = cv2.flip(img, 1)                                             # 水平翻转图像，解决镜像问题
    img = detector.findHands(img)                                       # 获得画面中手势数据
    lmList = detector.findPosition(img, draw=False)                     # 传入每帧图像, 返回手部关键点的坐标信息(字典构成的列表hands)
##############################
    if len(lmList) != 0:                                           # 2. 如果采集到到手势关键点
        x1, y1 = lmList[8][1:]                                          # 获得食指指尖的关键点8的部分坐标
        x2, y2 = lmList[4][1:]                                         # 获得拇指指尖的关键点4的部分坐标
##############################
        fingers = detector.fingersUp()                             # 3. 检测五个手指是竖起方法,返回值为[0,1,1,0,0]1该手指竖起,0该手指弯下
##############################
        if fingers[1] and fingers[0] == False:                     # 4. 如果食指竖起但拇指没有竖起
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
        if fingers[1] and fingers[0]:                                 # 5. 如果食指和拇指同时竖起
            length, img, pointInfo = detector.findDistance(8, 4, img)   # 计算食指尖和拇指尖间的距离
            if length < clickDistance:                                   # 且食指尖和拇指尖距离小于设定阈值,则单击鼠标
                cv2.circle(img, (pointInfo[4], pointInfo[5]), 15, (0, 255, 0), cv2.FILLED)   # 食指尖和拇指尖画绿色圆,以示点击鼠标
                pyautogui.click()                                        # 鼠标左键单击
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
