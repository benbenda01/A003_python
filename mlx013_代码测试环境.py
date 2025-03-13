import turtle

# 设置画布大小
turtle.setup(1000, 600)

# 画蓝色天空
turtle.bgcolor('skyblue')

# 画绿色草地
turtle.penup()
turtle.goto(-500, -300)
turtle.pendown()
turtle.color('green')
turtle.begin_fill()
turtle.forward(1000)
turtle.right(90)
turtle.forward(600)
turtle.right(90)
turtle.forward(1000)
turtle.right(90)
turtle.forward(600)
turtle.end_fill()

# 画树 trunk
turtle.pensize(20)
turtle.color('brown')
turtle.penup()
turtle.goto(-100, -300)
turtle.pendown()
turtle.forward(50)

# 画树冠
turtle.pensize(5)
turtle.color('green')
turtle.penup()
turtle.goto(-150, -200)
turtle.pendown()
turtle.circle(80)

# 画太阳
turtle.penup()
turtle.goto(400, 250)
turtle.pendown()
turtle.color('yellow')
turtle.begin_fill()
turtle.circle(50)
turtle.end_fill()

# 画白云
turtle.penup()
turtle.goto(-200, 200)
turtle.pendown()
turtle.color('white')
turtle.pensize(3)
turtle.circle(30)

turtle.penup()
turtle.goto(-100, 180)
turtle.pendown()
turtle.circle(20)

# 画两只小兔子
# 第一只兔子
turtle.penup()
turtle.goto(-250, -50)
turtle.pendown()
turtle.pensize(2)
turtle.color('white')
turtle.begin_fill()
turtle.circle(15)
turtle.end_fill()

turtle.penup()
turtle.goto(-260, -40)
turtle.pendown()
turtle.color('pink')
turtle.begin_fill()
turtle.circle(5)
turtle.end_fill()

# 第二只兔子
turtle.penup()
turtle.goto(-200, -100)
turtle.pendown()
turtle.pensize(2)
turtle.color('white')
turtle.begin_fill()
turtle.circle(15)
turtle.end_fill()

turtle.penup()
turtle.goto(-210, -90)
turtle.pendown()
turtle.color('pink')
turtle.begin_fill()
turtle.circle(5)
turtle.end_fill()

turtle.hideturtle()
turtle.done()