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
            self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            self.mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2)
        )

    def calculate_distance(self, point1, point2):
        """Calculate 3D distance between two points."""
        return ((point1[0] - point2[0])**2 + 
                (point1[1] - point2[1])**2 + 
                (point1[2] - point2[2])**2)**0.5

    def get_thumb_positions(self, results):
        """Get thumb tip positions of both hands."""
        thumb_positions = {'Left': None, 'Right': None}
        
        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, 
                                                results.multi_handedness):
                hand_type = handedness.classification[0].label
                thumb_tip = hand_landmarks.landmark[4]  # Thumb tip landmark
                thumb_positions[hand_type] = (thumb_tip.x, thumb_tip.y, thumb_tip.z)
        
        return thumb_positions

    def get_thumb_index_distance(self, hand_landmarks):
        """Calculate distance between thumb and index finger tips."""
        thumb_tip = hand_landmarks.landmark[4]  # Thumb tip
        index_tip = hand_landmarks.landmark[8]  # Index tip
        
        thumb_pos = (thumb_tip.x, thumb_tip.y, thumb_tip.z)
        index_pos = (index_tip.x, index_tip.y, index_tip.z)
        
        return self.calculate_distance(thumb_pos, index_pos)

    def count_fingers(self, hand_landmarks, handedness):
        """Count fingers for a given hand."""
        finger_count = 0
        points = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
        
        # Thumb
        if handedness == 'Right':
            if points[4][0] < points[3][0]:
                finger_count += 1
        else:
            if points[4][0] > points[3][0]:
                finger_count += 1
        
        # Other fingers
        tips = [8, 12, 16, 20]  # Index, middle, ring, pinky tips
        tips_base = [6, 10, 14, 18]  # Corresponding base joints
        for tip, base in zip(tips, tips_base):
            if points[tip][1] < points[base][1]:
                finger_count += 1
                
        return finger_count

    def find_right_hand(self, results):
        """Find the right hand landmarks if present."""
        if not results.multi_hand_landmarks:
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
        if not hand_landmarks:
            return False
            
        # Using existing get_thumb_index_distance method
        distance = self.get_thumb_index_distance(hand_landmarks)
        return distance < 0.05  # Pinch threshold

    def draw_mouse_pointer(self, frame, x, y):
        """Draw mouse pointer visualization at finger position."""
        h, w = frame.shape[:2]
        cx, cy = int(x * w), int(y * h)
        
        # Draw crosshair
        cv2.line(frame, (cx - 10, cy), (cx + 10, cy), (0, 255, 0), 2)
        cv2.line(frame, (cx, cy - 10), (cx, cy + 10), (0, 255, 0), 2)
    
    def close(self):
        """Close the hands object."""
        self.hands.close()
