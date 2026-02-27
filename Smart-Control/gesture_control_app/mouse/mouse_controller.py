import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import math
from collections import deque

# ---------------- CONFIG ----------------
CAM_WIDTH = 640
CAM_HEIGHT = 480

SMOOTHING_BUFFER = 3
PINCH_THRESHOLD = 0.03
CLICK_DEBOUNCE = 0.25
DRAG_HOLD_TIME = 0.15
SENSITIVITY = 1.8

pyautogui.FAILSAFE = False
# ----------------------------------------

screen_w, screen_h = pyautogui.size()

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

TIP_IDS = {"thumb": 4, "index": 8, "middle": 12, "ring": 16}

# ---------------- HELPER FUNCTIONS ----------------

def norm_distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def get_tip_coords(landmarks, tip_id):
    return landmarks[tip_id].x, landmarks[tip_id].y

# ---------------- MAIN FUNCTION ----------------

def run_mouse():

    last_left_click = 0
    last_right_click = 0
    last_double_click = 0

    drag_state = False
    drag_start_time = None
    pos_buffer = deque(maxlen=SMOOTHING_BUFFER)

    prev_time = time.time()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)

    print("Hand mouse started. Press ESC to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        now = time.time()

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            landmarks = hand_landmarks.landmark
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            thumb = get_tip_coords(landmarks, TIP_IDS["thumb"])
            index = get_tip_coords(landmarks, TIP_IDS["index"])
            middle = get_tip_coords(landmarks, TIP_IDS["middle"])
            ring = get_tip_coords(landmarks, TIP_IDS["ring"])

            d_thumb_index = norm_distance(thumb, index)
            d_thumb_middle = norm_distance(thumb, middle)
            d_index_ring = norm_distance(index, ring)

            index_tip_y = landmarks[TIP_IDS["index"]].y
            index_pip_y = landmarks[6].y

            # ---------------- CURSOR MOVE ----------------
            if index_tip_y < index_pip_y:

                ix, iy = index

                dx = (ix - 0.5) * SENSITIVITY + 0.5
                dy = (iy - 0.5) * SENSITIVITY + 0.5

                dx = np.clip(dx, 0, 1)
                dy = np.clip(dy, 0, 1)

                screen_x = np.interp(dx, [0, 1], [0, screen_w])
                screen_y = np.interp(dy, [0, 1], [0, screen_h])

                pos_buffer.append((screen_x, screen_y))

                avg_x = sum([p[0] for p in pos_buffer]) / len(pos_buffer)
                avg_y = sum([p[1] for p in pos_buffer]) / len(pos_buffer)

                pyautogui.moveTo(avg_x, avg_y, _pause=False)

            # ---------------- LEFT CLICK / DRAG ----------------
            if d_thumb_index < PINCH_THRESHOLD:
                if drag_start_time is None:
                    drag_start_time = now

                if now - drag_start_time > DRAG_HOLD_TIME and not drag_state:
                    pyautogui.mouseDown(button='left')
                    drag_state = True
            else:
                if drag_start_time is not None:
                    if drag_state:
                        pyautogui.mouseUp(button='left')
                        drag_state = False
                    else:
                        if now - last_left_click > CLICK_DEBOUNCE:
                            pyautogui.click(button='left')
                            last_left_click = now
                    drag_start_time = None

            # ---------------- RIGHT CLICK ----------------
            if d_thumb_middle < PINCH_THRESHOLD and now - last_right_click > CLICK_DEBOUNCE:
                pyautogui.click(button='right')
                last_right_click = now

            # ---------------- DOUBLE CLICK ----------------
            if d_index_ring < PINCH_THRESHOLD and now - last_double_click > 0.5:
                pyautogui.doubleClick()
                last_double_click = now

        # ---------------- FPS DISPLAY ----------------
        cur_time = time.time()
        fps = 1 / (cur_time - prev_time) if cur_time != prev_time else 0
        prev_time = cur_time

        cv2.putText(frame, f"FPS: {int(fps)}",
                    (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 255),
                    2)

        cv2.imshow("Hand Mouse (ESC to exit)", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Mouse mode stopped.")
