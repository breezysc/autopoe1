import cv2
import numpy as np
import time
import pydirectinput
import json
import os
import ctypes

# 强制 DPI 感知
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

def safe_screenshot(sct, monitor, screen_width, screen_height):
    """安全截图，边界保护"""
    monitor['left'] = max(0, min(int(monitor['left']), screen_width - monitor['width']))
    monitor['top'] = max(0, min(int(monitor['top']), screen_height - monitor['height']))
    
    try:
        img = np.array(sct.grab(monitor))
        return img
    except Exception as e:
        print(f"[STASH] 截图区域异常! monitor: {monitor}, 屏幕尺寸: {screen_width}x{screen_height}")
        raise

class StashController:
    def __init__(self, config_file="hideout_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.slot_width = 50
        self.slot_height = 50
        self.inventory_start_x = 100
        self.inventory_start_y = 100
        self.inventory_cols = 12
        self.inventory_rows = 5
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[STASH] 加载配置失败: {e}")
        return {}
    
    def is_protected_slot(self, col, row):
        """检查是否是保护区格子"""
        protected_slots = self.config.get("protected_slots", [])
        for slot in protected_slots:
            if len(slot) >= 2 and slot[0] == col and slot[1] == row:
                return True
        return False
    
    def get_slot_coordinate(self, col, row):
        """获取格子坐标"""
        x = self.inventory_start_x + col * self.slot_width
        y = self.inventory_start_y + row * self.slot_height
        return x, y
    
    def is_item_slot(self, sct, col, row):
        """识别格子是否有物品（占位符逻辑）"""
        screen_width, screen_height = get_screen_resolution()
        x, y = self.get_slot_coordinate(col, row)
        
        monitor = {
            "top": int(y), 
            "left": int(x), 
            "width": self.slot_width, 
            "height": self.slot_height
        }
        
        try:
            img = safe_screenshot(sct, monitor, screen_width, screen_height)
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            avg_brightness = np.mean(gray)
            
            if avg_brightness > 50:
                return True
            return False
        except:
            return False
    
    def click_slot(self, col, row, ctrl_click=False):
        """点击格子"""
        x, y = self.get_slot_coordinate(col, row)
        
        if ctrl_click:
            pydirectinput.keyDown('ctrl')
        
        pydirectinput.click(int(x), int(y))
        time.sleep(0.1)
        
        if ctrl_click:
            pydirectinput.keyUp('ctrl')
    
    def dump_inventory(self, sct):
        """存入逻辑：遍历非保护区格子，Ctrl+Click 存包"""
        print("[STASH] 开始存入流程...")
        
        stash_coord = self.config.get("coordinates", {}).get("stash", [0, 0])
        if stash_coord[0] == 0 and stash_coord[1] == 0:
            print("[STASH] 仓库坐标未配置")
            return False
        
        pydirectinput.click(int(stash_coord[0]), int(stash_coord[1]))
        time.sleep(0.5)
        
        items_deposited = 0
        
        for row in range(self.inventory_rows):
            for col in range(self.inventory_cols):
                if self.is_protected_slot(col, row):
                    print(f"[STASH] 跳过保护区格子 ({col}, {row})")
                    continue
                
                if self.is_item_slot(sct, col, row):
                    print(f"[STASH] 存入格子 ({col}, {row})")
                    self.click_slot(col, row, ctrl_click=True)
                    items_deposited += 1
                    time.sleep(0.2)
        
        print(f"[STASH] 存入完成，共存入 {items_deposited} 个物品")
        return True
    
    def take_item(self, col, row):
        """从仓库取出物品（占位符）"""
        print(f"[STASH] 从仓库格子 ({col}, {row}) 取出物品")
        x, y = self.get_slot_coordinate(col, row)
        pydirectinput.click(int(x), int(y))
        time.sleep(0.2)
    
    def switch_stash_tab(self, tab_index):
        """切换仓库标签页（占位符）"""
        print(f"[STASH] 切换到仓库标签页 {tab_index}")
        stash_coord = self.config.get("coordinates", {}).get("stash", [0, 0])
        tab_x = stash_coord[0] + tab_index * 60
        tab_y = stash_coord[1] - 30
        pydirectinput.click(int(tab_x), int(tab_y))
        time.sleep(0.3)
