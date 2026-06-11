import sys
import time

import cv2


class Camera:
    def __init__(self, camera_index=0, warmup_frames=15):
        if sys.platform == "win32":
            self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            raise RuntimeError(
                "Could not open camera. Close other apps using the webcam and try again."
            )

        for _ in range(warmup_frames):
            self.cap.read()
            time.sleep(0.03)

    def get_frame(self):
        for _ in range(10):
            success, frame = self.cap.read()
            if success and frame is not None:
                return frame
            time.sleep(0.05)

        raise RuntimeError(
            "Could not read frame. Close main.py or any other app using the camera, then try again."
        )

    def release(self):
        self.cap.release()
