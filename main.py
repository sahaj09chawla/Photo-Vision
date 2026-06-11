import cv2
import time

try:
    import serial
except ImportError:
    serial = None

from camera import Camera
from qr_detection import QRDetector
from distance_calculator import DistanceCalculator
from config import (QR_CODE_WIDTH_CM, FOCAL_LENGTH_CM, SERIAL_PORT, SERIAL_BAUD)

class DistanceEstimatorApplication:
    def __init__(self):
        self.camera = Camera()
        self.qr_detector = QRDetector()
        self.distance_calculator = DistanceCalculator(FOCAL_LENGTH_CM)
        self.last_raw_cm = None
        self.stable_count = 0
        self.last_sent_cm = None
        self.serial = None

        if serial is not None:
            try:
                self.serial = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
                time.sleep(2)
            except Exception as exc:
                print(f"Serial disabled: {exc}")

    def run(self):
        while True:
            frame = self.camera.get_frame()
            display = frame.copy()

            detection = self.qr_detector.detect(frame)

            if detection:
                distance_cm = self.distance_calculator.calculate_distance(QR_CODE_WIDTH_CM, detection["pixel_width"])
                rounded_cm = int(round(distance_cm))

                if self.last_raw_cm == rounded_cm:
                    self.stable_count += 1
                else:
                    self.last_raw_cm = rounded_cm
                    self.stable_count = 1

                if (
                    self.serial is not None
                    and self.stable_count >= 3
                    and rounded_cm != self.last_sent_cm
                ):
                    self.serial.write(f"{rounded_cm}\n".encode("ascii"))
                    self.last_sent_cm = rounded_cm

                distance_m = rounded_cm / 100.0

                self.qr_detector.draw(display, detection)
                cv2.putText(
                    display,
                    f"Distance: {rounded_cm} cm ({distance_m:.2f} m)",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                )

                print(f"Distance: {rounded_cm} cm | QR: {detection['decoded']}")

            else:
                self.last_raw_cm = None
                self.stable_count = 0
                cv2.putText(display, "No QR Code detected", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            cv2.imshow("Distance Estimator", display)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.camera.release()
        if self.serial is not None:
            self.serial.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    DistanceEstimatorApplication().run()
