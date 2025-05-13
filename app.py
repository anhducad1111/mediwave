import cv2
import numpy as np
import time
import threading
import queue
from hand_detector import HandDetector
from camera_manager import CameraManager
from display_manager import DisplayManager
from mouse_controller import MouseController

# Thread-safe queues for frame passing
frame_queue = queue.Queue(maxsize=4)  # Raw frames from camera
processed_queue = queue.Queue(maxsize=4)  # Processed frames with results

class HandTrackingApp:
    def __init__(self):
        """Initialize the hand tracking application."""
        self.camera = CameraManager()
        # Initialize with lower confidence thresholds for speed
        self.detector = HandDetector(max_num_hands=2, 
                                   min_detection_confidence=0.5, 
                                   min_tracking_confidence=0.5)
        self.display = DisplayManager()
        self.mouse = MouseController(smoothing_factor=0.7)  # Increase smoothing
        self.frame_count = 0  # Shared counter between threads
        self.display_interval = 3  # Reduced visual updates
        self.process_interval = 2  # Process every other frame
        self.running = False
        
    def handle_key_press(self):
        """Handle keyboard input."""
        key = cv2.waitKey(1) & 0xFF  # Reduced from 10ms to 1ms
        if key == ord('q'):
            return False
        elif key == ord('m'):
            # Toggle between mouse control and distance measurement
            if self.display.measure_mode == "mouse":
                self.display.measure_mode = "distance"
                self.detector = HandDetector(max_num_hands=2)
            else:
                self.display.measure_mode = "mouse"
                self.detector = HandDetector(max_num_hands=1)
        return True

    def camera_thread(self):
        """Thread for capturing frames from camera."""
        while self.running:
            frame = self.camera.capture_frame()
            if frame is not None:
                if frame_queue.full():
                    frame_queue.get()  # Remove old frame
                frame_queue.put((frame.copy(), time.time()))

    def process_thread(self):
        """Thread for processing frames with MediaPipe."""
        while self.running:
            try:
                frame, timestamp = frame_queue.get(timeout=1.0)
                if frame is not None:
                    last_results = None
                    results = None
                    # Only process every other frame
                    if self.frame_count % self.process_interval == 0:
                        # Further reduce resolution for processing
                        process_frame = cv2.resize(frame, (160, 120))
                        
                        # Detect hands
                        results = self.detector.find_hands(process_frame)
                        if results and results.multi_hand_landmarks:
                            last_results = results
                            if self.frame_count % self.display_interval == 0:
                                for hand_landmarks in results.multi_hand_landmarks:
                                    self.detector.draw_landmarks(frame, hand_landmarks)
                    else:
                        # Use previous results when skipping processing
                        try:
                            prev_frame, prev_results, _ = processed_queue.get_nowait()
                            if prev_results and prev_results.multi_hand_landmarks:
                                last_results = prev_results
                        except queue.Empty:
                            pass
                    
                    results = last_results if last_results else results
                    
                    if processed_queue.full():
                        processed_queue.get()  # Remove old result
                    processed_queue.put((frame, results, timestamp))
            except queue.Empty:
                continue

    def run(self):
        """Run the main application loop."""
        self.camera.start()
        self.running = True

        # Start worker threads
        camera_thread = threading.Thread(target=self.camera_thread)
        process_thread = threading.Thread(target=self.process_thread)
        camera_thread.start()
        process_thread.start()
        
        try:
            while True:
                try:
                    # Get processed results
                    frame, results, timestamp = processed_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                # Handle mouse control if in mouse mode
                if self.display.measure_mode == "mouse":
                    right_hand = self.detector.find_right_hand(results)
                    if right_hand:
                        finger_pos = self.detector.get_index_finger_pos(right_hand)
                        if finger_pos:
                            x, y = finger_pos
                            
                            # Move mouse cursor
                            screen_x, screen_y = self.mouse.map_coordinates(x, y, 
                                                                        frame.shape[1], 
                                                                        frame.shape[0])
                            smooth_x, smooth_y = self.mouse.smooth_position(screen_x, screen_y)
                            self.mouse.move_mouse(smooth_x, smooth_y)
                            
                            # Check for pinch gesture (click/drag)
                            is_pinched = self.detector.check_pinch(right_hand)
                            self.mouse.handle_pinch(is_pinched)
                            
                            # Check for zoom gestures
                            is_zoom_in = self.detector.check_zoom_in(right_hand)
                            is_zoom_out = self.detector.check_zoom_out(right_hand)
                            self.mouse.handle_zoom(is_zoom_in, is_zoom_out)
                            
                            if self.frame_count % self.display_interval == 0:
                                self.detector.draw_mouse_pointer(frame, x, y)
                    else:
                        self.mouse.disable_control()

                # Update display
                if self.frame_count % self.display_interval == 0:
                    self.display.draw_mode(frame)
                    fps = self.display.update_fps()
                    self.display.draw_fps(frame, fps)
                    self.display.show_frame(frame)
                
                # Increment shared frame counter and handle keyboard input
                self.frame_count += 1
                if not self.handle_key_press():
                    break

        finally:
            # Stop threads and cleanup
            self.running = False
            camera_thread.join()
            process_thread.join()
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        self.detector.close()
        self.camera.stop()
        self.display.cleanup()
