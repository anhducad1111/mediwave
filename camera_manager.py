from picamera2 import Picamera2, libcamera

class CameraManager:
    def __init__(self, width=640, height=480):
        """Initialize the camera with specified resolution."""
        self.picam2 = Picamera2()
        self.setup_camera(width, height)

    def setup_camera(self, width, height):
        """Configure camera settings."""
        self.picam2.preview_configuration.main.size = (width, height)
        self.picam2.preview_configuration.main.format = "RGB888"
        self.picam2.preview_configuration.transform = libcamera.Transform(vflip=1)
        self.picam2.set_controls({
            "FrameDurationLimits": (33333, 33333),  # Force 30fps
            "NoiseReductionMode": 0  # Minimal noise reduction
        })
        self.picam2.configure("preview")

    def start(self):
        """Start the camera."""
        self.picam2.start()

    def capture_frame(self):
        """Capture a single frame from the camera."""
        return self.picam2.capture_array()

    def stop(self):
        """Stop the camera."""
        self.picam2.stop()
