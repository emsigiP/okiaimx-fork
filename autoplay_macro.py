import tkinter as tk
from tkinter import messagebox
import ctypes
import time
import sys

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

# Screen size metrics
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

# Default Center coordinates
default_x = screen_width // 2
default_y = screen_height // 2

class AutoplayBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OKIAIMX Autoplay Bot")
        self.root.geometry("400x550")
        self.root.configure(bg="#11151e") # Dark Valorant navy-black theme
        self.root.resizable(False, False)
        
        # State variables
        self.active = False
        self.center_x = default_x
        self.center_y = default_y
        self.roi_size = 14
        self.target_color = "yellow"
        self.cooldown_until = 0
        
        # Hotkey tracking states
        self.s_was_pressed = False
        self.c_was_pressed = False
        self.q_was_pressed = False
        
        self.create_widgets()
        self.update_gui_values()
        
        # Start the background poll loop
        self.root.after(5, self.bot_loop)
        
    def create_widgets(self):
        # Header Title
        title_label = tk.Label(
            self.root, 
            text="OKIAIMX AUTOPLAY BOT", 
            font=("Arial", 16, "bold"), 
            bg="#11151e", 
            fg="#ff4655" # Valorant Red
        )
        title_label.pack(pady=15)
        
        # Status Frame
        status_frame = tk.Frame(self.root, bg="#1a222f", bd=1, relief="solid")
        status_frame.pack(fill="x", padx=20, pady=5)
        
        self.status_title = tk.Label(
            status_frame, 
            text="STATUS", 
            font=("Arial", 10, "semibold"), 
            bg="#1a222f", 
            fg="#768090"
        )
        self.status_title.pack(pady=(8, 2))
        
        self.status_val = tk.Label(
            status_frame, 
            text="PAUSED", 
            font=("Arial", 22, "bold"), 
            bg="#1a222f", 
            fg="#ff4655"
        )
        self.status_val.pack(pady=(0, 8))

        # Coordinates display frame
        coords_frame = tk.Frame(self.root, bg="#11151e")
        coords_frame.pack(fill="x", padx=20, pady=10)
        
        self.coords_lbl = tk.Label(
            coords_frame, 
            text=f"Aiming Center: ({self.center_x}, {self.center_y})", 
            font=("Arial", 11), 
            bg="#11151e", 
            fg="#ffffff"
        )
        self.coords_lbl.pack()
        
        # Settings section
        settings_label = tk.Label(
            self.root, 
            text="SETTINGS", 
            font=("Arial", 11, "bold"), 
            bg="#11151e", 
            fg="#768090"
        )
        settings_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        # Outline Color selector
        color_frame = tk.Frame(self.root, bg="#11151e")
        color_frame.pack(fill="x", padx=20, pady=5)
        
        tk.Label(
            color_frame, 
            text="Target Outline:", 
            font=("Arial", 11), 
            bg="#11151e", 
            fg="#ffffff"
        ).pack(side="left")
        
        self.color_var = tk.StringVar(value="Yellow")
        color_opt = tk.OptionMenu(
            color_frame, 
            self.color_var, 
            "Yellow", 
            "Red", 
            command=self.on_color_change
        )
        color_opt.configure(
            bg="#1a222f", 
            fg="#ffffff", 
            activebackground="#ff4655", 
            activeforeground="#ffffff", 
            highlightthickness=0,
            font=("Arial", 10),
            width=10
        )
        color_opt["menu"].configure(bg="#1a222f", fg="#ffffff", activebackground="#ff4655")
        color_opt.pack(side="right")
        
        # ROI Size Slider
        roi_frame = tk.Frame(self.root, bg="#11151e")
        roi_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(
            roi_frame, 
            text="Scan Box Size (px):", 
            font=("Arial", 11), 
            bg="#11151e", 
            fg="#ffffff"
        ).pack(side="left")
        
        self.roi_scale = tk.Scale(
            roi_frame, 
            from_=6, 
            to=30, 
            orient="horizontal", 
            bg="#11151e", 
            fg="#ffffff", 
            troughcolor="#1a222f",
            highlightthickness=0,
            resolution=2,
            command=self.on_roi_change
        )
        self.roi_scale.set(14)
        self.roi_scale.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Control Buttons
        btn_frame = tk.Frame(self.root, bg="#11151e")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        self.toggle_btn = tk.Button(
            btn_frame, 
            text="START BOT (S)", 
            font=("Arial", 11, "bold"), 
            bg="#0f1922", 
            fg="#31ff88", 
            activebackground="#31ff88", 
            activeforeground="#0f1922",
            height=2,
            command=self.toggle_bot
        )
        self.toggle_btn.pack(fill="x", pady=5)
        
        calibrate_btn = tk.Button(
            btn_frame, 
            text="CALIBRATE POSITION (C)", 
            font=("Arial", 11, "bold"), 
            bg="#0f1922", 
            fg="#ffffff", 
            activebackground="#ffffff", 
            activeforeground="#0f1922",
            height=2,
            command=self.calibrate_pos
        )
        calibrate_btn.pack(fill="x", pady=5)
        
        # Instructions/Hotkeys footer
        footer_frame = tk.Frame(self.root, bg="#11151e")
        footer_frame.pack(side="bottom", fill="x", pady=15)
        
        instructions = (
            "Hotkeys (Works Globally):\n"
            "Press 'S' to Start/Pause Bot  |  Press 'C' to Calibrate Center\n"
            "Press 'Q' to Quit Macro safely"
        )
        tk.Label(
            footer_frame, 
            text=instructions, 
            font=("Arial", 8), 
            bg="#11151e", 
            fg="#768090",
            justify="center"
        ).pack()

    def on_color_change(self, val):
        self.target_color = val.lower()
        print(f"[BOT] Target outline scan color set to: {val}")

    def on_roi_change(self, val):
        self.roi_size = int(val)

    def toggle_bot(self):
        self.active = not self.active
        self.update_gui_values()

    def calibrate_pos(self):
        point = POINT()
        user32.GetCursorPos(ctypes.byref(point))
        self.center_x = point.x
        self.center_y = point.y
        self.update_gui_values()
        print(f"[BOT] Calibrated center aiming point to: ({self.center_x}, {self.center_y})")

    def update_gui_values(self):
        if self.active:
            self.status_val.configure(text="ACTIVE", fg="#31ff88")
            self.toggle_btn.configure(text="PAUSE BOT (S)", fg="#ff4655")
        else:
            self.status_val.configure(text="PAUSED", fg="#ff4655")
            self.toggle_btn.configure(text="START BOT (S)", fg="#31ff88")
            
        self.coords_lbl.configure(text=f"Aiming Center: ({self.center_x}, {self.center_y})")

    def click_mouse(self):
        # Save current cursor pos
        orig_point = POINT()
        user32.GetCursorPos(ctypes.byref(orig_point))
        
        # Move cursor to calibrated center, click, then restore original cursor position
        user32.SetCursorPos(self.center_x, self.center_y)
        user32.mouse_event(0x0002, 0, 0, 0, 0) # LEFTDOWN
        time.sleep(0.005)
        user32.mouse_event(0x0004, 0, 0, 0, 0) # LEFTUP
        
        # Restore cursor
        user32.SetCursorPos(orig_point.x, orig_point.y)

    def is_yellow_outline(self, r, g, b):
        return r > 180 and g > 140 and b < 90

    def is_red_outline(self, r, g, b):
        return r > 180 and g < 100 and b < 100

    def bot_loop(self):
        # 1. Asynchronously read global keys (since Tkinter window might not be focused)
        s_state = user32.GetAsyncKeyState(0x53) & 0x8000
        if s_state:
            if not self.s_was_pressed:
                self.toggle_bot()
                self.s_was_pressed = True
        else:
            self.s_was_pressed = False

        c_state = user32.GetAsyncKeyState(0x43) & 0x8000
        if c_state:
            if not self.c_was_pressed:
                self.calibrate_pos()
                self.c_was_pressed = True
        else:
            self.c_was_pressed = False

        q_state = user32.GetAsyncKeyState(0x51) & 0x8000
        if q_state:
            if not self.q_was_pressed:
                print("[BOT] Quitting script via hotkey.")
                self.root.destroy()
                return
        else:
            self.q_was_pressed = False

        # 2. Perform the color scanning loop if active
        if self.active:
            now = time.time()
            if now >= self.cooldown_until:
                # Calc ROI boundaries
                left = self.center_x - self.roi_size // 2
                top = self.center_y - self.roi_size // 2
                right = self.center_x + self.roi_size // 2
                bottom = self.center_y + self.roi_size // 2
                
                # Fetch desktop device context
                hdc = user32.GetDC(0)
                target_found = False
                
                # Color check function selector
                is_outline_match = self.is_yellow_outline if self.target_color == "yellow" else self.is_red_outline
                
                # Scan the ROI box
                for y in range(top, bottom):
                    for x in range(left, right):
                        color = gdi32.GetPixel(hdc, x, y)
                        r = color & 0xFF
                        g = (color >> 8) & 0xFF
                        b = (color >> 16) & 0xFF
                        
                        if is_outline_match(r, g, b):
                            target_found = True
                            break
                    if target_found:
                        break
                        
                user32.ReleaseDC(0, hdc)
                
                if target_found:
                    self.click_mouse()
                    self.cooldown_until = now + 0.110
                    print(f"[HIT] Shot triggered at calibrated center ({self.center_x}, {self.center_y})")

        # Repeat this loop after 2 milliseconds
        self.root.after(2, self.bot_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoplayBotGUI(root)
    root.mainloop()
