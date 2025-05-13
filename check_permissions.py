import pyautogui
import time
from datetime import datetime

print("Nh?n Ctrl + C d? d?ng.\n")
try:
    while True:
        x, y = pyautogui.position()
        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{now}] Mouse at ({x}, {y})", end='\r')
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\nÐã d?ng theo yêu c?u.")