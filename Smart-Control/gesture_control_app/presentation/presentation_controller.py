import cv2
import mediapipe as mp
import pyautogui
import time
import numpy as np
from collections import deque


def run_presentation():

    # ================= CONFIG =================
    CAM_INDEX = 0
    CAM_WIDTH = 640
    CAM_HEIGHT = 480
    HOLD_TIME = 1.0
    COOLDOWN_TIME = 0.8
    GESTURE_BUFFER = 5

    pyautogui.FAILSAFE = False

    # ================= GESTURE MAP =================
    GESTURE_ACTIONS = {
        "NEXT": lambda: pyautogui.press("right"),
        "PREVIOUS": lambda: pyautogui.press("left"),
        "START": lambda: pyautogui.press("f5"),
        "EXIT": lambda: pyautogui.press("esc"),
        "FIST": lambda: pyautogui.press("esc"),
    }

    # ================= MEDIAPIPE =================
    mpHands = mp.solutions.hands
    mpDraw = mp.solutions.drawing_utils
    mpStyles = mp.solutions.drawing_styles

    hands = mpHands.Hands(
        static_image_mode=False,
        model_complexity=0,
        max_num_hands=1,
        min_detection_confidence=0.65,
        min_tracking_confidence=0.65,
    )

    cap = cv2.VideoCapture(CAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)

    gesture_buffer = deque(maxlen=GESTURE_BUFFER)
    current_gesture = ""
    gesture_start = 0
    cooldown_until = 0

    print("[Presentation Mode] Running — Press ESC to exit.")

    def fingers_up(lms, handedness):
        fingers = []

        if handedness == "Right":
            fingers.append(1 if lms.landmark[4].x < lms.landmark[3].x else 0)
        else:
            fingers.append(1 if lms.landmark[4].x > lms.landmark[3].x else 0)

        for tip in [8, 12, 16, 20]:
            fingers.append(1 if lms.landmark[tip].y < lms.landmark[tip - 2].y else 0)

        return fingers

    def classify_gesture(f):
        if f == [0, 1, 0, 0, 0]: return "NEXT"
        if f == [0, 1, 1, 0, 0]: return "PREVIOUS"
        if f == [0, 1, 1, 1, 0]: return "START"
        if f == [1, 0, 0, 0, 0]: return "EXIT"
        if f == [0, 0, 0, 0, 0]: return "FIST"
        return ""

    def stable_gesture(raw):
        gesture_buffer.append(raw)
        if len(gesture_buffer) < GESTURE_BUFFER:
            return ""
        if all(g == raw for g in gesture_buffer) and raw != "":
            return raw
        return ""

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        gesture = ""
        now = time.time()

        if result.multi_hand_landmarks and result.multi_handedness:
            for handLms, handInfo in zip(
                result.multi_hand_landmarks,
                result.multi_handedness
            ):
                side = handInfo.classification[0].label

                mpDraw.draw_landmarks(
                    img, handLms,
                    mpHands.HAND_CONNECTIONS,
                    mpStyles.get_default_hand_landmarks_style(),
                    mpStyles.get_default_hand_connections_style(),
                )

                fingers = fingers_up(handLms, side)
                raw = classify_gesture(fingers)
                gesture = stable_gesture(raw)

        if gesture:
            if gesture == current_gesture:
                if now > cooldown_until:
                    elapsed = now - gesture_start
                    if elapsed >= HOLD_TIME:
                        action = GESTURE_ACTIONS.get(gesture)
                        if action:
                            action()
                            print(f"[Presentation Mode] Triggered: {gesture}")

                        cooldown_until = now + COOLDOWN_TIME
                        current_gesture = ""
                        gesture_buffer.clear()
            else:
                current_gesture = gesture
                gesture_start = now
        else:
            current_gesture = ""

        cv2.putText(img, "Presentation Control Mode",
                    (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (0, 255, 140), 2)

        cv2.imshow("Presentation Control", img)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[Presentation Mode] Stopped.")