import cv2
import numpy as np
import mediapipe as mp
from pynput.keyboard import Controller
import time

# Initialize keyboard controller
keyboard = Controller()

# Initialize MediaPipe hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Keyboard layout
keys = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
    ["SHIFT", "SPACE", "BACK", "ENTER"]
]


# ---------------- BUTTON CLASS ----------------
class Button:
    def __init__(self, pos, text, size=(85, 85)):
        self.pos = pos
        self.size = size
        self.text = text

    def draw(self, img, color=(50, 50, 50)):
        x, y = self.pos
        w, h = self.size
        cv2.rectangle(img, (x, y), (x + w, y + h), color, cv2.FILLED)
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 2)

        font_scale = 1.5 if len(self.text) == 1 else 0.8
        text_size = cv2.getTextSize(
            self.text, cv2.FONT_HERSHEY_PLAIN, font_scale, 2
        )[0]

        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2

        cv2.putText(img, self.text, (text_x, text_y),
                    cv2.FONT_HERSHEY_PLAIN, font_scale,
                    (255, 255, 255), 2)

    def is_over(self, point):
        x, y = self.pos
        w, h = self.size
        px, py = point
        return x < px < x + w and y < py < y + h


# ---------------- MAIN FUNCTION ----------------
def run_keyboard():

    # Create buttons inside function (important for threading safety)
    button_list = []
    start_x, start_y = 50, 200

    for i, row in enumerate(keys):
        x_offset = 0
        for j, key in enumerate(row):
            if key == "SPACE":
                button_list.append(
                    Button((start_x + 100, start_y + i * 100),
                           key, (600, 85))
                )
            else:
                button_list.append(
                    Button((start_x + j * 90 + x_offset,
                            start_y + i * 100),
                           key)
                )

    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    final_text = ""
    last_click_time = 0
    click_cooldown = 0.3

    print("Virtual Keyboard Started! Press 'q' to quit.")

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        # Draw buttons
        for button in button_list:
            button.draw(img)

        # Display typed text
        cv2.rectangle(img, (50, 50), (1230, 120),
                      (50, 50, 50), cv2.FILLED)

        cv2.putText(img, final_text, (60, 95),
                    cv2.FONT_HERSHEY_PLAIN,
                    3, (255, 255, 255), 3)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:

                mp_drawing.draw_landmarks(
                    img,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

                landmarks = hand_landmarks.landmark
                h, w, _ = img.shape

                # Index finger
                index = landmarks[8]
                index_x, index_y = int(index.x * w), int(index.y * h)

                # Thumb
                thumb = landmarks[4]
                thumb_x, thumb_y = int(thumb.x * w), int(thumb.y * h)

                cv2.circle(img, (index_x, index_y),
                           15, (0, 255, 0), cv2.FILLED)

                distance = np.sqrt(
                    (index_x - thumb_x) ** 2 +
                    (index_y - thumb_y) ** 2
                )

                current_time = time.time()

                for button in button_list:
                    if button.is_over((index_x, index_y)):

                        button.draw(img, color=(0, 150, 0))

                        if (distance < 40 and
                                (current_time - last_click_time) > click_cooldown):

                            button.draw(img, color=(0, 255, 0))

                            if button.text == "SPACE":
                                final_text += " "
                                keyboard.press(' ')
                            else:
                                final_text += button.text
                                keyboard.press(button.text.lower())

                            last_click_time = current_time
                            print(f"Typed: {button.text}")

        cv2.putText(img,
                    "Pinch to Click | Press 'q' to quit",
                    (50, 680),
                    cv2.FONT_HERSHEY_PLAIN,
                    2, (255, 255, 255), 2)

        cv2.imshow("Virtual Keyboard", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Keyboard mode stopped.")
