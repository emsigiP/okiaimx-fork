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

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

# Default Center of the screen
center_x = screen_width // 2
center_y = screen_height // 2

# Region of interest (ROI) scan box size (in physical pixels)
ROI_SIZE = 14
left = center_x - ROI_SIZE // 2
top = center_y - ROI_SIZE // 2
right = center_x + ROI_SIZE // 2
bottom = center_y + ROI_SIZE // 2

def update_roi_bounds():
    global left, top, right, bottom
    left = center_x - ROI_SIZE // 2
    top = center_y - ROI_SIZE // 2
    right = center_x + ROI_SIZE // 2
    bottom = center_y + ROI_SIZE // 2

# Color filter for Yellow / Gold target outline (R > 180, G > 140, B < 90)
def is_yellow_outline(r, g, b):
    return r > 180 and g > 140 and b < 90

def click_mouse():
    # Save current cursor pos
    orig_point = POINT()
    user32.GetCursorPos(ctypes.byref(orig_point))
    
    # Move cursor to calibrated center, click, then restore original cursor position
    user32.SetCursorPos(center_x, center_y)
    user32.mouse_event(0x0002, 0, 0, 0, 0) # LEFTDOWN
    time.sleep(0.005)
    user32.mouse_event(0x0004, 0, 0, 0, 0) # LEFTUP
    
    # Restore cursor so it doesn't interrupt the user
    user32.SetCursorPos(orig_point.x, orig_point.y)

print("==================================================")
print("     OKIAIMX HIGH-SPEED AUTOPLAY BOT (DLL-ONLY)   ")
print("==================================================")
print(f"Screen Resolution: {screen_width}x{screen_height}")
print(f"Default Center: ({center_x}, {center_y})")
print(f"Scanning Area: {ROI_SIZE}x{ROI_SIZE} pixels")
print("--------------------------------------------------")
print("How to use:")
print("1. Open the game in fullscreen or windowed mode.")
print("2. Hover your mouse cursor over the game's center")
print("   crosshair and press the 'C' key to calibrate.")
print("3. Ensure Target Outline setting is set to 'Yellow'.")
print("4. Press 'S' key to START / PAUSE the bot.")
print("5. Press 'Q' key to QUIT.")
print("==================================================")

active = False
cooldown_until = 0
s_pressed = False
c_pressed = False
last_debug_time = 0

while True:
    # Check 'S' key state asynchronously (Start/Pause)
    s_state = user32.GetAsyncKeyState(0x53) & 0x8000
    if s_state:
        if not s_pressed:
            active = not active
            print("[BOT] " + ("ACTIVE - Let's hit some targets!" if active else "PAUSED"))
            s_pressed = True
    else:
        s_pressed = False

    # Check 'C' key state asynchronously (Calibrate)
    c_state = user32.GetAsyncKeyState(0x43) & 0x8000
    if c_state:
        if not c_pressed:
            point = POINT()
            user32.GetCursorPos(ctypes.byref(point))
            center_x = point.x
            center_y = point.y
            update_roi_bounds()
            print(f"[BOT] CALIBRATED! Aiming center locked to: ({center_x}, {center_y})")
            c_pressed = True
    else:
        c_pressed = False

    # Check 'Q' key state asynchronously (Quit)
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
        print(f"[DEBUG] Calibrated Center ({center_x},{center_y}) RGB({r}, {g}, {b}) | Yellow? {'YES' if is_yellow_outline(r, g, b) else 'NO'}")

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
