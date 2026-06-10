class DistanceCalculator:
    def __init__(self, focal_lengths_pixels: float):
        self.focal_length = focal_lengths_pixels

    def calculate_distance(self, real_width: float, pixel_width: float) -> float:
        if pixel_width <= 0:
            raise ValueError("Pixel width must be positive")

        return (real_width * self.focal_length) / pixel_width