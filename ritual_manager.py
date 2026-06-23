import cv2
import numpy as np
import time
import pydirectinput
import requests
import base64
import ctypes

# 1. 强制 DPI 感知 - 解决高分屏偏移
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

def get_screen_resolution():
    """动态获取屏幕分辨率"""
    try:
        user32 = ctypes.windll.user32
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        return width, height
    except:
        return 2560, 1600

def non_blocking_sleep(seconds):
    """非阻塞等待，确保窗口事件能够及时处理"""
    start_time = time.time()
    while time.time() - start_time < seconds:
        cv2.waitKey(1)

# 全局变量
affix_db = {}
priority_settings = {}
RITUAL_CFG = {}
anchor_templates = []
anchor_filenames = []
API_KEY = ""

def set_ritual_resources(db, settings, cfg, templates, api_key, filenames=None):
    """设置仪式管理器所需的资源"""
    global affix_db, priority_settings, RITUAL_CFG, anchor_templates, anchor_filenames, API_KEY
    affix_db = db
    priority_settings = settings
    RITUAL_CFG = cfg
    anchor_templates = templates
    if filenames:
        anchor_filenames = filenames
    API_KEY = api_key
    print(f"[RITUAL MANAGER] 资源注入完成，模板数量: {len(templates)}")

def safe_screenshot(sct, monitor, screen_width, screen_height):
    """2. 稳健的截图保护 - 终结截图区域异常"""
    # 强制对 monitor 字典进行边界裁剪
    monitor['left'] = max(0, min(int(monitor['left']), screen_width - monitor['width']))
    monitor['top'] = max(0, min(int(monitor['top']), screen_height - monitor['height']))
    
    try:
        img = np.array(sct.grab(monitor))
        return img
    except Exception as e:
        print(f"[DEBUG] 截图区域异常! monitor: {monitor}, 屏幕尺寸: {screen_width}x{screen_height}")
        raise

def perform_ocr(sct, tx, ty, screen_width, screen_height):
    """执行 OCR 识别"""
    monitor = {"top": int(ty - 40), "left": int(tx - 200), "width": 400, "height": 80}
    img = safe_screenshot(sct, monitor, screen_width, screen_height)
    _, enc = cv2.imencode('.jpg', cv2.cvtColor(img, cv2.COLOR_BGRA2BGR))
    img_base64 = base64.b64encode(enc).decode('utf-8')
    
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    payload = {
        "model": "qwen-vl-ocr",
        "input": {
            "messages": [{
                "role": "user",
                "content": [
                    {"image": f"data:image/jpeg;base64,{img_base64}"},
                    {"text": "直接给文字内容。"}
                ]
            }]
        }
    }
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5).json()
        if 'output' not in response:
            print(f"[DEBUG] 截图区域异常! monitor: {monitor}, 屏幕尺寸: {screen_width}x{screen_height}")
            return "OCR Error: No output"
        return response['output']['choices'][0]['message']['content'][0]['text']
    except Exception as e:
        print(f"[OCR] 错误: {e}, monitor: {monitor}, 屏幕尺寸: {screen_width}x{screen_height}")
        return "OCR Error"

def process_affix_decision(results):
    """处理词缀优先级决策"""
    valid_affixes = []
    for r in results:
        text = r["text"]
        is_safe = True
        priority = 0
        matched = False
        
        if priority_settings and isinstance(priority_settings, dict):
            for key, settings in priority_settings.items():
                clean_key = key.replace('.webp', '').replace('.png', '')
                if clean_key in text or text in clean_key:
                    if settings.get("高危词缀", "") == "真":
                        is_safe = False
                        print(f"[DECISION] 词缀 '{text}' 是高危词缀，跳过")
                        break
                    priority = int(settings.get("优先级", 0))
                    matched = True
                    break
        
        if is_safe:
            valid_affixes.append({"pos": r["pos"], "text": text, "priority": priority, "matched": matched})
            if matched:
                print(f"[DECISION] 词缀 '{text}' 安全，优先级: {priority}")
    
    target = None
    matched_affixes = [affix for affix in valid_affixes if affix["matched"]]
    if matched_affixes:
        matched_affixes.sort(key=lambda x: x["priority"], reverse=True)
        target = matched_affixes[0]
        print(f"[DECISION] 选择优先级最高的词缀: {target['text']} (优先级: {target['priority']})")
    else:
        if len(valid_affixes) > 1:
            target = valid_affixes[1]
            print(f"[DECISION] 没有匹配到词缀，选择中间词缀: {target['text']}")
        else:
            print("[DECISION] 没有找到安全的词缀")
    
    return target

