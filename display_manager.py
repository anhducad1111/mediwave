import cv2
import time

class DisplayManager:
    def __init__(self, fps_buffer_size=10):
        """Initialize display manager with FPS calculation settings."""
        self.prev_time = time.time()
        self.fps_values = []
        self.fps_buffer_size = fps_buffer_size
        self.measure_mode = "mouse"  # mouse or distance
        
        # Pre-initialize font settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.7
        self.text_thickness = 2
        self.line_thickness = 2
        
        # Create window with optimized properties
        cv2.namedWindow("Hand Tracking", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Hand Tracking", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        
        # Cache text positions
        self.fps_pos = (10, 30)
        self.distance_pos = (10, 70)
        self.mode_pos = (10, 110)

    def update_fps(self):
        """Calculate and update FPS."""
        current_time = time.time()
        fps = 1 / (current_time - self.prev_time)
        self.prev_time = current_time
        
        self.fps_values.append(fps)
        if len(self.fps_values) > self.fps_buffer_size:
            self.fps_values.pop(0)
        
        return int(sum(self.fps_values) / len(self.fps_values))

    def draw_fps(self, frame, fps):
        """Draw FPS counter on frame."""
        cv2.putText(frame, f'FPS: {fps}', self.fps_pos,
                   self.font, self.font_scale, (0, 255, 0), self.text_thickness)

    def draw_distance(self, frame, distance, points=None):
        """Draw distance measurement on frame."""
        cv2.putText(frame, f'Distance: {distance:.2f}', self.distance_pos,
                   self.font, self.font_scale, (0, 0, 255), self.text_thickness)
        
        # Draw line between thumb positions
        if points and len(points) == 2:
            p1 = (int(points[0][0] * frame.shape[1]), int(points[0][1] * frame.shape[0]))
            p2 = (int(points[1][0] * frame.shape[1]), int(points[1][1] * frame.shape[0]))
            cv2.line(frame, p1, p2, (0, 0, 255), self.line_thickness)

    def draw_mode(self, frame):
        """Draw current mode on frame."""
        mode_text = "Mouse Control" if self.measure_mode == "mouse" else "Distance Measurement"
        cv2.putText(frame, f'Mode: {mode_text}', self.mode_pos,
                   self.font, self.font_scale, (255, 0, 0), self.text_thickness)

    def show_frame(self, frame, window_name="Hand Tracking"):
        """Display the frame."""
        cv2.imshow(window_name, frame)

    def cleanup(self):
        """Clean up display resources."""
        cv2.destroyAllWindows()
