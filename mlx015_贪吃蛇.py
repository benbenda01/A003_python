import pygame
import random
import sys

# 初始化pygame
pygame.init()

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# 定义游戏参数
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_SIZE = 20
SNAKE_SPEED = 15

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('贪吃蛇')

# 加载字体
font = pygame.font.SysFont(None, 36)

class Snake:
    """定义蛇类"""
    
    def __init__(self):
        self.length = 1
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        self.color = GREEN
        self.score = 0
    
    def get_head_position(self):
        """获取蛇头位置"""
        return self.positions[0]
    
    def change_direction(self, direction):
        """改变蛇的方向"""
        if direction == "RIGHT" and not self.direction == "LEFT":
            self.direction = "RIGHT"
        elif direction == "LEFT" and not self.direction == "RIGHT":
            self.direction = "LEFT"
        elif direction == "UP" and not self.direction == "DOWN":
            self.direction = "UP"
        elif direction == "DOWN" and not self.direction == "UP":
            self.direction = "DOWN"
    
    def move(self):
        """移动蛇"""
        head = self.get_head_position()
        x, y = head
        
        if self.direction == "RIGHT":
            x += BLOCK_SIZE
        elif self.direction == "LEFT":
            x -= BLOCK_SIZE
        elif self.direction == "DOWN":
            y += BLOCK_SIZE
        elif self.direction == "UP":
            y -= BLOCK_SIZE
            
        # 检查是否超出边界（穿墙）
        if x >= SCREEN_WIDTH:
            x = 0
        elif x < 0:
            x = SCREEN_WIDTH - BLOCK_SIZE
        if y >= SCREEN_HEIGHT:
            y = 0
        elif y < 0:
            y = SCREEN_HEIGHT - BLOCK_SIZE
            
        # 更新蛇的位置
        self.positions.insert(0, (x, y))
        if len(self.positions) > self.length:
            self.positions.pop()
    
    def reset(self):
        """重置蛇"""
        self.length = 1
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        self.score = 0
    
    def draw(self, surface):
        """绘制蛇"""
        for i, p in enumerate(self.positions):
            # 蛇头用不同颜色
            if i == 0:
                pygame.draw.rect(surface, BLUE, pygame.Rect(p[0], p[1], BLOCK_SIZE, BLOCK_SIZE))
            else:
                pygame.draw.rect(surface, self.color, pygame.Rect(p[0], p[1], BLOCK_SIZE, BLOCK_SIZE))
            # 绘制蛇身体的边框
            pygame.draw.rect(surface, BLACK, pygame.Rect(p[0], p[1], BLOCK_SIZE, BLOCK_SIZE), 1)
    
    def handle_keys(self):
        """处理键盘输入"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.change_direction("UP")
                elif event.key == pygame.K_DOWN:
                    self.change_direction("DOWN")
                elif event.key == pygame.K_LEFT:
                    self.change_direction("LEFT")
                elif event.key == pygame.K_RIGHT:
                    self.change_direction("RIGHT")

class Food:
    """定义食物类"""
    
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()
    
    def randomize_position(self):
        """随机生成食物位置"""
        self.position = (
            random.randint(0, (SCREEN_WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE,
            random.randint(0, (SCREEN_HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        )
    
    def draw(self, surface):
        """绘制食物"""
        pygame.draw.rect(surface, self.color, pygame.Rect(self.position[0], self.position[1], BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(surface, BLACK, pygame.Rect(self.position[0], self.position[1], BLOCK_SIZE, BLOCK_SIZE), 1)

class Game:
    """定义游戏类"""
    
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.game_over = False
    
    def is_collision(self, pos1, pos2):
        """检测碰撞"""
        return pos1[0] == pos2[0] and pos1[1] == pos2[1]
    
    def check_self_collision(self):
        """检测蛇是否碰到自己"""
        head = self.snake.get_head_position()
        return head in self.snake.positions[1:]
    
    def render_score(self, surface):
        """显示分数"""
        score_text = font.render(f'得分: {self.snake.score}', True, BLACK)
        surface.blit(score_text, (10, 10))
    
    def render_game_over(self, surface):
        """显示游戏结束信息"""
        game_over_text = font.render('游戏结束! 按R键重新开始', True, RED)
        surface.blit(game_over_text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 30))
    
    def run(self):
        """运行游戏主循环"""
        clock = pygame.time.Clock()
        
        while True:
            if not self.game_over:
                self.snake.handle_keys()
                self.snake.move()
                
                # 检测是否吃到食物
                if self.is_collision(self.snake.get_head_position(), self.food.position):
                    self.snake.length += 1
                    self.snake.score += 10
                    self.food.randomize_position()
                
                # 检测是否碰到自己
                if self.check_self_collision():
                    self.game_over = True
            
            # 处理游戏结束后的按键
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_over:
                        self.game_over = False
                        self.snake.reset()
                        self.food.randomize_position()
            
            # 绘制游戏界面
            screen.fill(WHITE)
            self.snake.draw(screen)
            self.food.draw(screen)
            self.render_score(screen)
            
            if self.game_over:
                self.render_game_over(screen)
            
            pygame.display.update()
            clock.tick(SNAKE_SPEED)

# 创建游戏实例并运行
if __name__ == "__main__":
    game = Game()
    game.run()
