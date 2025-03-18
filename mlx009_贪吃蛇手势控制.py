#####################################################
# 此程序为:mlx009 贪吃蛇手势控制游戏
# 支持三种模式：手动控制、自动控制、手势控制
# 支持五档速度调节
#####################################################

import cv2
import numpy as np
import mediapipe as mp
import random
import time
import math
import pygame
import os
from PIL import Image, ImageDraw, ImageFont
from pygame.locals import *

# 手势检测器类
class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.8, trackCon=0.8):
        self.lmList = {'Left': {}, 'Right': {}}
        self.results = None
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.hands = None

        self.hands = mp.solutions.hands.Hands()
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]  # 指尖ID列表
        self.wristId = 0  # 手腕ID
    
    def findHands(self, img, draw=True):
        """处理图像并识别手势"""
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        
        # 检测到手部时绘制标记
        if self.results is not None \
            and hasattr(self.results, 'multi_hand_landmarks') \
            and self.results.multi_hand_landmarks is not None:

            for handLms in self.results.multi_hand_landmarks:
                if draw and self.mpDraw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                             mp.solutions.hands.HAND_CONNECTIONS)
        return img
    
    def findPosition(self, img, draw=True):
        """获取手部关键点位置"""
        self.lmList = {'Left': {}, 'Right': {}}
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
                            cv2.circle(img, (cx, cy), 7, (255, 0, 255), cv2.FILLED)
        return self.lmList
    
    def fingersUp(self):
        """检测哪些手指伸出"""
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
        
    def getIndexFingerDirection(self, img=None, draw=True):
        """检测食指的朝向，返回方向：'UP', 'DOWN', 'LEFT', 'RIGHT' 或 None"""
        # 确保有手部检测结果
        if not self.lmList:
            return None
            
        # 获取左手或右手的食指关键点
        index_finger_tip = None
        index_finger_pip = None
        wrist_point = None
        
        if self.lmList.get('Left') and self.lmList['Left'].get(8) and self.lmList['Left'].get(5) and self.lmList['Left'].get(0):
            index_finger_tip = self.lmList['Left'][8]  # 食指指尖
            index_finger_pip = self.lmList['Left'][5]  # 食指第二关节
            wrist_point = self.lmList['Left'][0]  # 手腕
        elif self.lmList.get('Right') and self.lmList['Right'].get(8) and self.lmList['Right'].get(5) and self.lmList['Right'].get(0):
            index_finger_tip = self.lmList['Right'][8]  # 食指指尖
            index_finger_pip = self.lmList['Right'][5]  # 食指第二关节
            wrist_point = self.lmList['Right'][0]  # 手腕
        
        if not index_finger_tip or not index_finger_pip or not wrist_point:
            return None
            
        # 计算食指方向向量
        dx = index_finger_tip[0] - index_finger_pip[0]
        dy = index_finger_tip[1] - index_finger_pip[1]
        
        # 绘制方向指示线
        if draw and img is not None:
            cv2.line(img, index_finger_pip, index_finger_tip, (0, 255, 0), 3)
            
        # 根据向量判断方向（使用角度判断更准确）
        angle = math.degrees(math.atan2(dy, dx))
        
        # 将角度转换为方向
        # 上：-45度到45度，下：135度到-135度，左：45度到135度，右：-135度到-45度
        if -45 <= angle <= 45:
            direction = 'RIGHT'
        elif 45 < angle <= 135:
            direction = 'DOWN'
        elif -135 <= angle < -45:
            direction = 'UP'
        else:  # 135 < angle <= 180 or -180 <= angle < -135
            direction = 'LEFT'
            
        return direction

# 定义一个函数用于绘制中文文本
def draw_chinese_text(img, text, position, text_color=(255, 255, 255), text_size=30):
    # 创建一个空白的PIL图像，设置透明背景
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    # 加载一个支持中文的字体
    fontpath = os.path.join(os.environ.get('WINDIR', 'C:\Windows'), 'Fonts', 'simhei.ttf')
    font = ImageFont.truetype(fontpath, text_size)
    
    # 在图像上绘制文本
    draw.text(position, text, font=font, fill=text_color)
    
    # 转换回OpenCV格式
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