def process_ritual(sct):
    """处理仪式祭坛逻辑"""
    screen_width, screen_height = get_screen_resolution()
    print(f"[RITUAL] 屏幕分辨率: {screen_width}x{screen_height}")
    
    best_loc = (0, 0)
    matched_filename = ""
    no_anchor_time = 0
    max_val = 0
    
    if anchor_templates:
        full_screen = np.array(sct.grab(sct.monitors[1]))
        img_bgr = cv2.cvtColor(full_screen, cv2.COLOR_BGRA2BGR)
        
        # 2. 改进锚点识别逻辑 - 前缀锁定
        # 遍历所有模板进行匹配
        for i, template in enumerate(anchor_templates):
            filename = anchor_filenames[i] if i < len(anchor_filenames) else f"template_{i}.png"
            h, w = template.shape[:2]
            
            if h > img_bgr.shape[0] or w > img_bgr.shape[1]:
                continue
            
            res = cv2.matchTemplate(img_bgr, template, cv2.TM_CCOEFF_NORMED)
            _, val, _, loc = cv2.minMaxLoc(res)
            max_val = max(max_val, val)
            
            print(f"[RITUAL] {filename} 匹配度: {val:.3f}")
            if val > 0.8:
                best_val = val
                best_loc = loc
                matched_filename = filename
                print(f"[RITUAL] 发现 {filename} 锚点，匹配度: {best_val:.3f}")
                print(f"[RITUAL] 锚点左上角坐标 (x0, y0): {best_loc}")
                break
        
        if not matched_filename:
            print(f"[RITUAL] 未发现锚点，最高匹配度: {max_val:.3f}")
            no_anchor_time += 1
            if no_anchor_time >= 100:
                print("[RITUAL] 连续100秒未识别到锚点，判定为祭坛已打完，切换回探路模式")
                return "MAP_MODE", 0
            return "RITUAL_ACTIVE", no_anchor_time
    else:
        print("[RITUAL MANAGER] 模板列表为空，无法进行识别")
        return "MAP_MODE", 0
    
    # 前缀判定
    is_first_round = False
    if matched_filename.lower().startswith("ritual") or matched_filename.lower().startswith("start"):
        is_first_round = True
        print(f"[ASSOCIATION] 匹配图片: {matched_filename} | 命中前缀匹配 | 强制关联 V1 坐标")
    else:
        print(f"[ASSOCIATION] 匹配图片: {matched_filename} | 关联版本: V2")
    
    no_anchor_time = 0
    
    if is_first_round:
        # 第一轮判定
        print("[RITUAL] 执行第一轮判定流程...")
        
        if "ritual_points_v1" not in RITUAL_CFG or len(RITUAL_CFG["ritual_points_v1"]) < 3:
            print("[ERROR] 配置不完整，缺少 ritual_points_v1")
            return "MAP_MODE", 0
        
        results = []
        for i, offset in enumerate(RITUAL_CFG["ritual_points_v1"]):
            tx, ty = best_loc[0] + offset[0], best_loc[1] + offset[1]
            print(f"[ASSOCIATION] 匹配图片: {matched_filename} | 命中前缀匹配 | 强制关联 V1 坐标 | 点击目标: ({tx}, {ty})")
            print(f"[SCAN] 正在检查词缀 #{i+1}，坐标: ({tx}, {ty})")
            
            pydirectinput.moveTo(int(tx), int(ty), duration=0.1)
            non_blocking_sleep(0.3)
            
            text = perform_ocr(sct, tx, ty, screen_width, screen_height)
            print(f"[OCR] 识别结果: {text}")
            results.append({"pos": (tx, ty), "text": text})
        
        target = process_affix_decision(results)
        
        if target:
            print(f"[ACTION] 点击词缀: {target['text']}")
            pydirectinput.click(int(target["pos"][0]), int(target["pos"][1]))
            non_blocking_sleep(0.5)
        
        # 点击开始按钮
        print("[RITUAL] 执行启动操作...")
        if RITUAL_CFG.get("start_button_offset_v1"):
            sx, sy = best_loc[0] + RITUAL_CFG["start_button_offset_v1"][0], best_loc[1] + RITUAL_CFG["start_button_offset_v1"][1]
        else:
            h, w = anchor_templates[0].shape[:2]
            sx, sy = best_loc[0] + w//2, best_loc[1] + h//2
        print(f"[ACTION] 点击开始试炼按钮，坐标: ({sx}, {sy})")
        pydirectinput.click(int(sx), int(sy))
        
        print("[RITUAL] 等待UI界面消失...")
        non_blocking_sleep(2)
        
        print("[RITUAL] 第一轮流程完成，切换回探路模式")
        # 4. 解决往返跑与无限循环
        print("[RITUAL] 状态锁定，等待4秒...")
        time.sleep(4)
        return "MAP_MODE", 0
    
    else:
        # 次轮判定
        print("[RITUAL] 执行次轮判定流程...")
        
        if "ritual_points_v2" not in RITUAL_CFG or len(RITUAL_CFG["ritual_points_v2"]) < 3:
            print("[ERROR] 配置不完整，缺少 ritual_points_v2")
            return "RITUAL_ACTIVE", 0
        
        print(f"[RITUAL] 检测到的锚点位置: {best_loc}")
        print(f"[RITUAL] 保存的词缀偏移量: {RITUAL_CFG['ritual_points_v2']}")
        
        results = []
        for i, offset in enumerate(RITUAL_CFG["ritual_points_v2"]):
            if RITUAL_CFG.get('ritual_points_v2_type') == 'absolute_screen_coordinates':
                tx, ty = offset[0], offset[1]
                print(f"[ASSOCIATION] 匹配图片: {matched_filename} | 关联版本: V2 | 点击目标: ({tx}, {ty})")
                print(f"[SAFETY CHECK] 即将检查词缀 #{i+1}，绝对坐标: ({tx}, {ty})")
            else:
                tx, ty = best_loc[0] + offset[0], best_loc[1] + offset[1]
                print(f"[ASSOCIATION] 匹配图片: {matched_filename} | 关联版本: V2 | 点击目标: ({tx}, {ty})")
                print(f"[SAFETY CHECK] 即将检查词缀 #{i+1}，相对坐标: ({tx}, {ty})")
            
            pydirectinput.moveTo(int(tx), int(ty), duration=0.1)
            non_blocking_sleep(0.3)
            
            text = perform_ocr(sct, tx, ty, screen_width, screen_height)
            print(f"[OCR] 识别结果: {text}")
            results.append({"pos": (tx, ty), "text": text})
        
        target = process_affix_decision(results)
        
        if target:
            print(f"[ACTION] 点击词缀: {target['text']}")
            pydirectinput.click(int(target["pos"][0]), int(target["pos"][1]))
            non_blocking_sleep(0.5)
            
            print("[RITUAL] 执行开始操作...")
            if RITUAL_CFG.get('ritual_points_v2_type') == 'absolute_screen_coordinates':
                if RITUAL_CFG.get('start_button_offset_v2'):
                    sx, sy = RITUAL_CFG['start_button_offset_v2'][0], RITUAL_CFG['start_button_offset_v2'][1]
                else:
                    sx, sy = best_loc[0], best_loc[1]
            else:
                if RITUAL_CFG.get("start_button_offset_v2"):
                    sx, sy = best_loc[0] + RITUAL_CFG["start_button_offset_v2"][0], best_loc[1] + RITUAL_CFG["start_button_offset_v2"][1]
                else:
                    if len(anchor_templates) > 1:
                        h, w = anchor_templates[1].shape[:2]
                        sx, sy = best_loc[0] + w//2, best_loc[1] + h//2
                    else:
                        sx, sy = best_loc[0], best_loc[1]
            
            print(f"[SAFETY CHECK] 即将点击开始按钮，坐标: ({sx}, {sy})")
            print(f"[ACTION] 点击开始试炼按钮，坐标: ({sx}, {sy})")
            pydirectinput.click(int(sx), int(sy))
            
            print("[RITUAL] 等待UI界面消失...")
            non_blocking_sleep(2)
            
            print("[RITUAL] 等待战斗开始...")
            non_blocking_sleep(5)
            print("[RITUAL] 等待完成，继续检测下一轮")
        
        print("[RITUAL] 次轮流程完成，保持在RITUAL_ACTIVE状态")
        return "RITUAL_ACTIVE", no_anchor_time
