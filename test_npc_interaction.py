import cv2
import numpy as np
import mss
import time
import tkinter as tk
import ctypes
import os
import pydirectinput
from pynput import keyboard as pynput_keyboard

# 1. 强制 DPI 感知，确保点击坐标精准
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    ctypes.windll.user32.SetProcessDPIAware()

class NPCTracker:
    def __init__(self):
        self.anchor_file = 'NPC.png'
        self.stop_file = 'tet.png'
        self.anchor_img = None
        self.is_processing = False 
        
        self.root = tk.Tk()
        self.root.title("NPC 终极逻辑版")
        self.root.geometry("350x250")
        self.root.attributes("-topmost", True)
        
        tk.Label(self.root, text="T 键功能：", font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Label(self.root, text="1. NPC 循环追踪 (直到消失)", fg="blue").pack()
        tk.Label(self.root, text="2. 固定坐标补刀 (830, 750 / 1150, 1150)", fg="green").pack()
        tk.Label(self.root, text="3. 1.5秒后向上偏移 500 点击", fg="purple").pack()
        tk.Label(self.root, text="* 识别到 tet.png 立即停止 *", fg="red").pack()
        
        self.status_label = tk.Label(self.root, text="状态: 等待初始化", fg="gray")
        self.status_label.pack(pady=10)
        self.load_resources()

    def load_resources(self):
        if os.path.exists(self.anchor_file):
            self.anchor_img = cv2.imread(self.anchor_file)
            self.status_label.config(text="资源已就绪", fg="green")
        else:
            self.status_label.config(text="缺失 NPC.png！", fg="red")

    def find_npc_pos(self):
        """通用识别函数"""
        if self.anchor_img is None: return None
        with mss.mss() as sct:
            img = np.array(sct.grab(sct.monitors[1]))
            img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            res = cv2.matchTemplate(img_bgr, self.anchor_img, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val > 0.8:
                h, w = self.anchor_img.shape[:2]
                return (max_loc[0] + w // 2, max_loc[1] + h // 2)
        return None

    def check_stop(self):
        """检查屏幕是否存在 tet.png，用于中断流程"""
        if not os.path.exists(self.stop_file): return False
        with mss.mss() as sct:
            img = np.array(sct.grab(sct.monitors[1]))
            img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            stop_img = cv2.imread(self.stop_file)
            res = cv2.matchTemplate(img_bgr, stop_img, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            return max_val > 0.8 # 识别到 tet.png 则返回 True

    def on_t_click(self):
        """核心逻辑序列"""
        if self.is_processing: return
        self.is_processing = True 
        
        try:
            # --- 阶段 1：NPC 循环追踪 (如果识别到就从头开始) ---
            while True:
                if self.check_stop(): # 每次循环开头检查中断
                    print("[STOP] 识别到 tet.png，流程终止")
                    return

                pos = self.find_npc_pos()
                if pos:
                    pydirectinput.click(pos[0], pos[1])
                    print(f"[ACTION] 点击 NPC: {pos}")
                    time.sleep(2) # 点击后停 2 秒
                    
                    if self.find_npc_pos(): # 2 秒后还能识别，继续循环
                        print("[LOOP] NPC 还在，重新循环...")
                        continue
                break # 识别不到 NPC，退出循环去执行后续补刀

            # --- 阶段 2：固定坐标补刀 ---
            if self.check_stop(): return 

            time.sleep(0.5)
            pydirectinput.click(830, 750)
            print("[ACTION] 点击固定坐标: (830, 750)")
            
            time.sleep(0.1)
            pydirectinput.click(1150, 1150)
            print("[ACTION] 点击固定坐标: (1150, 1150)")

            # --- 阶段 3：5秒后向上偏移 500 点击 ---
            time.sleep(5) # 5 秒间隔
            
            if self.check_stop(): return 
            
            # 以 1250, 150 为基准向上偏移 500 像素
            pydirectinput.click(1250, 150) 
            print("[FINISH] 流程全结束")

        finally:
            self.is_processing = False 

    def run(self):
        listener = pynput_keyboard.GlobalHotKeys({'t': self.on_t_click})
        listener.start()
        self.root.mainloop()

if __name__ == "__main__":
    NPCTracker().run()