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

# =================配置与全局变量=================
config_file = 'config_ritual_final.json'
user32 = ctypes.windll.user32
sw, sh = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

# 阿里千问API配置
API_KEY = "sk-e7fd8fabc0a14dfbaf044c0c5b4b142b"

# 使用你刚才框选出的精准偏移量
params = {
    "scan_l": 800, "scan_t": 35, "scan_w": 1600, "scan_h": 800,
    "offset_x": 90, "offset_y": 58, 
    "ocr_dx": -218, "ocr_dy": -155, "ocr_w": 417, "ocr_h": 70 # 高度收缩到标题栏
}

affix_db = {}
priority_settings = {}
anchor_templates = []  # 锚点模板列表
ritual_affix_screen_positions = [] 

def load_resources():
    global affix_db, priority_settings, anchor_templates
    # 加载词缀注册表
    if os.path.exists('词缀注册表.json'):
        with open('词缀注册表.json', 'r', encoding='utf-8') as f:
            affix_db = json.load(f)
        print(f"成功加载词缀注册表，共 {len(affix_db)} 个词缀")
    # 加载优先级设置
    if os.path.exists('优先级设置.json'):
        with open('优先级设置.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
            priority_settings = settings.get("图片配置", {})
        print(f"成功加载优先级设置，共 {len(priority_settings)} 个词缀")
    # 加载锚点模板（支持多个模板）
    anchor_templates = []
    # 加载当前目录下所有以 ritual_anchor 开头的 PNG 文件
    for filename in os.listdir('.'):
        if filename.startswith('ritual_anchor') and filename.endswith('.png'):
            try:
                template = cv2.imread(filename, cv2.IMREAD_COLOR)
                if template is not None:
                    anchor_templates.append(template)
                    print(f"成功加载锚点模板: {filename}")
            except Exception as e:
                print(f"加载锚点模板 {filename} 失败: {e}")
    if not anchor_templates:
        print("警告：未找到锚点模板文件")
    # 加载配置文件
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                params.update(json.load(f))
        except: pass

def save_params():
    with open(config_file, 'w') as f:
        json.dump(params, f)

def ocr_at_mouse():
    """精准识别鼠标上方的词缀标题"""
    mx, my = pydirectinput.position()
    # 使用框选测试出的绝对偏移
    roi = {
        "top": my + params["ocr_dy"], 
        "left": mx + params["ocr_dx"], 
        "width": params["ocr_w"], 
        "height": params["ocr_h"]
    }
    
    with mss.mss() as sct:
        img = np.array(sct.grab(roi))
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        # 保存截图用于调试
        cv2.imwrite('debug_ocr_final.png', img_bgr)
        
        # 将图片转换为base64
        _, img_encoded = cv2.imencode('.jpg', img_bgr)
        img_base64 = base64.b64encode(img_encoded).decode('utf-8')
        
        # 调用阿里千问API
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "qwen-vl-ocr", # 必须是这个模型
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"image": f"data:image/jpeg;base64,{img_base64}"},
                            # 提示词一针见血：要求逐字还原，不准总结
                            {"text": "请精确识别图中的所有中文文字，保持原有的排版和换行，不要输出任何解释，直接给文字内容。"}
                        ]
                    }
                ]
            }
        }

        print("正在请求阿里服务器...")
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            res_data = response.json()
            # 提取文字结果
            text_result = res_data['output']['choices'][0]['message']['content'][0]['text']
            
            # 清理识别结果
            clean_res = text_result.strip().replace(" ", "").replace("\n", "")
            print(f"[OCR] 识别结果: {clean_res}")
            return clean_res
        else:
            print(f"[OCR] 识别失败，错误码: {response.status_code}")
            print(response.text)
            return ""

# 模糊匹配词缀
def match_affix(clean_res):
    """模糊匹配词缀，返回匹配结果、变种属性、优先级和高危词缀状态"""
    if not clean_res:
        return None, None, None, None, None
    
    # 首先尝试匹配词缀注册表
    for key, value in affix_db.items():
        # 清理键名（移除.webp后缀）
        clean_key = key.split('.')[0]
        # 双向包含判断，容错OCR识别错误
        if clean_key in clean_res or clean_res in clean_key:
            variant = value.get('变种', '真')
            # 同时检查优先级设置
            priority_info = None
            high_risk = None
            priority = None
            
            for p_key, p_value in priority_settings.items():
                p_clean_key = p_key.split('.')[0]
                if p_clean_key in clean_res or clean_res in p_clean_key:
                    priority_info = p_key
                    high_risk = p_value.get('高危词缀', '假')
                    priority = p_value.get('优先级', 0)
                    break
            
            return key, variant, priority_info, high_risk, priority
    
    # 如果词缀注册表中没有匹配，尝试直接匹配优先级设置
    for p_key, p_value in priority_settings.items():
        p_clean_key = p_key.split('.')[0]
        if p_clean_key in clean_res or clean_res in p_clean_key:
            priority_info = p_key
            high_risk = p_value.get('高危词缀', '假')
            priority = p_value.get('优先级', 0)
            return None, None, priority_info, high_risk, priority
    
    return None, None, None, None, None

