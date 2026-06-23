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

# 1. 强制 DPI 感知 (确保全屏坐标点击精准)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    ctypes.windll.user32.SetProcessDPIAware()

config_file = 'config_loop.json'
API_KEY = "sk-e7fd8fabc0a14dfbaf044c0c5b4b142b"

# 基础参数 (坐标依然从 JSON 读取)
params = {
    "word2_x": 0, "word2_y": 0, "accept_x": 0, "accept_y": 0,
    "ocr_dx": -218, "ocr_dy": -155, "ocr_w": 417, "ocr_h": 70
}

is_running = False
is_paused = False
anchor_templates = [] 

def load_resources():
    global params, anchor_templates
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            params.update(json.load(f))
            print(f"[SYSTEM] 已载入 JSON 配置，当前 Word2 坐标: ({params['word2_x']}, {params['word2_y']})")

    # 多锚点模糊加载逻辑并输出日志
    anchor_templates = []
    print("\n[LOG] === 正在扫描并加载锚点图片 ===")
    for filename in os.listdir('.'):
        if filename.startswith('ritual_anchor') and filename.endswith('.png'):
            img = cv2.imread(filename)
            if img is not None:
                anchor_templates.append((img, filename))
                # 按照你的要求：日志输出已经加载了哪些锚点图片
                print(f"[LOG] 已成功加载锚点文件: {filename}")
    
    if not anchor_templates:
        print("[LOG] 警告：未发现任何 ritual_anchor 开头的图片！")
    print(f"[LOG] === 加载完成，共计 {len(anchor_templates)} 个文件 ===\n")

def perform_ritual_action(sct, anchor_name):
    # 根据文件名分流动作
    if 'rune' in anchor_name:
        print(f"[ACTION] 识别为符文关卡，直接点击 Word2 坐标: ({params['word2_x']}, {params['word2_y']})")
        pydirectinput.click(params["word2_x"], params["word2_y"])
        return

    # 菜单关卡执行 OCR
    print(f"[ACTION] 识别为菜单关卡，正在移动鼠标并调用阿里云...")
    pydirectinput.moveTo(params["word2_x"], params["word2_y"], duration=0.2)
    time.sleep(0.6)

    ocr_x, ocr_y = params["word2_x"] + params["ocr_dx"], params["word2_y"] + params["ocr_dy"]
    monitor = {"top": ocr_y, "left": ocr_x, "width": params["ocr_w"], "height": params["ocr_h"]}
    
    try:
        img_mss = np.array(sct.grab(monitor))
        img_bgr = cv2.cvtColor(img_mss, cv2.COLOR_BGRA2BGR)
        _, img_encoded = cv2.imencode('.jpg', img_bgr)
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
        res = requests.post(url, headers=headers, json=payload, timeout=8).json()
        
        text = res['output']['choices'][0]['message']['content'][0]['text'].strip()
        print(f"[OCR] 识别结果: {text}")
        
        # 执行点击
        pydirectinput.click(params["word2_x"], params["word2_y"])
        time.sleep(0.5)
        pydirectinput.click(params["accept_x"], params["accept_y"])
    except Exception as e:
        print(f"[ERROR] 流程异常: {e}")

def main():
    global is_paused, is_running
    load_resources()
    cv2.namedWindow('Test Loop Logic (Full Screen)', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Test Loop Logic (Full Screen)', 960, 540)
    
    last_log_time = 0
    
    with mss.mss() as sct:
        while True:
            # 视野范围：改为全屏扫描，和功能二一致
            monitor = sct.monitors[1] 
            img = cv2.cvtColor(np.array(sct.grab(monitor)), cv2.COLOR_BGRA2BGR)

            best_match = {"val": 0, "name": "", "loc": (0,0), "w": 0, "h": 0}
            
            # 遍历所有加载的锚点图片进行匹配
            for template, name in anchor_templates:
                res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(res)
                if max_val > best_match["val"]:
                    h, w = template.shape[:2]
                    best_match = {"val": max_val, "name": name, "loc": max_loc, "w": w, "h": h}

            # 匹配日志节流输出
            if time.time() - last_log_time > 3:
                print(f"[SCAN] 匹配中... 最佳图片: {best_match['name']} | 匹配度: {best_match['val']:.2f}")
                last_log_time = time.time()

            # 触发判断
            if best_match["val"] > 0.8 and not is_running and not is_paused:
                # 绿色边框高亮锚点
                x, y = best_match["loc"]
                cv2.rectangle(img, (x, y), (x + best_match["w"], y + best_match["h"]), (0, 255, 0), 3)
                
                is_running = True
                perform_ritual_action(sct, best_match["name"])
                print("[WAIT] 执行完成，冷却 8 秒...")
                time.sleep(8)
                is_running = False

            # UI 显示
            cv2.putText(img, f"Best: {best_match['name']} ({best_match['val']:.2f})", (50, 50), 1, 1.5, (0, 255, 255), 2)
            if is_paused: cv2.putText(img, "PAUSED (P)", (50, 100), 1, 2, (0, 0, 255), 3)
            
            cv2.imshow('Test Loop Logic (Full Screen)', img)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27: break
            elif key == ord('p'): 
                is_paused = not is_paused
                print(f"[SYSTEM] 暂停: {is_paused}")

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()