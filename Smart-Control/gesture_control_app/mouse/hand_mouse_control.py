"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                        HAND MOUSE CONTROL v2.0                            ║
║                    Control your mouse with hand gestures                  ║
╚═══════════════════════════════════════════════════════════════════════════╝

INSTALLATION INSTRUCTIONS:
--------------------------
1. Install required packages:
   pip install opencv-python mediapipe pyautogui numpy

2. Make sure you have a working webcam connected

USAGE INSTRUCTIONS:
-------------------
1. Run the script:
   python hand_mouse_control.py

2. Position your hand in front of the webcam
3. Keep your hand clearly visible and well-lit

GESTURE CONTROLS:
-----------------
✋ INDEX FINGER UP        → Move cursor (track index fingertip)
👌 THUMB + INDEX PINCH    → Left click (quick) / Drag (hold)
👌 THUMB + MIDDLE PINCH   → Right click
🤏 INDEX + RING PINCH     → Double click

TIPS FOR BEST PERFORMANCE:
---------------------------
• Keep hand 1-2 feet from camera
• Ensure good lighting (avoid backlighting)
• Use against a plain background
• Keep hand gestures clear and distinct
• Adjust SENSITIVITY if cursor moves too fast/slow

TROUBLESHOOTING:
----------------
• Low FPS: Reduce camera resolution or close other applications
• Cursor jittery: Increase SMOOTHING_BUFFER
• Gestures not detected: Adjust lighting or hand position
• Clicks too sensitive: Increase PINCH_THRESHOLD

