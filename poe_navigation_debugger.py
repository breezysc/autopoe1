import cv2
import numpy as np
import mss
import time
import json
import os
import pydirectinput
from pynput import keyboard
import threading
import ctypes

# =================配置与全局变量=================
config_file = 'config.json'

# 初始默认值
map_x_from_right = 6
map_y_from_top = 40
map_size = 380
threshold = 100
scan_radius = 44
sensitivity = 0.5
auto_move_enabled = False
click_distance = 250
click_delay = 200
wall_thickness = 3
wall_follow_mode = 1
safe_padding = 15
inertia_weight = 150

# 运行时状态
last_best_index = 0
last_click_time = 0
inertia_mode = False
inertia_start_time = 0
last_inertia_update_time = 0
inertia_update_interval = 0.5
show_message = False
message_text = ""
message_time = 0
frame_counter = 0

# 试炼祭坛检测相关
ritual_template = None
ritual_match_threshold = 0.7
ritual_detected = False
ritual_position = None
ritual_angle = 0
ritual_distance = 0

# 第二个目标检测相关
target2_template = None
target2_match_threshold = 0.7
target2_detected = False
target2_position = None
target2_angle = 0
target2_distance = 0

# 窗口位置
user32 = ctypes.windll.user32
sw, sh = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
win_x, win_y, win_w, win_h = 50, sh - 350, 600, 300

def load_config():
    global map_x_from_right, map_y_from_top, map_size, threshold, scan_radius, sensitivity, \
           click_distance, click_delay, wall_thickness, wall_follow_mode, win_x, win_y, win_w, win_h, \
           safe_padding, inertia_weight
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                c = json.load(f)
                map_x_from_right = c.get('map_x_from_right', map_x_from_right)
                map_y_from_top = c.get('map_y_from_top', map_y_from_top)
                map_size = c.get('map_size', map_size)
                threshold = c.get('threshold', threshold)
                scan_radius = c.get('scan_radius', scan_radius)
                sensitivity = c.get('sensitivity', sensitivity)
                click_distance = c.get('click_distance', click_distance)
                click_delay = c.get('click_delay', click_delay)
                wall_thickness = c.get('wall_thickness', wall_thickness)
                wall_follow_mode = c.get('wall_follow_mode', wall_follow_mode)
                win_x, win_y = c.get('win_x', win_x), c.get('win_y', win_y)
                win_w, win_h = c.get('win_w', win_w), c.get('win_h', win_h)
                safe_padding = c.get('safe_padding', safe_padding)
                inertia_weight = c.get('inertia_weight', inertia_weight)
        except: pass

def save_config():
    config = {
        'map_x_from_right': map_x_from_right, 'map_y_from_top': map_y_from_top,
        'map_size': map_size, 'threshold': threshold, 'scan_radius': scan_radius,
        'sensitivity': sensitivity, 'click_distance': click_distance, 'click_delay': click_delay,
        'wall_thickness': wall_thickness, 'wall_follow_mode': wall_follow_mode,
        'win_x': win_x, 'win_y': win_y, 'win_w': win_w, 'win_h': win_h,
        'safe_padding': safe_padding, 'inertia_weight': inertia_weight
    }
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def load_altar_templates():
    global ritual_template, target2_template
    # 加载试炼祭坛模板
    ritual_path = 'ritual_icon.png'
    if os.path.exists(ritual_path):
        try:
            ritual_template = cv2.imread(ritual_path, cv2.IMREAD_COLOR)
            if ritual_template is not None:
                print(f"[RITUAL] 加载模板: {ritual_path}")
            else:
                print("[RITUAL] 无法加载试炼祭坛模板")
        except:
            print("[RITUAL] 加载试炼祭坛模板时出错")
    else:
        print("[RITUAL] 未找到试炼祭坛模板，请确保 ritual_icon.png 存在")
    
    # 加载第二个目标模板
    target2_path = 'target_icon_2.png'
    if os.path.exists(target2_path):
        try:
            target2_template = cv2.imread(target2_path, cv2.IMREAD_COLOR)
            if target2_template is not None:
                print(f"[TARGET2] 加载模板: {target2_path}")
            else:
                print("[TARGET2] 无法加载第二个目标模板")
        except:
            print("[TARGET2] 加载第二个目标模板时出错")
    else:
        print("[TARGET2] 未找到第二个目标模板，请确保 target_icon_2.png 存在")

