import ctypes
import time
import os
from PIL import ImageGrab

# Screen size metrics
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

# Center of the screen (assuming browser is maximized / fullscreen)
center_x = screen_width // 2
center_y = screen_height // 2

# Region of interest (ROI) box size around the center of the screen (in pixels)
ROI_SIZE = 12
left = center_x - ROI_SIZE // 2
top = center_y - ROI_SIZE // 2
right = center_x + ROI_SIZE // 2
bottom = center_y + ROI_SIZE // 2

# Color detection filter for Yellow / Gold target outline (R > 200, G > 160, B < 80)
def is_yellow_outline(r, g, b):
    return r > 200 and g > 160 and b < 80

def click_mouse():
    # MOUSEEVENTF_LEFTDOWN = 0x0002, MOUSEEVENTF_LEFTUP = 0x0004
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.01)
    user32.mouse_event(0x0004, 0, 0, 0, 0)

print("==================================================")
print("     OKIAIMX YELLOW OUTLINE AUTOPLAY MACRO        ")
print("==================================================")
print(f"Screen Resolution: {screen_width}x{screen_height}")
print(f"Aiming Center: ({center_x}, {center_y})")
print("ROI Scan Box: 12x12 pixels")
print("--------------------------------------------------")
print("How to use:")
print("1. Open the game in fullscreen mode (Press F11).")
print("2. Ensure Target Outline setting is set to 'Yellow'.")
print("3. Start a game mode (Left Side, Right Side, etc.).")
print("4. Press 'S' key to START / PAUSE the autoplay bot.")
print("5. Press 'Q' key to QUIT the script.")
print("==================================================")

active = False
cooldown_until = 0
s_pressed = False

while True:
    # Check key state asynchronously (0x53 is 'S' key)
    s_state = user32.GetAsyncKeyState(0x53) & 0x8000
    if s_state:
        if not s_pressed:
            active = not active
            print("[MACRO] " + ("RUNNING - Autoplay bot active!" if active else "PAUSED"))
            s_pressed = True
    else:
        s_pressed = False

    # Check key state asynchronously (0x51 is 'Q' key)
    q_state = user32.GetAsyncKeyState(0x51) & 0x8000
    if q_state:
        print("[MACRO] Shutting down. Goodbye!")
        break

    if active:
        now = time.time()
        if now >= cooldown_until:
            # Capture the 12x12 area at the screen center
            bbox = (left, top, right, bottom)
            try:
                img = ImageGrab.grab(bbox)
                yellow_detected = False
                
                # Scan ROI for outline pixels
                for x in range(img.width):
                    for y in range(img.height):
                        r, g, b = img.getpixel((x, y))[:3]
                        if is_yellow_outline(r, g, b):
                            yellow_detected = True
                            break
                    if yellow_detected:
                        break
                
                if yellow_detected:
                    click_mouse()
                    # 120ms cooldown to prevent double clicking the same target
                    cooldown_until = now + 0.120
                    print(f"[HIT] Click triggered at {time.strftime('%H:%M:%S')}")
            except Exception as e:
                print(f"[ERROR] Screen capture failed: {e}")
                active = False

    time.sleep(0.005)  # 5ms tick rate