def start_hover_logic():
    print("\n[SYSTEM] 开始自动扫描决策...")
    if not ritual_affix_screen_positions:
        print("[ERR] 未发现锚点，请调整 Scan 范围直到绿框出现")
        return

    # 扫描三个词缀位置
    affix_candidates = []
    for i, (sx, sy) in enumerate(ritual_affix_screen_positions):
        print(f"[SCAN] 正在检查词缀 #{i+1}...")
        pydirectinput.moveTo(sx, sy)
        time.sleep(0.6) # 等待描述窗弹出
        
        name = ocr_at_mouse()
        print(f"[OCR] 识别结果: {name}")
        
        # 匹配词缀
        matched_key, variant, priority_info, high_risk, priority = match_affix(name)
        
        if priority_info:
            print(f"[MATCH] 匹配到: {priority_info} | 高危词缀: {high_risk} | 优先级: {priority}")
            # 只添加安全的词缀（高危词缀为假）
            if high_risk == "假":
                affix_candidates.append({
                    "position": (sx, sy),
                    "priority": priority,
                    "name": priority_info
                })
        elif matched_key:
            print(f"[MATCH] 匹配到词缀注册表: {matched_key} | 变种: {variant}")
            # 只添加安全的词缀（变种为假）
            if variant == "假":
                affix_candidates.append({
                    "position": (sx, sy),
                    "priority": 999, # 默认优先级，确保在没有优先级设置时排在最后
                    "name": matched_key
                })
        else:
            print("[MATCH] 未匹配到词缀")
    
    # 选择最优目标
    selected = False
    if affix_candidates:
        # 按优先级排序，选择优先级最小的
        affix_candidates.sort(key=lambda x: x["priority"])
        best_affix = affix_candidates[0]
        print(f"[ACTION] 选择最优词缀: {best_affix['name']}，优先级: {best_affix['priority']}")
        pydirectinput.moveTo(best_affix['position'][0], best_affix['position'][1])
        time.sleep(0.3)
        pydirectinput.click()
        selected = True
    
    if not selected:
        print("[ACTION] 未发现安全变种，默认点击第一个")
        pydirectinput.click(ritual_affix_screen_positions[0][0], ritual_affix_screen_positions[0][1])
    
    # 启动试炼 (移动到开始按钮位置)
    time.sleep(0.8)
    pydirectinput.moveRel(0, 100) # 根据实际调整
    pydirectinput.click()

def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if 10 <= x <= 150 and 10 <= y <= 50:
            start_hover_logic()

def main():
    load_resources()
    cv2.namedWindow('Ritual Debugger', cv2.WINDOW_NORMAL)
    # 设置默认窗口大小为 1000x800
    cv2.resizeWindow('Ritual Debugger', 1000, 800)
    cv2.setMouseCallback('Ritual Debugger', on_mouse)
    
    # 滑块仅保留必要的 Scan 范围和点位偏移
    cv2.createTrackbar('Scan_L', 'Ritual Debugger', params['scan_l'], sw, lambda v: params.update({"scan_l": v}) or save_params())
    cv2.createTrackbar('Scan_T', 'Ritual Debugger', params['scan_t'], sh, lambda v: params.update({"scan_t": v}) or save_params())
    cv2.createTrackbar('Scan_W', 'Ritual Debugger', params['scan_w'], sw, lambda v: params.update({"scan_w": v}) or save_params())
    cv2.createTrackbar('Scan_H', 'Ritual Debugger', params['scan_h'], sh, lambda v: params.update({"scan_h": v}) or save_params())
    cv2.createTrackbar('Off_X', 'Ritual Debugger', params['offset_x'], 500, lambda v: params.update({"offset_x": v}) or save_params())
    cv2.createTrackbar('Off_Y', 'Ritual Debugger', params['offset_y'], 500, lambda v: params.update({"offset_y": v}) or save_params())

    with mss.mss() as sct:
        while True:
            sl, st, sw_v, sh_v = params['scan_l'], params['scan_t'], params['scan_w'], params['scan_h']
            monitor = {"top": st, "left": sl, "width": max(1, sw_v), "height": max(1, sh_v)}
            img = cv2.cvtColor(np.array(sct.grab(monitor)), cv2.COLOR_BGRA2BGR)
            
            # 多锚点模板循环匹配
            anchor_found = False
            for template in anchor_templates:
                th, tw = template.shape[:2]
                if th < img.shape[0] and tw < img.shape[1]:
                    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, max_loc = cv2.minMaxLoc(res)
                    
                    if max_val > 0.7:
                        # 绘制绿色锚点框
                        cv2.rectangle(img, (max_loc[0], max_loc[1]), (max_loc[0]+tw, max_loc[1]+th), (0, 255, 0), 2)
                        
                        # 同步计算绝对坐标
                        base_x, base_y = max_loc[0] + tw // 2 + sl, max_loc[1] + th // 2 + st
                        ox, oy = params['offset_x'], params['offset_y']
                        
                        global ritual_affix_screen_positions
                        ritual_affix_screen_positions = [(base_x-ox, base_y+oy), (base_x, base_y+oy), (base_x+ox, base_y+oy)]
                        
                        for sx, sy in ritual_affix_screen_positions:
                            cv2.circle(img, (sx-sl, sy-st), 10, (255, 0, 255), -1)
                        
                        anchor_found = True
                        break  # 只要匹配到一个锚点就停止
            
            if not anchor_found:
                # 未找到锚点，清空词缀位置
                ritual_affix_screen_positions = []

            cv2.rectangle(img, (10, 10), (150, 50), (0, 0, 255), -1)
            cv2.putText(img, "START HOVER", (20, 40), 1, 1, (255, 255, 255), 2)
            cv2.imshow('Ritual Debugger', img)
            if cv2.waitKey(1) == 27: break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()