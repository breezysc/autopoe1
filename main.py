import cv2
import numpy as np
import time
import pydirectinput
import mss
import os
import json
import ctypes

# 导入各个模块
from config_manager import config_manager
import ritual_manager
import npc_handler
import vision_engine
from hideout_manager import hideout_manager

# 全局状态变量
STATE = "MAP_MODE"  # MAP_MODE, HIDEOUT_MODE, NPC_INTERACTING, RITUAL_ACTIVE
PAUSED = False
last_click_time = 0
ritual_detected = False
target2_detected = False

# 强制 DPI 感知设置
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception as e:
    print(f"[WARN] DPI awareness setup failed: {e}")

def main():
    global STATE, PAUSED, last_click_time, ritual_detected, target2_detected
    
    print("[SYSTEM] 初始化 PoE 自动化系统...")
    
    # 1. 加载配置
    config_manager.load_all()
    
    # 2. 初始化屏幕捕获
    sct = mss.mss()
    
    print("[SYSTEM] 系统初始化完成，进入主循环...")
    print("[SYSTEM] 按 'P' 键暂停/继续，按 'ESC' 键退出。")
    
    while True:
        current_time = time.time()
        
        # 键盘检测
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            print("[SYSTEM] 退出程序。")
            break
        elif key == ord('p') or key == ord('P'):
            PAUSED = not PAUSED
            print(f"[SYSTEM] 暂停状态: {PAUSED}")
            
        if PAUSED:
            time.sleep(0.1)
            continue
            
        # 场景检测
        scene = vision_engine.detect_scene(config_manager.hideout_template)
        
        # === 状态机逻辑 ===
        
        # 1. NPC 交互模式 (最高优先级)
        if STATE == "NPC_INTERACTING":
            print("[STATE] 当前状态: NPC_INTERACTING")
            # 执行 NPC 交互
            npc_handler_instance = npc_handler.NPC_Handler(
                config_manager.NPC_CFG,
                config_manager.API_KEY,
                config_manager.npc_template,
                config_manager.tet_template,
                config_manager.target2_template
            )
            success = npc_handler_instance.execute_npc_sequence(sct)
            
            if success:
                print("[NPC] 交互完成，切换回地图模式。")
                STATE = "MAP_MODE"
                target2_detected = False  # 锁定状态
                ritual_detected = False
            continue  # 强制结束当前帧，防止执行下方逻辑
            
        # 2. 场景切换保护 (防止覆盖交互状态)
        if STATE not in ["RITUAL_ACTIVE", "NPC_INTERACTING"]:
            if scene == "HIDEOUT":
                STATE = "HIDEOUT_MODE"
            elif scene == "MAP":
                STATE = "MAP_MODE"
                
        # 3. 地图模式
        if STATE == "MAP_MODE":
            # 截取小地图
            monitor = sct.monitors[1]
            mx = monitor['width'] - config_manager.NAV_CFG['map_x_from_right'] - config_manager.NAV_CFG['map_size']
            screenshot = sct.grab({'top': config_manager.NAV_CFG['map_y_from_top'], 
                                  'left': mx, 
                                  'width': config_manager.NAV_CFG['map_size'], 
                                  'height': config_manager.NAV_CFG['map_size']})
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)
            cx, cy = config_manager.NAV_CFG['map_size'] // 2, config_manager.NAV_CFG['map_size'] // 2
            
            # 目标检测
            ritual_detected, ritual_position, ritual_distance, ritual_angle, _ = vision_engine.detect_target2(img, config_manager.ritual_template, cx, cy)
            target2_detected, target2_position, target2_distance, target2_angle, _ = vision_engine.detect_target2(img, config_manager.target2_template, cx, cy)
            
            # 根据检测结果决定行为
            if ritual_detected and ritual_distance < 50:
                print("[MAP] 检测到试炼祭坛，切换到 RITUAL_ACTIVE 状态。")
                STATE = "RITUAL_ACTIVE"
                ritual_detected = False  # 锁定状态
                target2_detected = False
            elif target2_detected and target2_distance < 30:
                print("[MAP] 检测到 NPC/传送门，切换到 NPC_INTERACTING 状态。")
                STATE = "NPC_INTERACTING"
                ritual_detected = False
                target2_detected = False
            else:
                # 正常探路逻辑 (简化版，仅作展示)
                print("[MAP] 正在探路...")

        # 4. 藏身处模式
        elif STATE == "HIDEOUT_MODE":
            print("[STATE] 当前状态: HIDEOUT_MODE")
            # 调用 hideout_manager
            result = hideout_manager.run_logic(sct)
            if result == "MAP_MODE":
                print("[HIDEOUT] 离开藏身处，切换到地图模式。")
                STATE = "MAP_MODE"

        # 5. 仪式/神谕石模式
        elif STATE == "RITUAL_ACTIVE":
            print("[STATE] 当前状态: RITUAL_ACTIVE")
            # 执行仪式管理器
            new_state, _ = ritual_manager.process_ritual(sct)
            if new_state == "MAP_MODE":
                print("[RITUAL] 仪式完成，切换回地图模式。")
                STATE = "MAP_MODE"
                ritual_detected = False  # 锁定状态
                target2_detected = False

        # 显示状态信息 (如果需要)
        # status_img = np.zeros((200, 600, 3), dtype=np.uint8)
        # cv2.putText(status_img, f"STATE: {STATE}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        # cv2.imshow('Main Controller', status_img)
        
        time.sleep(0.1)  # 降低 CPU 占用

if __name__ == '__main__':
    print("[SYSTEM] 准备启动，请在 3 秒内切换到游戏界面...")
    for i in range(3, 0, -1):
        print(f"[SYSTEM] {i}...")
        time.sleep(1)
    try:
        main()
    except Exception as e:
        print(f"[ERROR] 程序异常: {e}")
        import traceback
        traceback.print_exc()
