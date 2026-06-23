import cv2
import numpy as np
import mss
import tkinter as tk
from tkinter import messagebox
import ctypes
import os
import json
import pydirectinput
import requests
import base64
import time

# 1. 强制 DPI 感知
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    ctypes.windll.user32.SetProcessDPIAware()

class RitualMasterFinal:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ritual 终极闭环系统")
        self.root.geometry("380x520")
        self.root.attributes("-topmost", True)

        self.config_file = 'anchor_config.json'
        self.api_key = "sk-e7fd8fabc0a14dfbaf044c0c5b4b142b"
        self.sct = mss.mss()
        self.anchors = []
        
        # 核心坐标数据
        self.point_offsets = [] 
        self.start_btn_offset = None 
        
        # UI 布局
        tk.Label(self.root, text="Ritual 坐标采集与自动闭环", font=('Arial', 12, 'bold')).pack(pady=10)
        
        tk.Button(self.root, text="1. 采集三词缀中心点", command=lambda: self.start_picking("points"), bg="#2196F3", fg="white", width=30).pack(pady=5)
        tk.Button(self.root, text="4. 采集【开始】按钮中心点", command=lambda: self.start_picking("start_btn"), bg="#E91E63", fg="white", width=30).pack(pady=5)
        
        tk.Label(self.root, text="--- 逻辑执行 ---").pack(pady=10)
        tk.Button(self.root, text="2. 遍历/决策/并自动开始", command=self.run_full_logic, bg="#9C27B0", fg="white", width=30, height=2).pack(pady=5)
        
        tk.Button(self.root, text="3. 保存所有配置到 JSON", command=self.save_all, bg="#4CAF50", fg="white", width=30).pack(pady=5)

        self.status_label = tk.Label(self.root, text="状态: 等待操作", fg="gray")
        self.status_label.pack(pady=15)
        
        self.load_resources()

    def load_resources(self):
        """载入锚点图和 JSON 配置"""
        self.anchors = []
        for f in os.listdir('.'):
            if f.startswith('ritual_anchor') and f.endswith('.png'):
                img = cv2.imread(f)
                if img is not None: self.anchors.append((img, f))
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.point_offsets = data.get("ritual_points_v2", [])
                    self.start_btn_offset = data.get("start_button_offset_v2")
                    self.priority = data.get("priority", ["通货", "地图", "幸运"])
                    if self.point_offsets:
                        self.status_label.config(text="配置已载入", fg="green")
            except: pass

    def find_anchor(self):
        """寻找当前屏幕最佳锚点"""
        img = np.array(self.sct.grab(self.sct.monitors[1]))
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        best = {"val": 0, "loc": (0, 0)}
        for temp, name in self.anchors:
            res = cv2.matchTemplate(img_bgr, temp, cv2.TM_CCOEFF_NORMED)
            _, val, _, loc = cv2.minMaxLoc(res)
            if val > best["val"]: best = {"val": val, "loc": loc}
        return best if best["val"] > 0.8 else None

    def start_picking(self, mode):
        """取点逻辑：词缀点(3个)或开始按钮(1个)"""
        anchor = self.find_anchor()
        if not anchor:
            messagebox.showwarning("错误", "未发现锚点，请确保祭坛界面已打开")
            return

        img_data = np.array(self.sct.grab(self.sct.monitors[1]))
        full_img = cv2.cvtColor(img_data, cv2.COLOR_BGRA2BGR)
        temp_points = []
        limit = 3 if mode == "points" else 1
        win_name = "PICKER - " + ("Click 3 Affixes" if mode == "points" else "Click START Button")

        def on_mouse(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                dx, dy = x - anchor["loc"][0], y - anchor["loc"][1]
                temp_points.append((dx, dy))
                cv2.circle(full_img, (x, y), 7, (0, 0, 255), -1)
                cv2.putText(full_img, str(len(temp_points)), (x+10, y), 1, 1.5, (0,0,255), 2)
                cv2.imshow(win_name, full_img)
                if len(temp_points) >= limit:
                    messagebox.showinfo("完成", f"已采集 {limit} 个点，请关闭图片窗口")

        cv2.namedWindow(win_name)
        cv2.setMouseCallback(win_name, on_mouse)
        cv2.imshow(win_name, full_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        if mode == "points": self.point_offsets = temp_points
        else: self.start_btn_offset = temp_points[0]
        self.status_label.config(text=f"新点位采集成功", fg="blue")

    def run_full_logic(self):
        """核心：遍历 -> OCR -> 优先级决策 -> 点击 -> 自动点击开始按钮"""
        anchor = self.find_anchor()
        if not anchor or len(self.point_offsets) < 3 or not self.start_btn_offset:
            messagebox.showwarning("错误", "请确保已采集三词缀点和开始按钮点")
            return

        results = []
        for i, offset in enumerate(self.point_offsets):
            tx, ty = anchor["loc"][0] + offset[0], anchor["loc"][1] + offset[1]
            pydirectinput.moveTo(int(tx), int(ty), duration=0.1)
            time.sleep(0.3)
            
            # 动态 OCR
            monitor = {"top": int(ty - 40), "left": int(tx - 200), "width": 400, "height": 80}
            img = np.array(self.sct.grab(monitor))
            _, enc = cv2.imencode('.jpg', cv2.cvtColor(img, cv2.COLOR_BGRA2BGR))
            b64 = base64.b64encode(enc).decode('utf-8')
            
            payload = {"model": "qwen-vl-ocr", "input": {"messages": [{"role": "user", "content": [{"image": f"data:image/jpeg;base64,{b64}"}, {"text": "直接给文字内容。"}]}]}}
            try:
                res = requests.post("https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation", 
                                    headers={"Authorization": f"Bearer {self.api_key}"}, json=payload, timeout=5).json()
                text = res['output']['choices'][0]['message']['content'][0]['text']
            except: text = "OCR Error"
            results.append({"pos": (tx, ty), "text": text})

        # 优先级决策
        target = results[1] 
        for p_word in self.priority:
            found = False
            for r in results:
                if p_word in r["text"]: target, found = r, True; break
            if found: break
        
        # 执行点击
        pydirectinput.click(int(target["pos"][0]), int(target["pos"][1]))
        time.sleep(0.5)

        # 自动点击开始按钮
        sx, sy = anchor["loc"][0] + self.start_btn_offset[0], anchor["loc"][1] + self.start_btn_offset[1]
        pydirectinput.click(int(sx), int(sy))
        self.status_label.config(text=f"已选: {target['text']} 并开始", fg="green")

    def save_all(self):
        """保存至 JSON"""
        data = {}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f: data = json.load(f)
            except: pass
        
        data["ritual_points_v2"] = self.point_offsets
        data["start_button_offset_v2"] = self.start_btn_offset
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("成功", "坐标已持久化保存")

if __name__ == "__main__":
    app = RitualMasterFinal()
    app.root.mainloop()