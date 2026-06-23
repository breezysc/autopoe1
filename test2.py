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
        self.root.title("Ritual 终极闭环系统 (start.png 锚点版)")
        self.root.geometry("380x520")
        self.root.attributes("-topmost", True)

        self.config_file = 'anchor_config.json'
        self.api_key = "sk-e7fd8fabc0a14dfbaf044c0c5b4b142b"
        self.sct = mss.mss()
        self.anchor_img = None
        
        # 核心坐标数据
        self.point_offsets = [] # 存储相对于 start.png 左上角的偏移
        self.start_btn_offset = [50, 25] # 默认点击按钮中心（相对于左上角）
        
        # UI 布局
        tk.Label(self.root, text="坐标系基准：start.png 左上角", font=('Arial', 10, 'bold')).pack(pady=10)
        
        tk.Button(self.root, text="1. 采集三词缀中心点 (相对于开始按钮)", command=lambda: self.start_picking("points"), bg="#2196F3", fg="white", width=35).pack(pady=5)
        tk.Button(self.root, text="2. 采集点击开始按钮的精准点", command=lambda: self.start_picking("start_btn"), bg="#E91E63", fg="white", width=35).pack(pady=5)
        
        tk.Label(self.root, text="--- 逻辑执行 ---").pack(pady=10)
        tk.Button(self.root, text="▶ 运行全流程 (基于按钮偏移识别点击)", command=self.run_full_logic, bg="#9C27B0", fg="white", width=35, height=2).pack(pady=5)
        
        tk.Button(self.root, text="3. 保存配置到 JSON", command=self.save_all, bg="#4CAF50", fg="white", width=35).pack(pady=5)

        self.status_label = tk.Label(self.root, text="状态: 等待操作", fg="gray")
        self.status_label.pack(pady=15)
        
        self.load_resources()

    def load_resources(self):
        """只加载 start.png 作为核心基准"""
        if os.path.exists('start.png'):
            self.anchor_img = cv2.imread('start.png')
            self.status_label.config(text="start.png 基准已就绪", fg="green")
        else:
            self.status_label.config(text="缺失 start.png！", fg="red")

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.point_offsets = data.get("ritual_points_v1", [])
                    self.start_btn_offset = data.get("start_button_offset_v1", [50, 25])
            except: pass

    def find_anchor(self):
        """寻找屏幕上的 start.png 按钮"""
        if self.anchor_img is None: return None
        img = np.array(self.sct.grab(self.sct.monitors[1]))
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        res = cv2.matchTemplate(img_bgr, self.anchor_img, cv2.TM_CCOEFF_NORMED)
        _, val, _, loc = cv2.minMaxLoc(res)
        
        if val > 0.8:
            return {"val": val, "loc": loc} # 返回左上角坐标
        return None

    def start_picking(self, mode):
        """取点逻辑：计算点击位置相对于按钮左上角的偏移"""
        anchor = self.find_anchor()
        if not anchor:
            messagebox.showwarning("错误", "未在屏幕发现“开始”按钮，请先打开祭坛界面")
            return

        img_data = np.array(self.sct.grab(self.sct.monitors[1]))
        full_img = cv2.cvtColor(img_data, cv2.COLOR_BGRA2BGR)
        temp_points = []
        limit = 3 if mode == "points" else 1
        win_name = "PICKER"

        def on_mouse(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                # 记录相对于 start.png 左上角的偏移
                dx, dy = x - anchor["loc"][0], y - anchor["loc"][1]
                temp_points.append([dx, dy])
                cv2.circle(full_img, (x, y), 7, (0, 0, 255), -1)
                cv2.imshow(win_name, full_img)
                if len(temp_points) >= limit:
                    messagebox.showinfo("完成", f"已记录 {limit} 个偏移点")

        cv2.namedWindow(win_name)
        cv2.setMouseCallback(win_name, on_mouse)
        cv2.imshow(win_name, full_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        if mode == "points": self.point_offsets = temp_points
        else: self.start_btn_offset = temp_points[0]
        self.status_label.config(text="点位偏移记录成功", fg="blue")

    def run_full_logic(self):
        """基于 start.png 锚点的随动决策"""
        anchor = self.find_anchor()
        if not anchor or len(self.point_offsets) < 3:
            messagebox.showwarning("错误", "配置不全或未发现按钮")
            return

        # 1. 巡检与识字
        results = []
        for i, offset in enumerate(self.point_offsets):
            tx, ty = anchor["loc"][0] + offset[0], anchor["loc"][1] + offset[1]
            pydirectinput.moveTo(int(tx), int(ty), duration=0.1)
            time.sleep(0.3)
            
            monitor = {"top": int(ty - 40), "left": int(tx - 200), "width": 400, "height": 80}
            img_ocr = np.array(self.sct.grab(monitor))
            _, enc = cv2.imencode('.jpg', cv2.cvtColor(img_ocr, cv2.COLOR_BGRA2BGR))
            b64 = base64.b64encode(enc).decode('utf-8')
            
            payload = {"model": "qwen-vl-ocr", "input": {"messages": [{"role": "user", "content": [{"image": f"data:image/jpeg;base64,{b64}"}, {"text": "直接给文字内容。"}]}]}}
            try:
                res = requests.post("https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation", 
                                    headers={"Authorization": f"Bearer {self.api_key}"}, json=payload).json()
                text = res['output']['choices'][0]['message']['content'][0]['text']
            except: text = "Error"
            results.append({"pos": (tx, ty), "text": text})

        # 2. 点击词缀
        # 此处简化：默认点第一个（你可以根据 JSON 优先级增加筛选逻辑）
        pydirectinput.click(int(results[0]["pos"][0]), int(results[0]["pos"][1]))
        time.sleep(0.5)

        # 3. 点击“开始”按钮本身
        sx = anchor["loc"][0] + self.start_btn_offset[0]
        sy = anchor["loc"][1] + self.start_btn_offset[1]
        pydirectinput.click(int(sx), int(sy))
        self.status_label.config(text="执行完毕", fg="green")

    def save_all(self):
        """保存"""
        # 读取现有数据
        existing_data = {}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except: pass
        
        # 更新数据
        existing_data["ritual_points_v1"] = self.point_offsets
        existing_data["start_button_offset_v1"] = self.start_btn_offset
        
        # 保存数据
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("成功", "坐标系偏移已保存")

if __name__ == "__main__":
    app = RitualMasterFinal()
    app.root.mainloop()