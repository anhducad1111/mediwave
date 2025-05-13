import cv2

class CameraManager:
    def __init__(self, width=640, height=480):
        """Initialize the camera with specified resolution."""
        self.cap = cv2.VideoCapture("/dev/video0", cv2.CAP_V4L2)
        self.setup_camera(width, height)

    def setup_camera(self, width, height):
        """Configure camera settings."""
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FPS, 24)  # Request 60fps
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer size
        
        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera")

    def start(self):
        """Start the camera."""
        # OpenCV camera is already started in __init__
        pass

    def capture_frame(self):
        """Capture a single frame from the camera."""
        ret, frame = self.cap.read()
        if not ret:
            return None
        return cv2.flip(frame, 0)  # Flip frame vertically as in camera_stream.py

    def stop(self):
        """Stop the camera."""
        self.cap.release()
        cv2.destroyAllWindows()
