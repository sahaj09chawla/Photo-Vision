import cv2
import numpy as np 

class QRDetector:
    def __init__(self):
        self.detector = cv2.QRCodeDetector()
        try:
            cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)
        except AttributeError:
            pass

    # return none if no QR code found, otherwise a dictionary with the QR code data:
    # decoded: string inside the QR Code
    # points: 4 points of the QR Code in the order of top-left, top-right, bottom-right, bottom-left
    # _: unused status return value
    def normalize_corners(self, points):
        pts = np.array(points, dtype=np.float32)

        if pts.ndim == 3:
            pts = pts[0]

        if pts.ndim != 2 or pts.shape != (4, 2):
            return None

        return pts.astype(int)

    def detect(self, frame):
        try:
            ok, points = self.detector.detect(frame)
        except cv2.error:
            return None

        if not ok or points is None:
            return None

        corners = self.normalize_corners(points)
        if corners is None:
            return None

        top = np.linalg.norm(corners[1] - corners[0])
        bottom = np.linalg.norm(corners[2] - corners[3])
        pixel_width = (top + bottom) / 2.0

        if pixel_width <= 0:
            return None

        area = cv2.contourArea(corners.reshape(-1, 1, 2).astype(np.float32))
        if area <= 0:
            return None

        decode = ""
        try:
            decode, _ = self.detector.decode(frame, np.array([corners], dtype=np.float32))
            decode = decode or ""
        except cv2.error:
            pass

        return {
            "decoded": decode,
            "points": corners,
            "pixel_width": pixel_width,
        }

    def draw(self, frame, detection):
        # draw the QR code points on the frame

        corners = detection["points"]
        for i in range(4):
            pt1 = tuple(corners[i].tolist())
            pt2 = tuple(corners[(i + 1) % 4].tolist())
            cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

        x, y = corners[0].tolist()
        label = detection["decoded"] or "QR detected"
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
