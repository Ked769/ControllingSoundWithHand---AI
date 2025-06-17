#############################################################
import cv2 # type: ignore
import mediapipe as mp # type: ignore
import math
import os
import sys # type: ignore
import platform
#############################################################

IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"

if IS_WINDOWS:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL # type: ignore
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume # type: ignore

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

def num_to_range(num, inMin, inMax, outMin, outMax):
    return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax - outMin))

#####################
wCam, hCam = 320, 240
#####################

def set_volume_windows(vol):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevel(vol, None)

def get_volume_range_windows():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    return volume.GetVolumeRange()

def set_volume_linux(vol_percentage):
    # Example using amixer (ALSA). Requires amixer installed.
    # You may need to adjust 'Master' to your system's mixer name.
    try:
        os.system(f"amixer -D pulse sset Master {int(vol_percentage)}%")
    except Exception as e:
        print(f"Could not set volume: {e}")

def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
    detector = HandDetector(detectionCon = 0.9)

    if IS_WINDOWS:
        minVol, maxVol, _ = get_volume_range_windows()
    else:
        minVol, maxVol = 0, 100  # Linux: use 0-100%

    smoothing = 5
    previous_vol = 0

    while True:
        success, img = cap.read()
        img, results = detector.findHands(img,draw=True)
        lmList = detector.findPosition(img, draw=False)
        if len(lmList)!=0:
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            cx, cy = (x1 + x2)//2, (y1 + y2)//2

            cv2.circle(img, (x1,y1), 10, (0,255,0), cv2.FILLED)
            cv2.circle(img, (x2,y2), 10, (0,255,0), cv2.FILLED)
            cv2.line(img, (x1,y1), (x2,y2), (255,255,0), 3)
            cv2.circle(img, (cx,cy), 10, (0,255,255), cv2.FILLED)

            length = math.hypot(x2-x1, y2-y1)

            # Adjusted hand range: 15 - 150 for more sensitivity
            vol = num_to_range(length, 15, 150, minVol, maxVol)
            vol = min(maxVol, max(minVol, vol))  # Ensure volume stays within bounds
            
            # Apply smoothing
            vol = (vol + previous_vol * (smoothing - 1)) / smoothing
            previous_vol = vol

            if IS_WINDOWS:
                set_volume_windows(vol)
                volPercentage = int(num_to_range(vol, minVol, maxVol, 0, 100))
            else:
                volPercentage = int(vol)
                set_volume_linux(volPercentage)

            # Adjust visual feedback ranges
            if length < 20:
                cv2.circle(img, (cx,cy), 10, (0,0,255), cv2.FILLED)  # Very low
            elif length < 50:
                cv2.circle(img, (cx,cy), 10, (0,165,255), cv2.FILLED)  # Low
            elif length < 100:
                cv2.circle(img, (cx,cy), 10, (0,255,0), cv2.FILLED)  # Medium
            else:
                cv2.circle(img, (cx,cy), 10, (255,255,255), cv2.FILLED)  # High

            # Display volume percentage
            cv2.putText(img, f'{volPercentage}%', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                       1, (255, 0, 0), 2)

        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == 27:  # ESC key to kill/exit
            break

    cap.release()
    cv2.destroyAllWindows()

###############################################################################################################
if __name__ =="__main__":
    main()
###############################################################################################################