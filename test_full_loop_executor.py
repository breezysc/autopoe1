import cv2
import numpy as np
import mss
import time
import os
import pydirectinput
import ctypes
import json
import requests
import base64
import winsound  # 增加音频反馈

# 1. 强制 DPI 感知
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    ctypes.windll.user32.SetProcessDPIAware()

config_file = 'config_loop.json'
user32 = ctypes.windll.user32
sw, sh = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

# 阿里 API 配置
API_KEY = "sk-e7fd8fabc0a14dfbaf044c0c5b4b142b"
params = {
    "word1_x": 0, "word1_y": 0, "word2_x": 0, "word2_y": 0,
    "word3_x": 0, "word3_y": 0, "accept_x": 0, "accept_y": 0,
    "view_top": 0, "view_left": 0, "view_width": 800, "view_height": 600,
    "ocr_dx": -218, "ocr_dy": -155, "ocr_w": 417, "ocr_h": 70
}

# 全局状态
is_running = False
is_paused = False
execution_status = "等待祭坛..."
ocr_result = ""
last_heartbeat = 0

def load_resources():
    global params, anchor_template
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            params.update(json.load(f))
    if os.path.exists('current_round_anchor.png'):
        anchor_template = cv2.imread('current_round_anchor.png')

def perform_ocr(sct):
    # OCR 区域可视化提示：在读取前画框
    ocr_x, ocr_y = params["word2_x"] + params["ocr_dx"], params["word2_y"] + params["ocr_dy"]
    monitor = {"top": ocr_y, "left": ocr_x, "width": params["ocr_w"], "height": params["ocr_h"]}
    
    img_mss = np.array(sct.grab(monitor))
    _, img_encoded = cv2.imencode('.jpg', cv2.cvtColor(img_mss, cv2.COLOR_BGRA2BGR))
    img_base64 = base64.b64encode(img_encoded).decode('utf-8')

    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    payload = {
        "model": "qwen-vl-ocr",
        "input": {"messages": [{"role": "user", "content": [
            {"image": f"data:image/jpeg;base64,{img_base64}"},
            {"text": "直接给文字内容。"}
        ]}]}
    }
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=5).json()
        return res['output']['choices'][0]['message']['content'][0]['text'].strip().replace(" ", "")
    except:
        return "OCR超时"

def auto_loop_logic(sct):
    global is_running, execution_status, ocr_result
    is_running = True
    winsound.Beep(800, 200)  # 发现祭坛提示音
    
    pts = [(params["word1_x"], params["word1_y"]), 
           (params["word2_x"], params["word2_y"]), 
           (params["word3_x"], params["word3_y"])]
    
    # 动作流程
    for i, pt in enumerate(pts):
        execution_status = f"巡检词缀 {i+1}..."
        pydirectinput.moveTo(pt[0], pt[1], duration=0.2)
        time.sleep(0.5)

    execution_status = "正在识字..."
    ocr_result = perform_ocr(sct)
    print(f"[{time.strftime('%H:%M:%S')}] 识字结果: {ocr_result}")

    execution_status = "选择词缀并点击"
    pydirectinput.click(pts[1][0], pts[1][1])
    time.sleep(0.4)

    execution_status = "点击接受"
    pydirectinput.click(params["accept_x"], params["accept_y"])
    winsound.Beep(1200, 150)  # 完成任务提示音
    
    execution_status = "流程完成，冷却8秒..."
    time.sleep(8)
    is_running = False
    execution_status = "继续扫描锚点..."

def main():
    global is_paused, execution_status, last_heartbeat
    load_resources()
    cv2.namedWindow('Full Loop Executor', cv2.WINDOW_AUTOSIZE)
    
    with mss.mss() as sct:
        while True:
            # 1. 扫描心跳提示
            if time.time() - last_heartbeat > 5:
                print(f"[HEARTBEAT] {time.strftime('%H:%M:%S')} - 脚本监控中...")
                last_heartbeat = time.time()

            monitor = {"top": params["view_top"], "left": params["view_left"], 
                       "width": params["view_width"], "height": params["view_height"]}
            img = cv2.cvtColor(np.array(sct.grab(monitor)), cv2.COLOR_BGRA2BGR)

            # 2. 锚点检测
            found = False
            if anchor_template is not None:
                res = cv2.matchTemplate(img, anchor_template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(res)
                if max_val > 0.8:
                    found = True
                    cv2.rectangle(img, max_loc, (max_loc[0]+30, max_loc[1]+30), (0, 255, 0), 2)
                    cv2.putText(img, "MATCHED!", (max_loc[0], max_loc[1]-10), 1, 1.2, (0, 255, 0), 2)

            # 3. 自动触发流程
            if found and not is_running and not is_paused:
                auto_loop_logic(sct)

            # 4. 视觉状态栏叠加
            color = (0, 0, 255) if is_paused else (255, 255, 0)
            status_txt = f"STATUS: {execution_status} | P: PAUSE"
            cv2.rectangle(img, (0, 0), (params["view_width"], 40), (40, 40, 40), -1)
            cv2.putText(img, status_txt, (10, 30), 1, 1.5, color, 2)
            
            if ocr_result:
                cv2.putText(img, f"OCR: {ocr_result}", (10, sh-200), 1, 1.2, (0, 255, 0), 2)

            cv2.imshow('Full Loop Executor', img)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27: break
            elif key == ord('p'): 
                is_paused = not is_paused
                print(f"[PAUSE] {'脚本已暂停' if is_paused else '脚本已恢复'}")

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()