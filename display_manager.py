import cv2
import time

class DisplayManager:
    def __init__(self, fps_buffer_size=10):
        """Initialize display manager with FPS calculation settings."""
        self.prev_time = time.time()
        self.fps_values = []
        self.fps_buffer_size = fps_buffer_size
        self.measure_mode = "mouse"  # none, thumbs, thumb_index, mouse

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
        cv2.putText(frame, f'FPS: {fps}', (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    def draw_hand_count(self, frame, hand_landmarks, hand_type, fingers):
        """Draw hand count at hand position."""
        x = int(hand_landmarks.landmark[0].x * frame.shape[1])
        y = int(hand_landmarks.landmark[0].y * frame.shape[0])
        cv2.putText(frame, f'{hand_type}: {fingers}', (x - 30, y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    def draw_total_count(self, frame, total_count):
        """Draw total finger count."""
        cv2.putText(frame, f'Total: {total_count}', (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    def show_frame(self, frame, window_name="Hand Tracking"):
        """Display the frame."""
        cv2.imshow(window_name, frame)

    def should_quit(self):
        """Check if user pressed 'q' to quit."""
        return cv2.waitKey(1) & 0xFF == ord('q')

    def draw_distance(self, frame, distance, points=None):
        """Draw distance measurement on frame."""
        # Draw the distance value
        text = f'Distance: {distance:.2f}'
        cv2.putText(frame, text, (10, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # If points are provided, draw a line between them
        if points and len(points) == 2:
            p1 = (int(points[0][0] * frame.shape[1]), int(points[0][1] * frame.shape[0]))
            p2 = (int(points[1][0] * frame.shape[1]), int(points[1][1] * frame.shape[0]))
            cv2.line(frame, p1, p2, (0, 0, 255), 2)

    def draw_mode(self, frame):
        """Draw current measurement mode."""
        mode_text = {
            "mouse": "Mode: Mouse Control",
            "none": "Mode: Finger Count",
            "thumbs": "Mode: Thumb Distance",
            "thumb_index": "Mode: Thumb-Index Distance"
        }
        cv2.putText(frame, mode_text[self.measure_mode], (10, 150),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    def cleanup(self):
        """Clean up display resources."""
        cv2.destroyAllWindows()
