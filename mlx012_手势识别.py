#####################################################
# 此程序为:12 手势识别程序
#####################################################
import cv2                                                 # 导入opencv-python库 同时也别忘下载msvc-runtime库文件
import HandTrackingModule as htm                           # 导入手部追踪方法HandTrackingModule单元
import numpy as np                                         # 导入数组与矩阵运算的库
import time                                                # 导入系统时间处理库
import os                                                  # 导入操作系统功能库

##############################
wCam, hCam = 1280, 720                                     # 设置摄像头捕捉画面的宽度和高度
##############################
cap = cv2.VideoCapture(0)                                  # 若使用笔记本自带摄像头则编号为0  若使用外接摄像头 则更改为1或其他编号
cap.set(3, wCam)                                           # 设定捕捉框的宽度
cap.set(4, hCam)                                           # 设定捕捉框的高度

# 导入手指图片
folderPath = "FingerImg"                                   # 设置手指图片文件夹路径
fingerImgList = os.listdir(folderPath)                     # 获取文件夹中的所有文件
fingerImgList.sort()                                       # 对文件名进行排序

# 加载所有手指图片
overLayList = []
for imgPath in fingerImgList:
    image = cv2.imread(f'{folderPath}/{imgPath}')          # 读取图片
    if image is not None:                                  # 确保图片成功加载
        overLayList.append(image)                          # 将图片添加到列表中

pTime = 0                                                  # 设置第一帧开始处理的起始时间
detector = htm.handDetector(detectionCon=0.75)             # 创建手势检测器实例，设置检测置信度为0.75

# 指尖ID列表，分别对应大拇指、食指、中指、无名指和小指的指尖
tipIds = [4, 8, 12, 16, 20]                                

while True:
    success, img = cap.read()                              # 读取摄像头画面
    if not success:
        print("无法获取摄像头画面")
        break
        
    img = detector.findHands(img)                          # 检测手部并在图像上绘制手部关键点
    lmList = detector.findPosition(img, draw=False)         # 获取手部关键点位置，但不在图像上绘制
    
    if len(lmList) != 0:                                   # 如果检测到手部关键点
        fingers = []                                        # 存储每个手指的状态（伸出或弯曲）
        
        # 大拇指检测（水平方向）
        if lmList[tipIds[0]][1] > lmList[tipIds[0]-1][1]:  # 如果大拇指指尖x坐标大于大拇指第二关节x坐标
            fingers.append(1)                               # 大拇指伸出
        else:
            fingers.append(0)                               # 大拇指弯曲
            
        # 其他四个手指检测（垂直方向）
        for id in range(1, 5):
            # 如果手指指尖y坐标小于该手指第二关节y坐标（因为y轴向下，所以小于表示指尖在上方）
            if lmList[tipIds[id]][2] < lmList[tipIds[id]-2][2]:
                fingers.append(1)                           # 手指伸出
            else:
                fingers.append(0)                           # 手指弯曲
                
        # 计算伸出的手指数量
        totalFingers = fingers.count(1)
        print(fingers)                                      # 打印手指状态列表
        
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