#####################################################
# 此程序为:mlx007 手势控制音量程序,通过检测手指间距离来控制系统音量 
#####################################################
import cv2
import numpy as np
import time
import math
import mediapipe as mp
from ctypes import cast, POINTER

# 尝试导入音量控制相关库
try:
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    volume_control_available = True
except ImportError:
    print("警告: 未找到comtypes或pycaw库，将使用模拟音量控制")
    print("提示: 请运行 'pip install comtypes pycaw' 安装所需依赖")
    volume_control_available = False

#############################
# 手势检测类
#############################
class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.8, trackCon=0.8):
        """初始化手势检测器
        Args:
            mode: 是否使用静态图像模式
            maxHands: 最大检测手数量
            detectionCon: 检测置信度阈值
            trackCon: 跟踪置信度阈值
        """
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.results = None
        self.lmList = []
        
        # 初始化mediapipe手部检测
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]  # 指尖ID列表 [拇指, 食指, 中指, 无名指, 小指]
    
    def findHands(self, img, draw=True):
        """处理图像并识别手势
        Args:
            img: 输入图像
            draw: 是否在图像上绘制手部标记
        Returns:
            处理后的图像
        """
        if img is None:
            return None
            
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        
        # 检测到手部时绘制标记
        if self.results and self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, mp.solutions.hands.HAND_CONNECTIONS)
        return img
    
    def findPosition(self, img, draw=False):
        """获取手部关键点位置
        Args:
            img: 输入图像
            draw: 是否在图像上绘制关键点
        Returns:
            关键点列表，每个关键点为[id, x, y]
        """
        self.lmList = []
        if img is None:
            return self.lmList
            
        if self.results and self.results.multi_hand_landmarks:
            # 使用第一只检测到的手
            myHand = self.results.multi_hand_landmarks[0]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 7, (255, 0, 255), cv2.FILLED)
        return self.lmList
        
    def __del__(self):
        """析构函数，释放资源"""
        if hasattr(self, 'hands') and self.hands:
            self.hands.close()

#############################
# 初始化音量控制
#############################
def initialize_volume_control():
    """初始化系统音量控制
    Returns:
        tuple: (是否可用, 最小音量, 最大音量, 音量控制对象)
    """
    global volume_control_available
    
    if volume_control_available:
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volumeRange = volume.GetVolumeRange()  # 通常为(-63.5, 0.0, 0.03125)
            minVol = volumeRange[0]  # 最小音量 (dB)
            maxVol = volumeRange[1]  # 最大音量 (dB)
            return True, minVol, maxVol, volume
        except Exception as e:
            print(f"初始化音量控制失败: {e}")
            volume_control_available = False
    
    # 如果音量控制不可用，设置模拟值
    print("使用模拟音量控制模式")
    return False, -63.5, 0.0, None

# 初始化音量控制
volume_control_available, minVol, maxVol, volume = initialize_volume_control()

#############################
# 主程序
#############################
def initialize_camera(width=640, height=480, camera_id=0):
    """初始化摄像头
    Args:
        width: 摄像头宽度
        height: 摄像头高度
        camera_id: 摄像头ID，0为默认摄像头
    Returns:
        摄像头对象
    """
    cap = cv2.VideoCapture(camera_id)  # 若使用笔记本自带摄像头则编号为0，外接摄像头则更改为1或其他编号
    cap.set(3, width)  # 设置宽度
    cap.set(4, height)  # 设置高度
    
    if not cap.isOpened():
        print("错误：无法打开摄像头")
        return None
    return cap

def process_hand_gesture(img, lmList, detector):
    """处理手势并控制音量
    Args:
        img: 输入图像
        lmList: 手部关键点列表
        detector: 手势检测器对象
    Returns:
        处理后的图像
    """
    global volume_control_available, minVol, maxVol, volume
    
    if len(lmList) == 0:
        return img
        
    # 获取拇指和食指的坐标
    x1, y1 = lmList[4][1], lmList[4][2]  # 拇指指尖
    x2, y2 = lmList[8][1], lmList[8][2]  # 食指指尖
    xc, yc = (x2 + x1) // 2, (y2 + y1) // 2  # 中心点
    
    # 绘制标记
    cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)  # 拇指
    cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)  # 食指
    cv2.circle(img, (xc, yc), 15, (255, 0, 255), cv2.FILLED)  # 中心点
    cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)  # 连线

    # 计算拇指和食指之间的距离
    length = math.hypot(x2 - x1, y2 - y1)  # 15--200
    
    # 如果距离小于25，显示绿色中心点表示激活
    if length < 25:
        cv2.circle(img, (xc, yc), 15, (0, 255, 0), cv2.FILLED)
        
    # 将手指距离映射到音量范围
    vol = np.interp(length, [15, 200], [minVol, maxVol])
    if volume_control_available:
        try:
            volume.SetMasterVolumeLevel(vol, None)
        except Exception as e:
            print(f"设置音量失败: {e}")
            volume_control_available = False
    
    # 将手指距离映射到音量条和百分比
    volBar = np.interp(length, [15, 200], [350, 150])
    volPer = np.interp(length, [15, 200], [0, 100])

    # 绘制音量条
    cv2.rectangle(img, (20, 150), (50, 350), (255, 0, 255), 2)
    cv2.rectangle(img, (20, int(volBar)), (50, 350), (255, 0, 255), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)}%', (10, 380), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
    
    return img

#############################
# 主程序入口
#############################
def main():
    """主程序入口"""
    # 初始化摄像头
    cap = initialize_camera()
    if cap is None:
        print("无法初始化摄像头，程序退出")
        return
    
    # 初始化手势检测器
    detector = handDetector(detectionCon=0.7)
    
    # 显示程序信息
    print("手势控制音量程序已启动")
    print("提示: 使用拇指和食指的距离来控制音量")
    print("按q键退出程序")
    
    # 主循环
    while True:
        # 读取摄像头画面
        success, img = cap.read()
        if not success:
            print("无法读取摄像头画面，程序退出")
            break
        
        # 检测手势
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        
        # 处理手势并控制音量
        img = process_hand_gesture(img, lmList, detector)
        
        # 显示FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime) if 'pTime' in locals() else 0
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
        
        # 显示画面
        cv2.imshow("手势控制音量", img)
        
        # 按q键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

# 程序入口
if __name__ == "__main__":
    main()
