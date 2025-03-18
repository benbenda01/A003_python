#####################################################
# 此程序为:mlx003 初学 使用opencv库和mediapipe库实现手掌识别
#####################################################

import cv2                                               # 导入opencv-python库 同时也别忘下载msvc-runtime库文件
import mediapipe                                         # 导入手势识别库

def initialize_camera():                                 # 初始化摄像头
    camera = cv2.VideoCapture(0)                         # 获取摄像头画面存入相机变量
    if not camera.isOpened():                            # 检查摄像头是否成功打开
        print("错误：无法打开摄像头")                      # 无法打开时进行提示
        return None                                      # 无法打开时返回None
    return camera                                        # 返回摄像头对象

def initialize_hand_detector():                           # 初始化手势识别器  
    return mediapipe.solutions.hands.Hands(min_detection_confidence=0.7)  # 设置较高的检测置信度

def process_frame(img, hand_detector):                   # 处理单帧图像，进行手势识别    
    if img is None:                                     # 检查图像是否为None
        return None                                     # 如果是None，直接返回None
    
    img = cv2.flip(img, 1)                               # 水平翻转图像，使其更符合用户直觉
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)       # 将获取的图片从BGR格式转换为RGB数据
    result = hand_detector.process(img_rgb)              # 在RGB图像中检测手部关节点    
    if result.multi_hand_landmarks:                      # 如果手指关节点有返回数值
        for handlms in result.multi_hand_landmarks:      # 遍历循环这20个手指关节点进行标注
            mediapipe.solutions.drawing_utils.draw_landmarks(
                img, 
                handlms, 
                mediapipe.solutions.hands.HAND_CONNECTIONS                    # 将20个关节点连线标注
            )  
    return img

def main():                                              # 主函数
    camera = initialize_camera()    
    if camera is None:                                   # 检查摄像头是否成功初始化
        print("摄像头初始化失败，程序退出")
        return
        
    hand_detector = initialize_hand_detector()
    try:
        while True:                                      # 无限循环
            success, img = camera.read()                 # 获取摄像头单帧画面存入照片变量
            if not success:                              # 检查是否成功获取图像
                print("无法获取摄像头画面")
                continue                                 # 继续下一次循环
                
            processed_img = process_frame(img, hand_detector)  # 处理图像并进行手势识别
            if processed_img is not None:                # 检查处理后的图像是否为None
                cv2.imshow('手势识别', processed_img)      # 将原图像进行显示输出
            
            k = cv2.waitKey(1)                           # 检测键位是否按下
            if k == ord('q'):                            # 如果是键位Q键按下
                break                                    # 退出循环
    finally:
        camera.release()                                 # 退出摄像头
        cv2.destroyAllWindows()                          # 关闭所有视窗

if __name__ == "__main__":
    main()
