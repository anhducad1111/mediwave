import cv2
from hand_detector import HandDetector
from camera_manager import CameraManager
from display_manager import DisplayManager
from mouse_controller import MouseController

class HandTrackingApp:
    def __init__(self):
        """Initialize the hand tracking application."""
        self.camera = CameraManager()
        self.detector = HandDetector()
        self.display = DisplayManager()
        self.mouse = MouseController(smoothing_factor=0.5)
        
    def handle_key_press(self):
        """Handle keyboard input for mode switching."""
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            return False
        elif key == ord('m'):
            # Cycle through measurement modes
            if self.display.measure_mode == "mouse":
                self.display.measure_mode = "thumbs"
            elif self.display.measure_mode == "thumbs":
                self.display.measure_mode = "thumb_index"
            elif self.display.measure_mode == "thumb_index":
                self.display.measure_mode = "none"
            else:
                self.display.measure_mode = "mouse"
        return True

    def run(self):
        """Run the main application loop."""
        self.camera.start()
        
        try:
            while True:
                # Capture frame
                frame = self.camera.capture_frame()
                
                # Detect hands
                results = self.detector.find_hands(frame)
                
                # Update FPS
                fps = self.display.update_fps()
                self.display.draw_fps(frame, fps)
                
                right_count = 0
                left_count = 0
                
                # Process detected hands
                if results.multi_hand_landmarks:
                    for hand_landmarks, handedness in zip(results.multi_hand_landmarks, 
                                                        results.multi_handedness):
                        # Get hand type
                        hand_type = handedness.classification[0].label
                        
                        # Draw landmarks
                        self.detector.draw_landmarks(frame, hand_landmarks)
                        
                        # Count fingers
                        fingers = self.detector.count_fingers(hand_landmarks, hand_type)
                        
                        # Update counts
                        if hand_type == 'Right':
                            right_count = fingers
                        else:
                            left_count = fingers
                        
                        # Display count for each hand
                        self.display.draw_hand_count(frame, hand_landmarks, hand_type, fingers)
                
                # Display total count
                total_fingers = right_count + left_count
                self.display.draw_total_count(frame, total_fingers)
                
                # Handle distance measurements based on mode
                if self.display.measure_mode == "thumbs":
                    # Get thumb positions of both hands
                    thumb_positions = self.detector.get_thumb_positions(results)
                    if thumb_positions['Left'] and thumb_positions['Right']:
                        distance = self.detector.calculate_distance(
                            thumb_positions['Left'], 
                            thumb_positions['Right']
                        )
                        self.display.draw_distance(frame, distance, 
                                                 [thumb_positions['Left'], 
                                                  thumb_positions['Right']])

                elif self.display.measure_mode == "thumb_index":
                    # Measure thumb-index distance for detected hands
                    if results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            distance = self.detector.get_thumb_index_distance(hand_landmarks)
                            thumb_tip = hand_landmarks.landmark[4]
                            index_tip = hand_landmarks.landmark[8]
                            self.display.draw_distance(frame, distance, 
                                                     [(thumb_tip.x, thumb_tip.y), 
                                                      (index_tip.x, index_tip.y)])

                # Handle mouse control mode
                elif self.display.measure_mode == "mouse":
                    right_hand = self.detector.find_right_hand(results)
                    if right_hand:
                        # Get index finger position for mouse control
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
                            
                            # Draw pointer visualization
                            self.detector.draw_mouse_pointer(frame, x, y)
                    else:
                        # Disable mouse control when hand not detected
                        self.mouse.disable_control()

                # Draw current mode
                self.display.draw_mode(frame)
                
                # Show frame (after all drawing operations)
                self.display.show_frame(frame)
                
                # Handle keyboard input
                if not self.handle_key_press():
                    break
                    
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        self.detector.close()
        self.camera.stop()
        self.display.cleanup()
