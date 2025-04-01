#####################################################
# 此程序为:mlx010 绘制小老虎程序
#####################################################

import turtle
import math

# 设置窗口
def setup_screen():
    screen = turtle.Screen()
    screen.title("小老虎绘制")
    screen.setup(800, 600)
    screen.bgcolor("white")
    return screen

# 创建画笔
def create_pen():
    pen = turtle.Turtle()
    pen.speed(0)  # 最快速度
    pen.hideturtle()  # 隐藏画笔
    return pen

# 绘制圆形
def draw_circle(pen, x, y, radius, color="black", fill_color=None):
    pen.penup()
    pen.goto(x, y - radius)  # 移动到圆的底部
    if fill_color:
        pen.fillcolor(fill_color)
        pen.begin_fill()
    pen.pendown()
    pen.circle(radius)
    if fill_color:
        pen.end_fill()

# 绘制椭圆
def draw_oval(pen, x, y, width, height, color="black", fill_color=None):
    pen.penup()
    pen.goto(x, y)
    pen.pencolor(color)
    if fill_color:
        pen.fillcolor(fill_color)
        pen.begin_fill()
    pen.pendown()
    
    # 使用参数方程绘制椭圆
    for i in range(361):
        angle = math.radians(i)
        px = x + width * math.sin(angle)
        py = y + height * math.cos(angle)
        pen.goto(px, py)
    
    if fill_color:
        pen.end_fill()

# 绘制三角形
def draw_triangle(pen, x1, y1, x2, y2, x3, y3, color="black", fill_color=None):
    pen.penup()
    pen.goto(x1, y1)
    pen.pencolor(color)
    if fill_color:
        pen.fillcolor(fill_color)
        pen.begin_fill()
    pen.pendown()
    pen.goto(x2, y2)
    pen.goto(x3, y3)
    pen.goto(x1, y1)
    if fill_color:
        pen.end_fill()

# 绘制老虎条纹
def draw_stripes(pen, x, y, width, height, color="black"):
    pen.pencolor(color)
    pen.pensize(3)
    
    # 绘制身体上的条纹
    for i in range(-2, 3):
        pen.penup()
        pen.goto(x - width/4, y + i * 15)
        pen.pendown()
        pen.goto(x + width/4, y + i * 15 + 10)

# 绘制老虎头部
def draw_tiger_head(pen):
    # 绘制头部轮廓
    draw_circle(pen, 0, 100, 80, "black", "orange")
    
    # 绘制耳朵
    draw_triangle(pen, -60, 160, -40, 200, -20, 160, "black", "orange")
    draw_triangle(pen, 60, 160, 40, 200, 20, 160, "black", "orange")
    
    # 绘制内耳
    draw_triangle(pen, -50, 165, -40, 190, -30, 165, "black", "#FFC0CB")
    draw_triangle(pen, 50, 165, 40, 190, 30, 165, "black", "#FFC0CB")
    
    # 绘制眼睛
    draw_circle(pen, -30, 120, 10, "black", "white")
    draw_circle(pen, 30, 120, 10, "black", "white")
    draw_circle(pen, -30, 120, 5, "black", "black")
    draw_circle(pen, 30, 120, 5, "black", "black")
    
    # 绘制鼻子
    draw_circle(pen, 0, 90, 10, "black", "black")
    
    # 绘制嘴巴
    pen.penup()
    pen.goto(0, 90)
    pen.pendown()
    pen.pencolor("black")
    pen.pensize(2)
    pen.goto(0, 70)
    
    # 绘制胡须
    pen.penup()
    pen.goto(-10, 80)
    pen.pendown()
    pen.goto(-40, 85)
    
    pen.penup()
    pen.goto(-10, 75)
    pen.pendown()
    pen.goto(-40, 70)
    
    pen.penup()
    pen.goto(10, 80)
    pen.pendown()
    pen.goto(40, 85)
    
    pen.penup()
    pen.goto(10, 75)
    pen.pendown()
    pen.goto(40, 70)
    
    # 绘制脸部条纹
    pen.pencolor("black")
    pen.pensize(3)
    
    # 左脸条纹
    pen.penup()
    pen.goto(-60, 100)
    pen.pendown()
    pen.goto(-40, 90)
    
    pen.penup()
    pen.goto(-65, 85)
    pen.pendown()
    pen.goto(-45, 75)
    
    # 右脸条纹
    pen.penup()
    pen.goto(60, 100)
    pen.pendown()
    pen.goto(40, 90)
    
    pen.penup()
    pen.goto(65, 85)
    pen.pendown()
    pen.goto(45, 75)

# 绘制老虎身体
def draw_tiger_body(pen):
    # 绘制身体
    draw_oval(pen, 0, 0, 100, 60, "black", "orange")
    
    # 绘制条纹
    draw_stripes(pen, 0, 0, 200, 120, "black")
    
    # 绘制四肢
    # 前腿
    pen.penup()
    pen.goto(-60, -20)
    pen.pendown()
    pen.pensize(20)
    pen.pencolor("orange")
    pen.goto(-60, -80)
    
    pen.penup()
    pen.goto(60, -20)
    pen.pendown()
    pen.pensize(20)
    pen.pencolor("orange")
    pen.goto(60, -80)
    
    # 后腿
    pen.penup()
    pen.goto(-40, -40)
    pen.pendown()
    pen.pensize(20)
    pen.pencolor("orange")
    pen.goto(-40, -100)
    
    pen.penup()
    pen.goto(40, -40)
    pen.pendown()
    pen.pensize(20)
    pen.pencolor("orange")
    pen.goto(40, -100)
    
    # 绘制爪子
    for x in [-60, 60, -40, 40]:
        y = -80 if x in [-60, 60] else -100
        pen.penup()
        pen.goto(x, y)
        pen.pendown()
        pen.pensize(1)
        pen.pencolor("black")
        pen.fillcolor("black")
        pen.begin_fill()
        pen.circle(5)
        pen.end_fill()
    
    # 绘制尾巴
    pen.penup()
    pen.goto(0, -40)
    pen.pendown()
    pen.pensize(8)
    pen.pencolor("orange")
    for i in range(20):
        pen.goto(i*5, -40 - math.sin(i/2) * 20)
    
    # 尾巴尖
    pen.penup()
    pen.goto(95, -40)
    pen.pendown()
    pen.pensize(1)
    pen.pencolor("black")
    pen.fillcolor("black")
    pen.begin_fill()
    pen.circle(8)
    pen.end_fill()

# 主函数
def main():
    screen = setup_screen()
    pen = create_pen()
    
    # 绘制标题
    pen.penup()
    pen.goto(0, 200)
    pen.pendown()
    pen.pencolor("black")
    pen.write("小老虎", align="center", font=("Arial", 24, "bold"))
    
    # 绘制老虎
    draw_tiger_body(pen)
    draw_tiger_head(pen)
    
    # 等待用户点击关闭窗口
    screen.exitonclick()

if __name__ == "__main__":
    main()