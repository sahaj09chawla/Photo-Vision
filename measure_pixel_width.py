import cv2

from camera import Camera
from qr_detection import QRDetector
from config import QR_CODE_WIDTH_CM

# Optional: set this if you also want focal length printed (same as calibration distance)
KNOWN_DISTANCE_CM = 23.5

camera = Camera()
qr_detector = QRDetector()

print("Point the camera at your printed QR code.")
print("Press C to capture the pixel width, Q to quit.")

while True:
    frame = camera.get_frame()
    display = frame.copy()
    det = qr_detector.detect(frame)

    if det:
        qr_detector.draw(display, det)
        cv2.putText(
            display,
            f"Pixel width: {det['pixel_width']:.1f} px",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            display,
            "Press C to capture | Q to quit",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )
    else:
        cv2.putText(
            display,
            "No QR code detected",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
        )

    cv2.imshow("Measure Pixel Width", display)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("c") and det:
        pixel_width = det["pixel_width"]
        focal = (pixel_width * KNOWN_DISTANCE_CM) / QR_CODE_WIDTH_CM

        print("\n--- Measurement ---")
        print(f"Pixel width: {pixel_width:.1f} pixels")
        print(f"\nFocal length formula:")
        print(f"  f = (pixel_width x known_distance) / real_QR_width")
        print(f"  f = ({pixel_width:.1f} x {KNOWN_DISTANCE_CM}) / {QR_CODE_WIDTH_CM}")
        print(f"  f = {focal:.1f}")
        print(f"\nPut this in config.py:")
        print(f"  FOCAL_LENGTH_CM = {focal:.1f}\n")
        break

    if key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
