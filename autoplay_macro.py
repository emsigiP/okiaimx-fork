import ctypes
import time

# 1. Make the process DPI-aware on Windows so coordinates match the screen pixels
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

# Setup GDI and User32 dlls
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

# Center of the screen
center_x = screen_width // 2
center_y = screen_height // 2

# Region of interest (ROI) scan box size (in physical pixels)
# Scanning a 14x14 box at the exact center of the screen
ROI_SIZE = 14
left = center_x - ROI_SIZE // 2
top = center_y - ROI_SIZE // 2
right = center_x + ROI_SIZE // 2
bottom = center_y + ROI_SIZE // 2

# Color filter for Yellow / Gold target outline (R > 180, G > 140, B < 90)
def is_yellow_outline(r, g, b):
    return r > 180 and g > 140 and b < 90

def click_mouse():
    # MOUSEEVENTF_LEFTDOWN = 0x0002, MOUSEEVENTF_LEFTUP = 0x0004
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.005)
    user32.mouse_event(0x0004, 0, 0, 0, 0)

print("==================================================")
print("     OKIAIMX HIGH-SPEED AUTOPLAY BOT (DLL-ONLY)   ")
print("==================================================")
print(f"Screen Resolution: {screen_width}x{screen_height}")
print(f"Aiming Center: ({center_x}, {center_y})")
print(f"Scanning Area: {ROI_SIZE}x{ROI_SIZE} pixels")
print("--------------------------------------------------")
print("How to use:")
print("1. Open the game in fullscreen mode (Press F11).")
print("2. Ensure Target Outline setting is set to 'Yellow'.")
print("3. Start a game mode (Left Side, Right Side, etc.).")
print("4. Press 'S' key to START / PAUSE the bot.")
print("5. Press 'Q' key to QUIT.")
print("==================================================")

active = False
cooldown_until = 0
s_pressed = False
last_debug_time = 0

while True:
    # Check 'S' key state asynchronously
    s_state = user32.GetAsyncKeyState(0x53) & 0x8000
    if s_state:
        if not s_pressed:
            active = not active
            print("[BOT] " + ("ACTIVE - Let's hit some targets!" if active else "PAUSED"))
            s_pressed = True
    else:
        s_pressed = False

    # Check 'Q' key state asynchronously
    q_state = user32.GetAsyncKeyState(0x51) & 0x8000
    if q_state:
        print("[BOT] Shutting down...")
        break

    now = time.time()

    # Debug print: Shows color at screen center when paused to verify colors
    if not active and now - last_debug_time >= 1.5:
        last_debug_time = now
        # Get Desktop Device Context
        hdc = user32.GetDC(0)
        # Read COLORREF (0x00BBGGRR)
        color = gdi32.GetPixel(hdc, center_x, center_y)
        user32.ReleaseDC(0, hdc)
        
        r = color & 0xFF
        g = (color >> 8) & 0xFF
        b = (color >> 16) & 0xFF
        print(f"[DEBUG] Center pixel: RGB({r}, {g}, {b}) | Yellow outline? {'YES' if is_yellow_outline(r, g, b) else 'NO'}")

    if active:
        if now >= cooldown_until:
            hdc = user32.GetDC(0)
            yellow_detected = False
            
            # Ultra-fast color scanning using GDI GetPixel (takes ~0.05ms)
            for y in range(top, bottom):
                for x in range(left, right):
                    color = gdi32.GetPixel(hdc, x, y)
                    r = color & 0xFF
                    g = (color >> 8) & 0xFF
                    b = (color >> 16) & 0xFF
                    
                    if is_yellow_outline(r, g, b):
                        yellow_detected = True
                        break
                if yellow_detected:
                    break
            
            user32.ReleaseDC(0, hdc)

            if yellow_detected:
                click_mouse()
                # 110ms cooldown to allow the target to pass
                cooldown_until = now + 0.110
                print(f"[HIT] Target shot at {time.strftime('%H:%M:%S')}")

    time.sleep(0.001)  # 1ms loop sleep (up to 1000 scans per second)
