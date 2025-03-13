#####################################################
# 此程序为:05 用手势标出食指和中指的指尖
#####################################################
import cv2                                              # 导入opencv-python库 同时也别忘下载msvc-runtime库文件
from mlx004_手势库文件 import HandDetector                # 导入手势识别文件,调用mlx004_手势库文件.py文件

camera = cv2.VideoCapture(0)                            # 获取摄像头画面存入相机变量
hand_detector = HandDetector()                          # 获取手势识别器
while True:                                             # 无限循环
    success, img = camera.read()                        # 获取摄像头单帧画面存入照片变量
    if success:                                         # 如果判断为真
        img = cv2.flip(img, 1)                          # 左右翻转获得的画面
        hand_detector.process(img)                      # 将获取的画面从BGR数据转换为RGB数据
        position = hand_detector.find_position(img)     # 获取手势坐标

        left_finger = position['Left'].get(8, None)     # 左手位置获取
        if left_finger:                                 # 判断左手位置数据
            cv2.circle(img, (int(left_finger[0]), int(left_finger[1])), 10, (0, 0, 255), cv2.FILLED)    # 左手的食指红点

        right_finger = position['Right'].get(8, None)   # 右手位置获取
        if right_finger:                                # 判断右手位置数据
            cv2.circle(img, (int(right_finger[0]), int(right_finger[1])), 10, (0, 255, 0), cv2.FILLED)  # 右手的食指绿点
        cv2.imshow('Video', img)                        # 在原图像上显示结果

    k = cv2.waitKey(1)                                  # 检测键位是否按下
    if k == ord('q'):                                   # 如果是键位Q键按下
        break                                           # 退出循环
camera.release()                                        # 退出摄像头
cv2.destroyAllWindows()                                 # 关闭所有视窗
