import cv2

from camera import Camera
from qr_detection import QRDetector
from distance_calculator import DistanceCalculator
from config import (QR_CODE_WIDTH_CM, FOCAL_LENGTH_CM)

class DistanceEstimatorApplication:
    def __init__(self):
        self.camera = Camera()
        self.qr_detector= QRDetector()
        self.distance_calculator = DistanceCalculator(FOCAL_LENGTH_CM)

    def run(self):
        while True:
            frame = self.camera.get_frame()
            display = frame.copy()

            detection = self.qr_detector.detect(frame)

            if detection:
                distance = self.distance_calculator.calculate_distance(QR_CODE_WIDTH_CM, detection["pixel_width"])

                self.qr_detector.draw(display, detection)
                cv2.putText(display, f"Distance: {distance:.2f} cm", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                print(f"Distance: {distance:.2f} cm | QR: {detection['decoded']}")

            else:
                cv2.putText(display, "No QR Code detected", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            cv2.imshow("Distance Estimator", display)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    DistanceEstimatorApplication().run()
