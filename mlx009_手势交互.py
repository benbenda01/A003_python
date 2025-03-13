#####################################################
# �˳���Ϊ:09 �����ƻ���
#####################################################

import cv2
import HandTrackingModule as htm
import os
import numpy as np


folderPath = "PainterImg/"
mylist = os.listdir(folderPath)
overlayList = []
for imPath in mylist:
    image = cv2.imread(f'{folderPath}/{imPath}')
    overlayList.append(image)
header = overlayList[0]
color = [255, 0, 0]                                 # ��ɫ�趨
brushThickness = 15                                 # ���ʿ��
eraserThickness = 40                                # ��Ƥ���

cap = cv2.VideoCapture(0)                           # ��ʹ�ñʼǱ��Դ�����ͷ����Ϊ0  ��ʹ���������ͷ �����Ϊ1���������
cap.set(3, 1280)                                    # ��ϵͳ�ֱ��ʻ�����Ȧ����1300 ��700�Ĳ�׽��
cap.set(4, 720)

detector = htm.handDetector()                       # �������Ƽ�⺯��
xp, yp = 0, 0                                       #
imgCanvas = np.zeros((720, 1280, 3), np.uint8)      # �½�һ������

while True:                                     # 1.import image
    success, img = cap.read()                       # ͼƬ�Ƿ�ɹ�����֡ͼ��img
    img = cv2.flip(img, 1)                          # ��תͼ���е��Լ� 1����ˮƽ,0������ֱ��ת

    img = detector.findHands(img)               # 2.find hand landmarks
    lmList = detector.findPosition(img, draw=True)

    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        fingers = detector.fingersUp()          # 3. Check which fingers are up

        if fingers[1] and fingers[2]:           # 4. If Selection Mode �C Two finger are up
            if y1 < 153:
                if 0 < x1 < 320:
                    header = overlayList[0]
                    color = [50, 128, 250]
                elif 320 < x1 < 640:
                    header = overlayList[1]
                    color = [0, 0, 255]
                elif 640 < x1 < 960:
                    header = overlayList[2]
                    color = [0, 255, 0]
                elif 960 < x1 < 1280:
                    header = overlayList[3]
                    color = [0, 0, 0]
        img[0:1280][0:153] = header

        if fingers[1] and fingers[2] == False:    # 5. If Drawing Mode �C Index finger is up
            cv2.circle(img, (x1, y1), 15, color, cv2.FILLED)
            print("Drawing Mode")
            if xp == 0 and yp == 0:
                xp, yp = x1, y1

            if color == [0, 0, 0]:
                cv2.line(img, (xp, yp), (x1, y1), color, eraserThickness)  # ??
                cv2.line(imgCanvas, (xp, yp), (x1, y1), color, eraserThickness)
            else:
                cv2.line(img, (xp, yp), (x1, y1), color, brushThickness)   # ??
                cv2.line(imgCanvas, (xp, yp), (x1, y1), color, brushThickness)

        xp, yp = x1, y1
        # Clear Canvas when all fingers are up
        # if all (x >= 1 for x in fingers):
        #     imgCanvas = np.zeros((720, 1280, 3), np.uint8)
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)      # ʵʱ��ʾ���ʹ켣��ʵ��
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)
    img[0:1280][0:153] = header

    cv2.imshow("Image", img)
    # cv2.imshow("Canvas", imgCanvas)
    # cv2.imshow("Inv", imgInv)
    k = cv2.waitKey(1)                      # ����λ�Ƿ���
    if k == ord('q'):                       # ����Ǽ�λQ������
        break                               # �˳�ѭ��
cap.release()                               # �˳�����ͷ
cv2.destroyAllWindows()                     # �ر������Ӵ�

cv2.destroyAllWindows()                     # �ر������Ӵ