Press ESC to exit the application
"""

import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import math
from collections import deque

# ============================================================================
#                           CONFIGURATION SETTINGS
# ============================================================================

# Camera Settings
CAM_WIDTH = 640          # Lower for better FPS (try 320), higher for accuracy
CAM_HEIGHT = 480         # Lower for better FPS (try 240), higher for accuracy

# Performance Settings
SMOOTHING_BUFFER = 3     # Cursor smoothing (higher = smoother but laggier)
SKIP_FRAMES = 0          # Skip every N frames (0 = no skip, 1 = skip half)

# Gesture Detection
PINCH_THRESHOLD = 0.03   # Pinch sensitivity (lower = more sensitive)
CLICK_DEBOUNCE = 0.25    # Minimum time between clicks (seconds)
DRAG_HOLD_TIME = 0.15    # Hold time before drag starts (seconds)

# Cursor Control
SENSITIVITY = 1.8        # Cursor movement sensitivity (higher = faster)
EDGE_MARGIN = 0.1        # Dead zone at screen edges (0.0 - 0.5)

# Safety
pyautogui.FAILSAFE = False  # Move mouse to corner to stop if True

# ============================================================================
#                              INITIALIZATION
# ============================================================================

screen_w, screen_h = pyautogui.size()
print(f"Screen resolution: {screen_w}x{screen_h}")

# MediaPipe setup with optimized settings
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=1,              # Track only 1 hand for better performance
    min_detection_confidence=0.7,  # Higher = more accurate, fewer false positives
    min_tracking_confidence=0.5,   # Lower = better tracking in motion
    model_complexity=0             # 0 = fastest, 1 = balanced (use 0 for speed)
)

# Finger landmark indices
TIP_IDS = {
    "thumb": 4,
    "index": 8,
    "middle": 12,
    "ring": 16,
    "pinky": 20
}

PIP_IDS = {
    "index": 6,
    "middle": 10,
    "ring": 14
}

# ============================================================================
#                            STATE VARIABLES
# ============================================================================

last_left_click = 0
last_right_click = 0
last_double_click = 0
drag_state = False
drag_start_time = None
pos_buffer = deque(maxlen=SMOOTHING_BUFFER)
prev_time = time.time()
frame_count = 0

# ============================================================================
#                            HELPER FUNCTIONS
# ============================================================================

def normalize_distance(point_a, point_b):
    """Calculate Euclidean distance between two points."""
    return math.hypot(point_a[0] - point_b[0], point_a[1] - point_b[1])


def get_landmark_coords(landmarks, landmark_id):
    """Extract x, y coordinates from a landmark."""
    return landmarks[landmark_id].x, landmarks[landmark_id].y


def is_finger_up(landmarks, finger_name):
    """Check if a finger is extended (pointing up)."""
    if finger_name == "thumb":
        # Thumb: compare x-coordinates (left/right)
        return landmarks[TIP_IDS["thumb"]].x < landmarks[TIP_IDS["thumb"] - 2].x
    else:
        # Other fingers: compare y-coordinates (tip vs PIP joint)
        tip_y = landmarks[TIP_IDS[finger_name]].y
        pip_y = landmarks[PIP_IDS[finger_name]].y
        return tip_y < pip_y


def map_to_screen(x, y, sensitivity=SENSITIVITY, margin=EDGE_MARGIN):
    """
    Map hand coordinates to screen coordinates with sensitivity and margins.
    
    Args:
        x, y: Normalized coordinates (0-1)
        sensitivity: Movement amplification
        margin: Dead zone at edges
    """
    # Apply margin (dead zone)
    x = np.clip((x - margin) / (1 - 2 * margin), 0, 1)
    y = np.clip((y - margin) / (1 - 2 * margin), 0, 1)
    
    # Apply sensitivity from center
    dx = (x - 0.5) * sensitivity + 0.5
    dy = (y - 0.5) * sensitivity + 0.5
    
    # Clip to valid range
    dx = np.clip(dx, 0, 1)
    dy = np.clip(dy, 0, 1)
    
    # Map to screen
    screen_x = np.interp(dx, [0, 1], [0, screen_w])
    screen_y = np.interp(dy, [0, 1], [0, screen_h])
    
    return screen_x, screen_y


def smooth_position(new_pos, buffer):
    """Apply moving average smoothing to cursor position."""
    buffer.append(new_pos)
    avg_x = sum(p[0] for p in buffer) / len(buffer)
    avg_y = sum(p[1] for p in buffer) / len(buffer)
    return avg_x, avg_y


def draw_gesture_text(frame, text, y_offset, color):
    """Draw gesture feedback text on frame."""
    cv2.putText(frame, text, (10, 60 + y_offset), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)


# ============================================================================
#                              MAIN LOOP
# ============================================================================

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, 60)  # Request higher FPS if camera supports it

# Reduce buffer size for lower latency
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

print("\n" + "="*70)
print("🖐️  HAND MOUSE CONTROL STARTED")
print("="*70)
print("📹 Camera initialized")
print("✋ Show your hand to start controlling the mouse")
print("❌ Press ESC to exit\n")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️  Failed to capture frame. Check your webcam.")
            break
        
        frame_count += 1
        
        # Skip frames for better performance if configured
        if SKIP_FRAMES > 0 and frame_count % (SKIP_FRAMES + 1) != 0:
            continue
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert to RGB (MediaPipe uses RGB)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False  # Performance optimization
        
        # Process hand detection
        results = hands.process(rgb)
        
        rgb.flags.writeable = True
        now = time.time()
        
        # Process detected hands
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            landmarks = hand_landmarks.landmark
            
            # Draw hand landmarks (optional - disable for better FPS)
            mp_drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1)
            )
            
            # Get fingertip coordinates
            thumb = get_landmark_coords(landmarks, TIP_IDS["thumb"])
            index = get_landmark_coords(landmarks, TIP_IDS["index"])
            middle = get_landmark_coords(landmarks, TIP_IDS["middle"])
            ring = get_landmark_coords(landmarks, TIP_IDS["ring"])
            
            # Calculate distances between fingers
            d_thumb_index = normalize_distance(thumb, index)
            d_thumb_middle = normalize_distance(thumb, middle)
            d_index_ring = normalize_distance(index, ring)
            
            # ================================================================
            #                       CURSOR MOVEMENT
            # ================================================================
            
            if is_finger_up(landmarks, "index"):
                ix, iy = index
                screen_x, screen_y = map_to_screen(ix, iy)
                avg_x, avg_y = smooth_position((screen_x, screen_y), pos_buffer)
                pyautogui.moveTo(avg_x, avg_y, _pause=False)
                
                # Visual feedback
                cv2.circle(frame, 
                          (int(ix * frame.shape[1]), int(iy * frame.shape[0])), 
                          10, (0, 255, 255), -1)
            
            # ================================================================
            #                    LEFT CLICK & DRAG
            # ================================================================
            
            if d_thumb_index < PINCH_THRESHOLD:
                # Pinch detected
                if drag_start_time is None:
                    drag_start_time = now
                
                # Start drag if held long enough
                if now - drag_start_time > DRAG_HOLD_TIME and not drag_state:
                    pyautogui.mouseDown(button='left')
                    drag_state = True
                    draw_gesture_text(frame, "🖱️ DRAGGING", 0, (0, 165, 255))
            else:
                # Pinch released
                if drag_start_time is not None:
                    if drag_state:
                        # End drag
                        pyautogui.mouseUp(button='left')
                        drag_state = False
                        draw_gesture_text(frame, "✓ DRAG END", 0, (0, 255, 0))
                    else:
                        # Quick pinch = left click
                        if now - last_left_click > CLICK_DEBOUNCE:
                            pyautogui.click(button='left')
                            last_left_click = now
                            draw_gesture_text(frame, "👆 LEFT CLICK", 0, (0, 255, 0))
                    
                    drag_start_time = None
            
            # ================================================================
            #                        RIGHT CLICK
            # ================================================================
            
            if d_thumb_middle < PINCH_THRESHOLD:
                if now - last_right_click > CLICK_DEBOUNCE:
                    pyautogui.click(button='right')
                    last_right_click = now
                    draw_gesture_text(frame, "👆 RIGHT CLICK", 30, (255, 0, 0))
            
            # ================================================================
            #                       DOUBLE CLICK
            # ================================================================
            
            if d_index_ring < PINCH_THRESHOLD:
                if now - last_double_click > 0.5:
                    pyautogui.doubleClick()
                    last_double_click = now
                    draw_gesture_text(frame, "👆👆 DOUBLE CLICK", 60, (255, 0, 255))
        
        else:
            # No hand detected - reset drag state
            if drag_state:
                pyautogui.mouseUp(button='left')
                drag_state = False
            drag_start_time = None
            pos_buffer.clear()
            
            # Show instruction
            cv2.putText(frame, "Show your hand", 
                       (frame.shape[1]//2 - 100, frame.shape[0]//2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # ====================================================================
        #                          FPS DISPLAY
        # ====================================================================
        
        cur_time = time.time()
        fps = 1 / (cur_time - prev_time) if cur_time != prev_time else 0
        prev_time = cur_time
        
        # FPS with color coding
        fps_color = (0, 255, 0) if fps > 25 else (0, 165, 255) if fps > 15 else (0, 0, 255)
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, fps_color, 2)
        
        # Instructions overlay
        cv2.putText(frame, "ESC = Exit", (frame.shape[1] - 150, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Display frame
        cv2.imshow("Hand Mouse Control v2.0", frame)
        
        # Check for ESC key
        if cv2.waitKey(1) & 0xFF == 27:
            print("\n👋 Exiting Hand Mouse Control...")
            break

except KeyboardInterrupt:
    print("\n⚠️  Interrupted by user")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Cleanup
    if drag_state:
        pyautogui.mouseUp(button='left')
    
    cap.release()
    cv2.destroyAllWindows()
    hands.close()
    
    print("✓ Cleanup complete")
    print("="*70)