# =================控制模块=================
def on_press(key):
    global auto_move_enabled, show_message, message_text, message_time
    try:
        if key == keyboard.Key.f1:
            auto_move_enabled = not auto_move_enabled
            message_text = f"AUTO: {'ON' if auto_move_enabled else 'OFF'}"
            show_message, message_time = True, time.time()
        elif key == keyboard.Key.f2:
            auto_move_enabled = False
            message_text = "EMERGENCY STOP"
            show_message, message_time = True, time.time()
    except: pass

def click_at_angle(angle):
    if not auto_move_enabled: return
    # 核心修正：这里直接使用 angle。所有的 -90 偏移已在 main 逻辑中处理
    rad = np.deg2rad(angle - 90)
    screen_w, screen_h = pydirectinput.size()
    cx, cy = screen_w // 2, screen_h // 2
    
    tx = int(cx + click_distance * np.cos(rad))
    ty = int(cy + click_distance * np.sin(rad))
    
    try:
        pydirectinput.mouseDown(tx, ty)
        time.sleep(0.05)
        pydirectinput.mouseUp(tx, ty)
    except: pass

def detect_ritual(img, cx, cy):
    global ritual_detected, ritual_position, ritual_angle, ritual_distance
    ritual_detected = False
    ritual_position = None
    ritual_angle = 0
    ritual_distance = 0
    
    if ritual_template is None:
        return
    
    h, w = ritual_template.shape[:2]
    if h > img.shape[0] or w > img.shape[1]:
        return
    
    result = cv2.matchTemplate(img, ritual_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val > ritual_match_threshold:
        center_x = max_loc[0] + w // 2
        # 向上偏移25像素，适应角色立体高度
        center_y = max_loc[1] + h // 2 - 25
        
        # 计算距离和角度
        distance = np.sqrt((center_x - cx)**2 + (center_y - cy)**2)
        angle = np.degrees(np.arctan2(center_y - cy, center_x - cx)) + 90
        if angle < 0: angle += 360
        
        ritual_detected = True
        ritual_position = (center_x, center_y)
        ritual_angle = angle
        ritual_distance = distance
        print(f"[RITUAL] 发现试炼祭坛，距离: {distance:.1f}, 角度: {angle:.1f}")

def detect_target2(img, cx, cy):
    global target2_detected, target2_position, target2_angle, target2_distance
    target2_detected = False
    target2_position = None
    target2_angle = 0
    target2_distance = 0
    
    if target2_template is None:
        return
    
    h, w = target2_template.shape[:2]
    if h > img.shape[0] or w > img.shape[1]:
        return
    
    result = cv2.matchTemplate(img, target2_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val > target2_match_threshold:
        center_x = max_loc[0] + w // 2
        # 向上偏移25像素，适应角色立体高度
        center_y = max_loc[1] + h // 2 - 45
        
        # 计算距离和角度
        distance = np.sqrt((center_x - cx)**2 + (center_y - cy)**2)
        angle = np.degrees(np.arctan2(center_y - cy, center_x - cx)) + 90
        if angle < 0: angle += 360
        
        target2_detected = True
        target2_position = (center_x, center_y)
        target2_angle = angle
        target2_distance = distance
        print(f"[TARGET2] 发现第二个目标，距离: {distance:.1f}, 角度: {angle:.1f}")

# =================GUI 回调=================
def update_val(val_name, val):
    globals()[val_name] = val
    save_config()

# =================主程序=================
def main():
    global last_best_index, last_click_time, inertia_mode, inertia_start_time, frame_counter, last_inertia_update_time, show_message, message_text, message_time, click_distance

    load_config()
    load_altar_templates()
    
    # 创建 GUI 窗口
    cv2.namedWindow('PoE Live Navigation Debugger', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('PoE Live Navigation Debugger', cv2.WND_PROP_TOPMOST, 1)
    
    # 窗口初始化与定位
    hwnd = ctypes.windll.user32.FindWindowW(None, 'PoE Live Navigation Debugger')
    if hwnd: ctypes.windll.user32.MoveWindow(hwnd, win_x, win_y, win_w, win_h, True)

    # 创建滑动条
    cv2.createTrackbar('Threshold', 'PoE Live Navigation Debugger', threshold, 255, lambda v: update_val('threshold', v))
    cv2.createTrackbar('Scan_R', 'PoE Live Navigation Debugger', scan_radius, 200, lambda v: update_val('scan_radius', v))
    cv2.createTrackbar('Sens', 'PoE Live Navigation Debugger', int(sensitivity*100), 100, lambda v: update_val('sensitivity', v/100.0))
    cv2.createTrackbar('Inertia_W', 'PoE Live Navigation Debugger', inertia_weight, 200, lambda v: update_val('inertia_weight', v))
    cv2.createTrackbar('Wall_T', 'PoE Live Navigation Debugger', wall_thickness, 10, lambda v: update_val('wall_thickness', v))
    cv2.createTrackbar('Safe_P', 'PoE Live Navigation Debugger', safe_padding, 50, lambda v: update_val('safe_padding', v))

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    with mss.mss() as sct:
        while True:
            frame_counter += 1
            if cv2.waitKey(1) == 27: break
            
            monitor = sct.monitors[1]
            mx = monitor['width'] - map_x_from_right - map_size
            screenshot = sct.grab({'top': map_y_from_top, 'left': mx, 'width': map_size, 'height': map_size})
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)
            
            # 目标检测
            cx, cy = map_size // 2, map_size // 2
            detect_ritual(img, cx, cy)
            detect_target2(img, cx, cy)
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
            if wall_thickness > 0:
                binary = cv2.dilate(binary, np.ones((3,3), np.uint8), iterations=wall_thickness)

            scores = []
            valid_dirs = []
            full_path_count = 0

            # 1. 扫描与碰撞检测
            for i in range(12):
                angle = i * 30
                rad = np.deg2rad(angle - 90) # 统一坐标系：0度为北
                
                # 射线避障
                collision = False
                for r in [0.3, 0.6, 0.9]:
                    dist = int(scan_radius * r)
                    px, py = int(cx + dist * np.cos(rad)), int(cy + dist * np.sin(rad))
                    if 0 <= px < map_size and 0 <= py < map_size and binary[py, px] == 255:
                        collision = True; break
                
                # 扇形评分
                mask = np.zeros((map_size, map_size), np.uint8)
                cv2.ellipse(mask, (cx, cy), (scan_radius, scan_radius), 0, angle-90-15, angle-90+15, 255, -1)
                score = np.sum(cv2.bitwise_and(binary, binary, mask=mask) == 0) / np.sum(mask == 255)
                
                if collision: score = 0
                scores.append(score)
                valid_dirs.append(score > sensitivity)
                if score > 0.95: full_path_count += 1

            # 2. 惯性逻辑加权
            if valid_dirs[last_best_index]:
                scores[last_best_index] *= (inertia_weight / 100.0)

            # 3. 决策系统 (优先级：排斥 > 惯性 > 贴墙)
            curr_time = time.time()
            wall_nearby = False
            safe_r = int(scan_radius * 0.25)
            # 简易近身墙检测
            for i in range(12):
                r_safe = np.deg2rad(i*30-90)
                px, py = int(cx + safe_r*np.cos(r_safe)), int(cy + safe_r*np.sin(r_safe))
                if 0 <= px < map_size and 0 <= py < map_size and binary[py, px] == 255:
                    wall_nearby = True; break

            # 惯性模式判断
            if full_path_count >= 11:
                if not inertia_mode: inertia_mode, inertia_start_time = True, curr_time
            else:
                if inertia_mode and (curr_time - inertia_start_time > 1.5): inertia_mode = False

            # 确定当前追踪的目标
            target_detected = ritual_detected or target2_detected
            current_distance = ritual_distance if ritual_detected else (target2_distance if target2_detected else 9999)
            
            # 最终索引选定
            if ritual_detected:
                # 试炼祭坛检测优先级最高 - 直接使用原始角度
                best_angle = ritual_angle
                print("[RITUAL] 发现试炼祭坛，执行追踪模式")
                # 标记为目标模式，不使用索引
                max_idx = -1
            elif target2_detected:
                # 第二个目标检测优先级次之 - 直接使用原始角度
                best_angle = target2_angle
                print("[TARGET2] 发现第二个目标，执行追踪模式")
                # 标记为目标模式，不使用索引
                max_idx = -1
            elif wall_nearby:
                max_idx = (last_best_index - 1) % 12 # 紧急左转避障
                best_angle = max_idx * 30
            elif inertia_mode and (curr_time - last_inertia_update_time < inertia_update_interval):
                max_idx = last_best_index # 锁定惯性
                best_angle = max_idx * 30
            else:
                if wall_follow_mode == 1:
                    # 贴右墙逻辑
                    max_idx = last_best_index
                    for offset in [1, 0, -1, -2, -3]: # 优先看右，再看前，再看左
                        idx = (last_best_index + offset) % 12
                        if valid_dirs[idx]:
                            max_idx = idx; break
                else:
                    max_idx = scores.index(max(scores))
                best_angle = max_idx * 30
                last_inertia_update_time = curr_time

            last_best_index = max_idx

            # 4. 执行与可视化 - 像素级精准刹车
            original_click_distance = click_distance
            should_click = True
            
            # 像素级精准刹车机制 - 极点刹车
            if target_detected:
                if current_distance < 4:
                    # 第二步（锁死）：当距离小于4像素时，停止所有点击并强制松手
                    print(f"[BRAKE] 距离目标 {current_distance:.1f} 像素，强力停止")
                    should_click = False
                    # 强制松手，确保没有残留的长按指令
                    pydirectinput.mouseUp()
                elif current_distance < 30:
                    # 第一步（减速）：动态自适应点击距离
                    click_distance = max(10, current_distance)
                    print(f"[BRAKE] 距离目标 {current_distance:.1f} 像素，动态减速模式，点击距离: {click_distance}")
                elif current_distance < 50:
                    # 中等距离，适当缩短距离
                    click_distance = 100
            
            # 判断是否强制覆盖避障（最后冲刺阶段）
            force_click = target_detected and current_distance < 50
            
            # 执行点击 - 提高目标检测时的决策频率
            if should_click:
                # 目标模式时，将点击延迟缩减为50%
                target_click_delay = click_delay * 0.5 if target_detected else click_delay
                
                if force_click:
                    # 最后冲刺阶段，强制点击，无视避障评分
                    if (curr_time*1000 - last_click_time) > target_click_delay:
                        click_at_angle(best_angle)
                        last_click_time = curr_time*1000
                else:
                    # 正常模式，检查方向有效性
                    if max_idx >= 0 and scores[max_idx] > sensitivity:
                        if (curr_time*1000 - last_click_time) > target_click_delay:
                            click_at_angle(best_angle)
                            last_click_time = curr_time*1000
                    elif max_idx < 0:  # 目标模式，直接点击
                        if (curr_time*1000 - last_click_time) > target_click_delay:
                            click_at_angle(best_angle)
                            last_click_time = curr_time*1000
            
            # 恢复原始点击距离
            click_distance = original_click_distance

            # 绘制
            res_img = img.copy()
            
            # 绘制试炼祭坛检测结果（黄色方框）
            if ritual_detected and ritual_position:
                x, y = ritual_position
                cv2.rectangle(res_img, (x-10, y-10), (x+10, y+10), (0, 255, 255), 2)
                cv2.putText(res_img, "TARGET: RITUAL ALTAR", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(res_img, f"DIST: {ritual_distance:.1f}px", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # 绘制第二个目标检测结果（蓝色方框）
            if target2_detected and target2_position:
                x, y = target2_position
                cv2.rectangle(res_img, (x-10, y-10), (x+10, y+10), (255, 0, 0), 2)
                # 如果同时检测到两个目标，显示优先级信息
                if ritual_detected:
                    cv2.putText(res_img, "TARGET: TARGET2 (LOW PRIORITY)", (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                    cv2.putText(res_img, f"DIST: {target2_distance:.1f}px", (20, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                else:
                    cv2.putText(res_img, "TARGET: TARGET2", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                    cv2.putText(res_img, f"DIST: {target2_distance:.1f}px", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            for i in range(12):
                r_draw = np.deg2rad(i*30-90)
                px, py = int(cx + scan_radius*np.cos(r_draw)), int(cy + scan_radius*np.sin(r_draw))
                cv2.circle(res_img, (px, py), 3, (0, 255, 0) if valid_dirs[i] else (0, 0, 255), -1)
            
            target_rad = np.deg2rad(best_angle - 90)
            tx, ty = int(cx + scan_radius*np.cos(target_rad)), int(cy + scan_radius*np.sin(target_rad))
            cv2.arrowedLine(res_img, (cx, cy), (tx, ty), (255, 255, 0), 2)
            
            if show_message and (time.time() - message_time < 1.5):
                cv2.putText(res_img, message_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            cv2.imshow('PoE Live Navigation Debugger', np.hstack([res_img, cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)]))

    listener.stop()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    print("[SYSTEM] 启动程序...")
    print("[SYSTEM] 请在5秒内切换到游戏界面...")
    import time
    for i in range(5, 0, -1):
        print(f"[SYSTEM] {i}...")
        time.sleep(1)
    try:
        main()
    except Exception as e:
        print(f"[ERROR] 程序异常: {e}")
        import traceback
        traceback.print_exc()