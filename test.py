import pyautogui

def test_function():
    # Get the screen size
    screen_width, screen_height = pyautogui.size()
    print(f"Screen size: {screen_width}x{screen_height}")

    # Move the mouse to the center of the screen
    pyautogui.moveTo(screen_width / 2, screen_height / 2, duration=1)
    print("Mouse moved to the center of the screen.")

if __name__ == "__main__":
    test_function()