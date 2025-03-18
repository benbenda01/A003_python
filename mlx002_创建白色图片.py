#####################################################
# 此程序为:mlx002 初学 使用opencv库和numpy库创建纯白色图片
#####################################################

import cv2                                    # 导入OpenCV库
import numpy as np                            # 导入numpy库

data = np.ones((200, 200, 3), np.uint8)*255       # 创建白色图片
cv2.imshow("dataImg", data)                       # 显示图片
cv2.waitKey(0)                                    # 等待按键输入
cv2.destroyAllWindows()                           # 检测到按键按下后，销毁所有窗口