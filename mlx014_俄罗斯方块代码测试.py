import sys
import pygame
import random

pygame.init()

# 设置屏幕大小
screen = pygame.display.set_mode((800, 600))

# 设置颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 设置字体
font = pygame.font.Font(None, 36)

# 设置速度
clock = pygame.time.Clock()

# 定义方块类
class Block(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()

# 定义方块组
block_list = pygame.sprite.Group()
all_sprites_list = pygame.sprite.Group()

for i in range(50):
    block = Block(WHITE, 20, 15)
    block.rect.x = random.randint(0, 780)
    block.rect.y = random.randint(0, 580)
    block_list.add(block)
    all_sprites_list.add(block)

player = Block(BLACK, 20, 15)
all_sprites_list.add(player)

done = False
score = 0

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.rect.x -= 5
    if keys[pygame.K_RIGHT]:
        player.rect.x += 5
    if keys[pygame.K_UP]:
        player.rect.y -= 5
    if keys[pygame.K_DOWN]:
        player.rect.y += 5

    screen.fill(WHITE)

    blocks_hit_list = pygame.sprite.spritecollide(player, block_list, True)

    for block in blocks_hit_list:
        score += 1
        print(score)

    all_sprites_list.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
