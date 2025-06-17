#############################################################
import cv2
import mediapipe as mp
import math
import os
#############################################################

class HandDetector:

    def __init__(self,mode=False, max_hands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = max_hands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.model_complexity = 0

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.model_complexity, self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw = True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img,self.results
    
    def findPosition(self, img, handNo=0, draw =True):
            lmList = []
            if self.results.multi_hand_landmarks:
                myHand = self.results.multi_hand_landmarks[handNo]
                for handLms in self.results.multi_hand_landmarks:
                    for id, lm in enumerate(handLms.landmark):
                        h, w, c = img.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        lmList.append([id,cx,cy])
            return lmList

    
"""
def main():
    cap = cv2.VideoCapture(0)
    detector = handDetector()

    while True:
        success, img = cap.read()
        img, results = detector.findHands(img, draw=False)
        lmList = detector.findPosition(img)
        if len(lmList)!=0: print(lmList[4], lmList[0])
        cv2.imshow("Image", img)
        cv2.waitKey(1)
"""

def num_to_range(num, inMin, inMax, outMin, outMax):
  return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax - outMin))


#####################
wCam, hCam = 320, 240
#####################

def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
    detector = HandDetector(detectionCon = 0.9)

    while True:
        success, img = cap.read()
        img, results = detector.findHands(img,draw=True)
        lmList = detector.findPosition(img, draw=False)
        if len(lmList)!=0:
            print(lmList[4], lmList[8])

            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            cx, cy = (x1 + x2)//2, (y1 + y2)//2
            print(lmList)

            cv2.circle(img, (x1,y1), 10, (0,255,0), cv2.FILLED)
            cv2.circle(img, (x2,y2), 10, (0,255,0), cv2.FILLED)
            cv2.line(img, (x1,y1), (x2,y2), (255,255,0), 3)
            cv2.circle(img, (cx,cy), 10, (0,255,255), cv2.FILLED)

            length = math.hypot(x2-x1, y2-y1)
            print(length)

            #Hand Range: 5 - 100
            n = num_to_range(length,0,125,0,100)
            os.system('SoundVolumeView.exe /SetVolume "2- High Definition Audio Device\Device\Speakers" {0}'.format(n))        

            if length < 30:
                cv2.circle(img, (cx,cy), 10, (0,0,255), cv2.FILLED)
            if length > 70:
                cv2.circle(img, (cx,cy), 10, (0,255,0), cv2.FILLED)
            if length > 90:
                cv2.circle(img, (cx,cy), 10, (255,255,255), cv2.FILLED)
            if length < 15:
                cv2.circle(img, (cx,cy), 10, (0,0,0), cv2.FILLED)
        cv2.imshow("Image", img)
        cv2.waitKey(1) 


###############################################################################################################
if __name__ =="__main__":
    main()
##############################################################################################################