# 贪吃蛇游戏类
class SnakeGame:
    def __init__(self, width=640, height=480):
        # 初始化pygame
        pygame.init()
        
        # 游戏窗口设置
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('贪吃蛇手势控制游戏')
        
        # 颜色定义
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.GRAY = (128, 128, 128)
        
        # 游戏参数
        self.cell_size = 20
        self.snake_speed = 10  # 初始速度
        self.speed_levels = [5, 10, 15, 20, 25]  # 五档速度
        self.speed_level = 1  # 默认速度等级（索引）
        
        # 游戏状态
        self.game_mode = 0  # 0: 手动模式, 1: 自动模式, 2: 手势控制模式
        self.mode_names = ['手动模式', '自动模式', '手势控制模式']
        self.running = True
        self.game_over = False
        self.paused = False
        
        # 初始化蛇和食物
        self.reset_game()
        
        # 字体
        self.font = pygame.font.SysFont('simhei', 24)
        self.large_font = pygame.font.SysFont('simhei', 36)
        
        # 时钟
        self.clock = pygame.time.Clock()
    
    def reset_game(self):
        # 蛇的初始位置和方向
        self.snake = [(self.width // 2, self.height // 2)]
        self.snake_length = 1
        self.direction = 'RIGHT'
        
        # 随机生成食物位置
        self.generate_food()
        
        # 重置游戏状态
        self.score = 0
        self.game_over = False
        self.paused = False
    
    def generate_food(self):
        # 生成食物，确保不在蛇身上
        while True:
            x = random.randint(0, (self.width - self.cell_size) // self.cell_size) * self.cell_size
            y = random.randint(0, (self.height - self.cell_size) // self.cell_size) * self.cell_size
            self.food = (x, y)
            if self.food not in self.snake:
                break
    
    def change_direction(self, new_direction):
        # 防止蛇反向移动
        if (new_direction == 'UP' and self.direction != 'DOWN') or \
           (new_direction == 'DOWN' and self.direction != 'UP') or \
           (new_direction == 'LEFT' and self.direction != 'RIGHT') or \
           (new_direction == 'RIGHT' and self.direction != 'LEFT'):
            self.direction = new_direction
    
    def move_snake(self):
        # 根据方向移动蛇头
        x, y = self.snake[0]
        if self.direction == 'UP':
            y -= self.cell_size
        elif self.direction == 'DOWN':
            y += self.cell_size
        elif self.direction == 'LEFT':
            x -= self.cell_size
        elif self.direction == 'RIGHT':
            x += self.cell_size
        
        # 实现墙壁穿透功能
        if x < 0:
            x = self.width - self.cell_size
        elif x >= self.width:
            x = 0
        if y < 0:
            y = self.height - self.cell_size
        elif y >= self.height:
            y = 0
        
        # 新的蛇头位置
        new_head = (x, y)
        
        # 检查是否撞到自己
        if new_head in self.snake[1:]:
            self.game_over = True
            return
        
        # 添加新的蛇头
        self.snake.insert(0, new_head)
        
        # 检查是否吃到食物
        if new_head == self.food:
            self.score += 1
            self.generate_food()
        else:
            # 如果没吃到食物，移除蛇尾
            self.snake.pop()
    
    def auto_play(self):
        # 自动模式的简单AI
        if not self.snake:
            return
        
        head_x, head_y = self.snake[0]
        food_x, food_y = self.food
        
        # 决定移动方向
        if head_x < food_x and self.direction != 'LEFT':
            new_direction = 'RIGHT'
        elif head_x > food_x and self.direction != 'RIGHT':
            new_direction = 'LEFT'
        elif head_y > food_y and self.direction != 'DOWN':
            new_direction = 'UP'
        elif head_y < food_y and self.direction != 'UP':
            new_direction = 'DOWN'
        else:
            # 如果被卡住，尝试其他方向
            possible_directions = []
            if self.direction != 'DOWN':
                possible_directions.append('UP')
            if self.direction != 'UP':
                possible_directions.append('DOWN')
            if self.direction != 'RIGHT':
                possible_directions.append('LEFT')
            if self.direction != 'LEFT':
                possible_directions.append('RIGHT')
            
            # 检查哪个方向不会导致碰撞
            safe_directions = []
            for d in possible_directions:
                test_x, test_y = head_x, head_y
                if d == 'UP':
                    test_y -= self.cell_size
                elif d == 'DOWN':
                    test_y += self.cell_size
                elif d == 'LEFT':
                    test_x -= self.cell_size
                elif d == 'RIGHT':
                    test_x += self.cell_size
                
                # 检查是否安全
                if (0 <= test_x < self.width and 0 <= test_y < self.height and 
                    (test_x, test_y) not in self.snake):
                    safe_directions.append(d)
            
            if safe_directions:
                new_direction = random.choice(safe_directions)
            else:
                return  # 无路可走
        
        self.change_direction(new_direction)
    
    def draw(self):
        # 绘制游戏界面
        self.screen.fill(self.BLACK)
        
        # 绘制蛇
        for i, segment in enumerate(self.snake):
            # 绘制蛇身
            pygame.draw.rect(self.screen, self.GREEN, (segment[0], segment[1], self.cell_size, self.cell_size))
            
            # 在蛇头上显示"笨"字
            if i == 0:
                ben_text = self.font.render('笨', True, self.BLACK)
                text_rect = ben_text.get_rect(center=(segment[0] + self.cell_size//2, segment[1] + self.cell_size//2))
                self.screen.blit(ben_text, text_rect)
            # 在蛇身上显示序数
            elif i > 0:
                # 计算序数（从1开始）
                seq_num = str(i)
                seq_text = self.font.render(seq_num, True, self.BLACK)
                text_rect = seq_text.get_rect(center=(segment[0] + self.cell_size//2, segment[1] + self.cell_size//2))
                self.screen.blit(seq_text, text_rect)
        
        # 绘制食物
        pygame.draw.rect(self.screen, self.RED, (self.food[0], self.food[1], self.cell_size, self.cell_size))
        
        # 绘制边界
        pygame.draw.rect(self.screen, self.WHITE, (0, 0, self.width, self.height), 2)
        
        # 绘制分数
        score_text = self.font.render(f'分数: {self.score}', True, self.WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # 绘制模式和速度
        mode_text = self.font.render(f'模式: {self.mode_names[self.game_mode]}', True, self.WHITE)
        self.screen.blit(mode_text, (10, 40))
        
        speed_text = self.font.render(f'速度: {self.speed_level + 1}/5', True, self.WHITE)
        self.screen.blit(speed_text, (10, 70))
        
        # 绘制控制说明
        controls_text = self.font.render('M: 切换模式 | +/-: 调整速度 | R: 重置游戏 | P: 暂停 | ESC: 退出', True, self.WHITE)
        self.screen.blit(controls_text, (10, self.height - 30))
        
        # 游戏结束或暂停时显示提示
        if self.game_over:
            game_over_text = self.large_font.render('游戏结束!', True, self.WHITE)
            self.screen.blit(game_over_text, (self.width//2 - 80, self.height//2 - 50))
            restart_text = self.font.render('按R键重新开始', True, self.WHITE)
            self.screen.blit(restart_text, (self.width//2 - 80, self.height//2))
        
        if self.paused:
            pause_text = self.large_font.render('游戏暂停', True, self.WHITE)
            self.screen.blit(pause_text, (self.width//2 - 80, self.height//2 - 50))
            resume_text = self.font.render('按P键继续', True, self.WHITE)
            self.screen.blit(resume_text, (self.width//2 - 60, self.height//2))
        
        # 更新显示
        pygame.display.flip()

# 主程序
def main():
    # 初始化游戏和摄像头
    game = SnakeGame(width=800, height=600)
    cap = cv2.VideoCapture(0)  # 使用默认摄像头
    detector = handDetector(detectionCon=0.7)
    
    # 手势控制相关变量
    last_gesture_time = time.time()
    gesture_cooldown = 0.3  # 手势识别冷却时间（秒）
    
    # 游戏主循环
    while game.running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == QUIT:
                game.running = False
            elif event.type == KEYDOWN:
                # 键盘控制
                if event.key == K_ESCAPE:
                    game.running = False
                elif event.key == K_r:
                    game.reset_game()
                elif event.key == K_p:
                    game.paused = not game.paused
                elif event.key == K_m:
                    game.game_mode = (game.game_mode + 1) % 3
                elif event.key == K_EQUALS or event.key == K_PLUS:
                    game.speed_level = min(game.speed_level + 1, len(game.speed_levels) - 1)
                    game.snake_speed = game.speed_levels[game.speed_level]
                elif event.key == K_MINUS:
                    game.speed_level = max(game.speed_level - 1, 0)
                    game.snake_speed = game.speed_levels[game.speed_level]
                
                # 手动模式下的方向控制
                if game.game_mode == 0 and not game.paused and not game.game_over:
                    if event.key == K_UP:
                        game.change_direction('UP')
                    elif event.key == K_DOWN:
                        game.change_direction('DOWN')
                    elif event.key == K_LEFT:
                        game.change_direction('LEFT')
                    elif event.key == K_RIGHT:
                        game.change_direction('RIGHT')
        
        # 如果游戏暂停或结束，只更新显示
        if game.paused or game.game_over:
            game.draw()
            game.clock.tick(30)
            continue
        
        # 手势控制模式
        if game.game_mode == 2:
            success, img = cap.read()
            if success:
                img = cv2.flip(img, 1)  # 水平翻转图像
                img = detector.findHands(img)
                lmList = detector.findPosition(img, draw=True)
                
                # 检测手势
                fingers = detector.fingersUp()
                finger_count = sum(fingers)
                
                # 获取食指朝向
                direction = detector.getIndexFingerDirection(img)
                
                # 创建信息显示区域
                info_section = np.zeros((150, img.shape[1], 3), np.uint8)
                
                # 显示手指状态信息
                info_section = draw_chinese_text(info_section, f"手指状态: {fingers}, 伸出手指数: {finger_count}", (10, 30))
                
                # 显示控制说明
                info_section = draw_chinese_text(info_section, "控制说明: 伸出食指，指向不同方向控制蛇的移动", (10, 70))
                
                # 显示当前方向
                if direction:
                    direction_text = {
                        'UP': '上',
                        'DOWN': '下',
                        'LEFT': '左',
                        'RIGHT': '右'
                    }.get(direction, '')
                    info_section = draw_chinese_text(info_section, f"当前方向: {direction_text}", (10, 110), text_color=(0, 255, 255))
                
                # 将信息区域添加到图像底部
                img_with_info = np.vstack([img, info_section])
                
                # 根据食指朝向控制方向
                current_time = time.time()
                if current_time - last_gesture_time > gesture_cooldown and fingers[1] == 1 and direction:
                    # 只有食指伸出时才根据方向控制
                    game.change_direction(direction)
                    last_gesture_time = current_time
                    
                    # 在图像上显示方向变化提示
                    direction_text = {
                        'UP': '上',
                        'DOWN': '下',
                        'LEFT': '左',
                        'RIGHT': '右'
                    }.get(direction, '')
                    cv2.putText(img, f"方向: {direction_text}", (img.shape[1]//2-50, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                
                # 显示摄像头画面
                cv2.imshow("手势控制", img_with_info)
                
                # 按ESC键退出
                if cv2.waitKey(1) & 0xFF == 27:
                    game.running = False
        
        # 自动模式
        if game.game_mode == 1:
            game.auto_play()
        
        # 更新游戏状态
        game.move_snake()
        
        # 绘制游戏
        game.draw()
        
        # 控制游戏速度
        game.clock.tick(game.snake_speed)
    
    # 清理资源
    if game.game_mode == 2:
        cap.release()
        cv2.destroyAllWindows()
    pygame.quit()

# 启动游戏
if __name__ == "__main__":
    main()