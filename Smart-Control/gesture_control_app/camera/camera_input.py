import cv2

class CameraInput:
    def __init__(self, cam_index=0):
        self.cap = cv2.VideoCapture(cam_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


    def get_frame(self):
        success, frame = self.cap.read()
        if not success:
            return None
        return cv2.flip(frame, 1)

    def release(self):
        self.cap.release()
