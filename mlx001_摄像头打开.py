import cv2                                               # 导入opencv-python库 同时也别忘下载msvc-runtime库文件
camera = cv2.VideoCapture(0)                             # 获取摄像头画面存入相机变量

# 检查摄像头是否成功打开
if not camera.isOpened():
    print("错误：无法打开摄像头")
    exit()

# 添加循环来持续捕获和显示摄像头画面
while True:
    success, img = camera.read()                         # 获取摄像头单帧画面存入照片变量
    if success:                                          # 如果判断为真
        cv2.imshow('Video', img)                         # 显示图像
        
    k = cv2.waitKey(1)                                  # 检测键位是否按下
    if k == ord('q'):                                   # 如果是键位Q键按下
        break                                           # 退出循环
        
camera.release()                                         # 退出摄像头
cv2.destroyAllWindows()                                  # 关闭所有视窗