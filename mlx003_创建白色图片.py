import cv2                                    # ����Opencv-pythonͼƬ�༭��
import numpy as np                            # ����numpy���鴦���

data = np.ones((200, 200, 3), np.uint8)*255   # ��һ�Ű�ɫͼƬ
cv2.imwrite(r"D:\mlx.png", data)              # ����ͼƬ
cv2.imshow("dataImg", data)                   # ��ʾͼƬ
cv2.waitKey(0)                                # ������������
cv2.destroyAllWindows()                       # ��⵽����������£��ݻ���ʾͼƬ��������
