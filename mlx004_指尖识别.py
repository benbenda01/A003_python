#####################################################
# 此程序为:mlx04 用手势标出食指和中指的指尖
#####################################################
import cv2                                              # 导入opencv-python库 同时也别忘下载msvc-runtime库文件
import mediapipe as mp                                  # 导入手势识别库

# 定义HandDetector类
class HandDetector():                                             # 建立一个手势检测的类
    def __init__(self):                                           # 初始化方法
        self.hand_detector = mp.solutions.hands.Hands()           # 获取手势检测方法
        self.drawer = mp.solutions.drawing_utils                  # 获取手势划线方法

    def process(self, img):                                       # 建立一个图像处理的类
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)            # 将获取的图像从BGR灰阶处理为RGB数据
        self.hands_data = self.hand_detector.process(img_rgb)     # 获取处理后数据
        if self.hands_data.multi_hand_landmarks:                  # 获得所有手势数据
            for handlms in self.hands_data.multi_hand_landmarks:  # 查找手势的位置字典
                self.drawer.draw_landmarks(img, handlms, mp.solutions.hands.HAND_CONNECTIONS)    # 连接手势的关键点为直线

    def find_position(self, img):                                 # 建立一个手势位置查找类
        h, w, c = img.shape                                       # 获取高宽长数据
        position = {'Left': {}, 'Right': {}}                      # 左右手数组
        if self.hands_data.multi_hand_landmarks:                  # 获得手势的关节点数据
            i = 0                                                 # 定义循环变量
            for point in self.hands_data.multi_handedness:        # 查找手势点
                score = point.classification[0].score             # 左手右手的判别方法
                if score >= 0.8:                                  # 假如近似分数大于0.8
                    label = point.classification[0].label         # 获取位置点
                    hand_lms = self.hands_data.multi_hand_landmarks[i].landmark     #自动切换左右手
                    for id, lm in enumerate(hand_lms):            # 查找每个关键点
                        x, y = int(lm.x * w), int(lm.y * h)       # 获取显示框的长度和高度，修复y坐标缺少int转换的问题
                        position[label][id] = (x, y)              # 位置标签号
                i = i + 1                                         # 循环变量自增
        return position                                           # 返回位置点

# 主程序部分
def main():
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

# 程序入口
if __name__ == "__main__":
    main()
