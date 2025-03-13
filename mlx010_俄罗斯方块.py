import pygame
import random

# 定义窗口相关参数
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GAME_WIDTH = 300
GAME_HEIGHT = 600
TOP_LEFT_X = (WINDOW_WIDTH - GAME_WIDTH) // 2
TOP_LEFT_Y = WINDOW_HEIGHT - GAME_HEIGHT

# 定义方块大小
BLOCK_SIZE = 30

# 定义方块颜色
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 128, 0)
GRAY = (128, 128, 128)

# 定义方块形状，共7种不同的形状
I_BLOCK = [[1, 1, 1, 1]]
J_BLOCK = [[1, 0, 0], [1, 1, 1]]
L_BLOCK = [[0, 0, 1], [1, 1, 1]]
O_BLOCK = [[1, 1], [1, 1]]
S_BLOCK = [[0, 1, 1], [1, 1, 0]]
T_BLOCK = [[0, 1, 0], [1, 1, 1]]
Z_BLOCK = [[1, 1, 0], [0, 1, 1]]
BLOCKS = [I_BLOCK, J_BLOCK, L_BLOCK, O_BLOCK, S_BLOCK, T_BLOCK, Z_BLOCK]

# 初始化pygame模块
pygame.init()

# 创建游戏窗口
game_screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tetris")

# 加载字体
font = pygame.font.SysFont(None, 25)

