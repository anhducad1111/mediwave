import mediapipe as mp
import cv2

class HandDetector:
    def __init__(self, static_image_mode=False, max_num_hands=1, 
                 min_detection_confidence=0.7, min_tracking_confidence=0.5):
        """Initialize hand detector optimized for mouse control."""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils

    def find_hands(self, frame):
        """Process the frame and detect hands."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.hands.process(rgb_frame)

    def draw_landmarks(self, frame, hand_landmarks):
        """Draw hand landmarks on the frame."""
        self.mp_draw.draw_landmarks(
            frame,
            hand_landmarks,
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
            self.mp_draw.DrawingSpec(color=(0, 0, 255), thickness=1)
        )

    def find_right_hand(self, results):
        """Find the right hand landmarks if present."""
        if results is None or not results.multi_hand_landmarks:
            return None
            
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                            results.multi_handedness):
            if handedness.classification[0].label == "Right":
                return hand_landmarks
        return None

    def get_index_finger_pos(self, hand_landmarks):
        """Get normalized coordinates of index finger tip."""
        if hand_landmarks:
            index_tip = hand_landmarks.landmark[8]  # Index finger tip
            return index_tip.x, index_tip.y
        return None

    def check_pinch(self, hand_landmarks):
        """Check if thumb and index finger are pinched."""
        return self._check_finger_distance(hand_landmarks, 4, 8, 0.05)  # thumb to index
    
    def check_zoom_in(self, hand_landmarks):
        """Check if thumb and middle finger are pinched for zoom in."""
        return self._check_finger_distance(hand_landmarks, 4, 12, 0.05)  # thumb to middle
    
    def check_zoom_out(self, hand_landmarks):
        """Check if thumb and ring finger are pinched for zoom out."""
        return self._check_finger_distance(hand_landmarks, 4, 16, 0.05)  # thumb to ring
        
    def _check_finger_distance(self, hand_landmarks, finger1_id, finger2_id, threshold):
        """Calculate distance between two finger tips."""
        if not hand_landmarks:
            return False
            
        finger1_tip = hand_landmarks.landmark[finger1_id]
        finger2_tip = hand_landmarks.landmark[finger2_id]
        
        # Calculate distance between finger tips
        distance = ((finger1_tip.x - finger2_tip.x)**2 + 
                   (finger1_tip.y - finger2_tip.y)**2 + 
                   (finger1_tip.z - finger2_tip.z)**2)**0.5
        return distance < threshold

    def draw_mouse_pointer(self, frame, x, y):
        """Draw mouse pointer visualization at finger position."""
        h, w = frame.shape[:2]
        cx, cy = int(x * w), int(y * h)
        
        # Draw smaller crosshair
        cv2.line(frame, (cx - 5, cy), (cx + 5, cy), (0, 255, 0), 1)
        cv2.line(frame, (cx, cy - 5), (cx, cy + 5), (0, 255, 0), 1)
    
    def close(self):
        """Close the hands object."""
        self.hands.close()
