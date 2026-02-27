import cv2
import mediapipe as mp
import math
import numpy as np
import time
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


# ===================== MAIN FUNCTION =====================
def run_volume():

    # ---------------- AUDIO SETUP ----------------
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_,
        CLSCTX_ALL,
        None
    )
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    minVol, maxVol, _ = volume.GetVolumeRange()

    # ---------------- MEDIAPIPE ----------------
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils

    # ---------------- CAMERA ----------------
    wCam, hCam = 640, 480
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)

    # ---------------- UI CONSTANTS ----------------
    BAR_X, BAR_Y = 50, 100
    BAR_WIDTH, BAR_HEIGHT = 40, 300

    HAND_COLOR = (0, 255, 255)
    BAR_COLOR = (0, 255, 0)
    LOCKED_BAR_COLOR = (255, 165, 0)
    TEXT_COLOR = (255, 255, 255)
    BG_COLOR = (40, 40, 40)
    LOCK_COLOR = (255, 215, 0)

    # ---------------- STATES ----------------
    smoothness = 5
    pTime = 0

    volume_locked = False
    locked_volume = None
    lock_cooldown = 0
    COOLDOWN_FRAMES = 30

    peace_sign_counter = 0
    PEACE_SIGN_THRESHOLD = 30

    print("Advanced Volume Control Started (Press Q to exit)")

    # ---------------- GESTURE DETECTORS ----------------
    def detect_peace_sign(lmList):
        if len(lmList) < 21:
            return False
        return (
            lmList[8][2] < lmList[6][2] - 20 and
            lmList[12][2] < lmList[10][2] - 20 and
            lmList[16][2] > lmList[14][2] and
            lmList[20][2] > lmList[18][2]
        )

    def detect_thumbs_up(lmList):
        if len(lmList) < 21:
            return False
        return (
            lmList[4][2] < lmList[3][2] - 30 and
            lmList[8][2] > lmList[6][2] and
            lmList[12][2] > lmList[10][2] and
            lmList[16][2] > lmList[14][2] and
            lmList[20][2] > lmList[18][2]
        )

    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    ) as hands:

        while cap.isOpened():

            success, img = cap.read()
            if not success:
                break

            img = cv2.flip(img, 1)
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            lmList = []

            if result.multi_hand_landmarks:
                hand = result.multi_hand_landmarks[0]
                mp_draw.draw_landmarks(img, hand, mp_hands.HAND_CONNECTIONS)

                for id, lm in enumerate(hand.landmark):
                    cx, cy = int(lm.x * wCam), int(lm.y * hCam)
                    lmList.append([id, cx, cy])

            # ---------------- CONTROL LOGIC ----------------
            if lmList:

                is_peace = detect_peace_sign(lmList)
                is_thumbs_up = detect_thumbs_up(lmList)

                # Lock / Unlock
                if is_peace and lock_cooldown == 0:
                    peace_sign_counter += 1
                    if peace_sign_counter >= PEACE_SIGN_THRESHOLD:
                        volume_locked = not volume_locked
                        if volume_locked:
                            locked_volume = volume.GetMasterVolumeLevel()
                        else:
                            locked_volume = None
                        peace_sign_counter = 0
                        lock_cooldown = COOLDOWN_FRAMES
                else:
                    peace_sign_counter = max(0, peace_sign_counter - 2)

                # Max volume
                if is_thumbs_up and not volume_locked:
                    volume.SetMasterVolumeLevel(maxVol, None)

                # Pinch adjust
                if not is_peace and not is_thumbs_up:
                    x1, y1 = lmList[4][1], lmList[4][2]
                    x2, y2 = lmList[8][1], lmList[8][2]

                    length = math.hypot(x2 - x1, y2 - y1)

                    if not volume_locked:
                        vol = np.interp(length, [40, 220], [minVol, maxVol])
                        vol = round(vol / smoothness) * smoothness
                        volume.SetMasterVolumeLevel(vol, None)
                    else:
                        volume.SetMasterVolumeLevel(locked_volume, None)

                # Draw volume bar
                current_vol = volume.GetMasterVolumeLevel()
                volBar = np.interp(current_vol, [minVol, maxVol], [BAR_HEIGHT, 0])
                volPer = np.interp(current_vol, [minVol, maxVol], [0, 100])

                bar_color = LOCKED_BAR_COLOR if volume_locked else BAR_COLOR

                cv2.rectangle(img, (BAR_X, BAR_Y),
                              (BAR_X + BAR_WIDTH, BAR_Y + BAR_HEIGHT),
                              BG_COLOR, 2)

                cv2.rectangle(img,
                              (BAR_X, int(BAR_Y + volBar)),
                              (BAR_X + BAR_WIDTH, BAR_Y + BAR_HEIGHT),
                              bar_color, -1)

                cv2.putText(img, f'{int(volPer)} %',
                            (BAR_X - 10, BAR_Y + BAR_HEIGHT + 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                            TEXT_COLOR, 2)

            # Cooldown update
            if lock_cooldown > 0:
                lock_cooldown -= 1

            # FPS
            cTime = time.time()
            fps = 1 / (cTime - pTime) if cTime != pTime else 0
            pTime = cTime

            cv2.putText(img, f'FPS: {int(fps)}',
                        (500, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (0, 255, 0), 2)

            cv2.imshow("Advanced Gesture Volume Control", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    print("Volume mode stopped.")
