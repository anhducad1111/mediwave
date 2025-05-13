import time
import numpy as np
import pyautogui

class MouseController:
    def __init__(self, smoothing_factor=0.8, screen_w=None, screen_h=None):
        """Initialize mouse controller with optional screen dimensions."""
        self.debug_prefix = "[MouseController]"
        self.hand_lost_threshold = 0.2  # seconds to wait before considering hand truly lost
        self.last_hand_detected_time = time.time()
        
        # Zoom gesture cooldown to prevent rapid triggers
        self.zoom_cooldown = 0.5  # seconds
        self.last_zoom_time = 0
        try:
            # Get screen resolution from pyautogui if not provided
            if screen_w is None or screen_h is None:
                screen_w, screen_h = pyautogui.size()
                print(f"Screen resolution detected: {screen_w}x{screen_h}")
            
            self.screen_w = screen_w
            self.screen_h = screen_h
            self.smoothing_factor = smoothing_factor
            self.last_x = screen_w // 2  # Start at screen center
            self.last_y = screen_h // 2
            self.is_dragging = False
            self.pinch_start_time = None
            self.is_mouse_down = False
            
            # Move to center initially
            pyautogui.moveTo(self.last_x, self.last_y)
            
        except Exception as e:
            print(f"Error initializing mouse control: {str(e)}")
            self.screen_w = 1920
            self.screen_h = 1080
            self.last_x = 960
            self.last_y = 540
    
    def smooth_position(self, x, y):
        """Apply smoothing to reduce jitter. Higher smoothing_factor = more responsive."""
        try:
            smoothed_x = self.last_x + (x - self.last_x) * self.smoothing_factor
            smoothed_y = self.last_y + (y - self.last_y) * self.smoothing_factor
            
            # Ensure coordinates are within screen bounds
            smoothed_x = np.clip(smoothed_x, 0, self.screen_w - 1)
            smoothed_y = np.clip(smoothed_y, 0, self.screen_h - 1)
            
            self.last_x = smoothed_x
            self.last_y = smoothed_y
            
            return int(smoothed_x), int(smoothed_y)
        except Exception as e:
            print(f"Error in smooth_position: {str(e)}")
            return self.last_x, self.last_y
    
    def map_coordinates(self, x, y, input_w, input_h):
        """Map input coordinates to screen coordinates."""
        try:
            # Map to screen coordinates directly
            screen_x = x * self.screen_w
            screen_y = y * self.screen_h
            
            # Ensure coordinates are within bounds
            screen_x = np.clip(screen_x, 0, self.screen_w - 1)
            screen_y = np.clip(screen_y, 0, self.screen_h - 1)
            
            return screen_x, screen_y
        except Exception as e:
            print(f"Error in map_coordinates: {str(e)}")
            return self.last_x, self.last_y
    
    def move_mouse(self, x, y):
        """Move mouse to specified coordinates."""
        try:
            x = int(x)
            y = int(y)
            if 0 <= x < self.screen_w and 0 <= y < self.screen_h:
                if abs(x - self.last_x) > 0 or abs(y - self.last_y) > 0:
                    pyautogui.moveTo(x, y)
                    self.last_x = x
                    self.last_y = y
        except Exception as e:
            print(f"Error moving mouse: {str(e)}")
    
    def handle_pinch(self, is_pinched):
        """Handle pinch gesture for mouse clicks and dragging."""
        try:
            current_time = time.time()
            self.last_hand_detected_time = current_time  # Update last hand detection time
            
            if is_pinched:
                if not self.is_dragging:
                    if self.pinch_start_time is None:
                        # Start timing the pinch
                        self.pinch_start_time = current_time
                        if not self.is_mouse_down:
                            pyautogui.mouseDown()
                            self.is_mouse_down = True
                    elif current_time - self.pinch_start_time >= 0.5:
                        # Convert to drag after 0.5s
                        self.is_dragging = True
            else:
                if self.pinch_start_time is not None:
                    if not self.is_dragging:
                        # Quick pinch and release = click
                        if self.is_mouse_down:
                            pyautogui.mouseUp()
                            pyautogui.click()
                            self.is_mouse_down = False
                    else:
                        # End dragging
                        if self.is_mouse_down:
                            pyautogui.mouseUp()
                            self.is_mouse_down = False
                        self.is_dragging = False
                    self.pinch_start_time = None
        except Exception as e:
            print(f"Error in handle_pinch: {str(e)}")
            self.disable_control()
    
    def handle_zoom(self, is_zoom_in, is_zoom_out):
        """Handle zoom in/out gestures."""
        try:
            current_time = time.time()
            self.last_hand_detected_time = current_time
            
            # Check cooldown to prevent rapid zooming
            if current_time - self.last_zoom_time < self.zoom_cooldown:
                return
                
            if is_zoom_in:
                pyautogui.hotkey('ctrl', '+')
                self.last_zoom_time = current_time
            elif is_zoom_out:
                pyautogui.hotkey('ctrl', '-')
                self.last_zoom_time = current_time
                
        except Exception as e:
            print(f"Error in handle_zoom: {str(e)}")
    
    def disable_control(self):
        """Reset control state when hand is not detected."""
        try:
            current_time = time.time()
            # Only reset states if hand has been lost for longer than threshold
            if current_time - self.last_hand_detected_time > self.hand_lost_threshold:
                if self.is_mouse_down:
                    pyautogui.mouseUp()
                    self.is_mouse_down = False
                if self.is_dragging:
                    self.is_dragging = False
                    self.pinch_start_time = None
        except Exception as e:
            print(f"Error in disable_control: {str(e)}")