class Block:
    """定义方块类"""

    def __init__(self, x, y, shape, color):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = color
        self.rotation = 0

    def get_block(self):
        """返回当前方块形状"""
        return self.shape[self.rotation % len(self.shape)]

    def move_down(self):
        """向下移动方块"""
        self.y += BLOCK_SIZE

    def move_left(self):
        """向左移动方块"""
        self.x -= BLOCK_SIZE

    def move_right(self):
        """向右移动方块"""
        self.x += BLOCK_SIZE

    def rotate(self):
        """旋转方块"""
        self.rotation += 1

    def draw(self):
        """将方块绘制到游戏窗口上"""
        shape_to_draw = self.get_block()

        for i, row in enumerate(shape_to_draw):
            for j, col in enumerate(row):
                if col == 1:
                    pygame.draw.rect(game_screen, self.color, (self.x + j * BLOCK_SIZE, self.y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

class Game:
    """定义游戏类"""

    def __init__(self):
        self.score = 0
        self.level = 1
        self.speed = 500
        self.current_block = None
        self.next_block = self.get_random_block()
        self.blocks = []
        self.game_over = False

    def start_new_game(self):
        """开始新游戏"""
        self.score = 0
        self.level = 1
        self.speed = 500
        self.current_block = None
        self.next_block = self.get_random_block()
        self.blocks = []
        self.game_over = False

    def get_random_block(self):
        """获取一个随机方块"""
        block_shape = random.choice(BLOCKS)
        return Block(TOP_LEFT_X + GAME_WIDTH // 2 - BLOCK_SIZE, TOP_LEFT_Y, block_shape, random.choice([WHITE, BLUE, RED, GREEN, YELLOW, CYAN, ORANGE, GRAY]))

    def check_collision(self):
        """检查方块是否碰撞到已有方块"""
        for block in self.blocks:
            for i, row in enumerate(self.current_block.get_block()):
                for j, col in enumerate(row):
                    if col == 1:
                        x = self.current_block.x + j * BLOCK_SIZE
                        y = self.current_block.y + i * BLOCK_SIZE
                        if block.x == x and block.y == y:
                            return True
        return False

    def check_rows_for_removal(self):
        """检查是否需要移除填满的行"""
        for i in range(GAME_HEIGHT // BLOCK_SIZE):
            row_blocks = []
            for block in self.blocks:
                if block.y == TOP_LEFT_Y + i * BLOCK_SIZE:
                    row_blocks.append(block)
            if len(row_blocks) == GAME_WIDTH // BLOCK_SIZE:
                for block in row_blocks:
                    self.blocks.remove(block)
                self.score += 10
                self.speed -= 10
                self.level = self.score // 100 + 1

    def draw_game_screen(self):
        """绘制游戏画面"""
        game_screen.fill((0, 0, 0))
        pygame.draw.rect(game_screen, (255, 255, 255), (TOP_LEFT_X, TOP_LEFT_Y, GAME_WIDTH, GAME_HEIGHT), 5)
        pygame.draw.rect(game_screen, (255, 255, 255), (TOP_LEFT_X + GAME_WIDTH + 50, TOP_LEFT_Y, 150, 150), 5)
        pygame.draw.line(game_screen, (255, 255, 255), (TOP_LEFT_X + GAME_WIDTH, TOP_LEFT_Y), (TOP_LEFT_X + GAME_WIDTH, TOP_LEFT_Y + GAME_HEIGHT))

        # 绘制已下落方块
        for block in self.blocks:
            block.draw()

        # 绘制当前方块
        if self.current_block:
            self.current_block.draw()

        # 绘制下一个方块
        next_block_text = font.render("Next block:", True, (255, 255, 255))
        game_screen.blit(next_block_text, (TOP_LEFT_X + GAME_WIDTH + 10, TOP_LEFT_Y + 10))
        pygame.draw.rect(game_screen, self.next_block.color, (TOP_LEFT_X + GAME_WIDTH + 10, TOP_LEFT_Y + 50, BLOCK_SIZE * 3, BLOCK_SIZE * 3), 0)
        next_block_shape = self.next_block.get_block()
        for i, row in enumerate(next_block_shape):
            for j, col in enumerate(row):
                if col == 1:
                    pygame.draw.rect(game_screen, self.next_block.color, (TOP_LEFT_X + GAME_WIDTH + 10 + j * BLOCK_SIZE, TOP_LEFT_Y + 50 + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

        # 绘制分数
        score_text = font.render("Score: " + str(self.score), True, (255, 255, 255))
        game_screen.blit(score_text, (TOP_LEFT_X + GAME_WIDTH + 10, TOP_LEFT_Y + 120))

        # 绘制等级
        level_text = font.render("Level: " + str(self.level), True, (255, 255, 255))
        game_screen.blit(level_text, (TOP_LEFT_X + GAME_WIDTH + 10, TOP_LEFT_Y + 160))

        # 绘制游戏结束信息
        if self.game_over:
            game_over_text = font.render("Game Over!", True, (255, 0, 0))
            game_screen.blit(game_over_text, (TOP_LEFT_X + GAME_WIDTH // 4, TOP_LEFT_Y + GAME_HEIGHT // 2))

    def run_game(self):
        """运行游戏主循环"""
        clock = pygame.time.Clock()
        self.start_new_game()

        while True:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if not self.game_over:
                        if event.key == pygame.K_LEFT:
                            self.current_block.move_left()
                            if self.check_collision():
                                self.current_block.move_right()
                        elif event.key == pygame.K_RIGHT:
                            self.current_block.move_right()
                            if self.check_collision():
                                self.current_block.move_left()
                        elif event.key == pygame.K_DOWN:
                            self.current_block.move_down()
                            if self.check_collision():
                                self.current_block.move_up()
                        elif event.key == pygame.K_UP:
                            self.current_block.rotate()

            if not self.game_over:
                if not self.current_block:
                    self.current_block = self.next_block
                    self.next_block = self.get_random_block()

                self.current_block.move_down()
                if self.check_collision():
                    self.current_block.move_up()
                    self.blocks.append(self.current_block)
                    self.current_block = None
                    self.check_rows_for_removal()
                    if self.check_collision():
                        self.game_over = True

            self.draw_game_screen()
            pygame.display.update()

    def quit_game(self):
        """退出游戏"""
        pygame.quit()
        quit()

if __name__ == '__main__':
    game = Game()
    game.run_game()

