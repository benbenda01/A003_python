#####################################################
# �˳���Ϊ:07 ʶ������ �����ֺ�ͼƬȷ������
#####################################################
import cv2
import HandTrackingModule as htm
import time

#############################
wCam, hCam = 640, 480
#############################
cap = cv2.VideoCapture(0)                          # ��ʹ�ñʼǱ��Դ�����ͷ����Ϊ0  ��ʹ���������ͷ �����Ϊ1���������
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
detector = htm.handDetector()

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    pointList = [4, 8, 12, 16, 20]
    if len(lmList) != 0:
        countList = []                            # ��Ĵָ
        if lmList[4][1] > lmList[3][1]:
            countList.append(1)
        else:
            countList.append(0)                   # �����ĸ���ָ
        for i in range(1, 5):
            if lmList[pointList[i]][2] < lmList[pointList[i] - 2][2]:
                countList.append(1)
            else:
                countList.append(0)               # print(countList)

        count = countList.count(1)                # ���б��к��е�1����
        HandImage = cv2.imread(f'FingerImg/{count}.jpg')
        HandImage = cv2.resize(HandImage, (150, 200))
        h, w, c = HandImage.shape
        img[0:h, 0:w] = HandImage
        cv2.putText(img, f'{int(count)}', (15, 400), cv2.FONT_HERSHEY_PLAIN, 15, (255, 0, 255), 10)


    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'fps: {int(fps)}', (600, 40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

    cv2.imshow("Image", img)
    k = cv2.waitKey(1)  # ����λ�Ƿ���
    if k == ord('q'):  # ����Ǽ�λQ������
        break  # �˳�ѭ��
cap.release()  # �˳�����ͷ
cv2.destroyAllWindows()  # �ر������Ӵ�
