#####################################################
# 此程序为:手势库文件 用于mlx05 文件运行的库调用
#####################################################
import cv2                                                        # 导入opencv-python库 同时也别忘下载msvc-runtime库文件
import mediapipe as mp                                            # 导入手势识别库

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
                        x, y = int(lm.x * w), (lm.y * h)          # 获取显示框的长度和高度
                        position[label][id] = (x, y)              # 位置标签号
                i = i + 1                                         # 循环变量自增
        return position                                           # 返回位置点
