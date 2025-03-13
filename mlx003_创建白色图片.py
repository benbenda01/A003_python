import cv2                                    # 导入Opencv-python图片编辑库
import numpy as np                            # 导入numpy数组处理库

data = np.ones((200, 200, 3), np.uint8)*255   # 建一张白色图片
cv2.imwrite(r"D:\mlx.png", data)              # 保存图片
cv2.imshow("dataImg", data)                   # 显示图片
cv2.waitKey(0)                                # 按下任意键检测
cv2.destroyAllWindows()                       # 检测到有任意键按下，摧毁显示图片结束程序
