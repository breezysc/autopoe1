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
        print(f"[MAP] 截图区域异常! monitor: {monitor}, 屏幕尺寸: {screen_width}x{screen_height}")
        raise

class MapProcessor:
    def __init__(self, config_file="hideout_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.portal_template = None
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[MAP] 加载配置失败: {e}")
        return {}
    
    def load_templates(self):
        """加载模板图片（占位符机制）"""
        resource_paths = self.config.get("resource_paths", {})
        
        portal_path = resource_paths.get("portal_icon", "assets/portal.png")
        if os.path.exists(portal_path):
            try:
                self.portal_template = cv2.imread(portal_path, cv2.IMREAD_COLOR)
                print(f"[MAP] 加载传送门模板: {portal_path}")
            except Exception as e:
                print(f"[MAP] 加载传送门模板失败: {e}")
        else:
            print(f"[MAP] 传送门模板不存在: {portal_path}，使用占位符")
    
    def detect_portal(self, sct, image_path=None):
        """检测传送门（预留 image_path 接口）"""
        screen_width, screen_height = get_screen_resolution()
        
        if image_path:
            template = cv2.imread(image_path, cv2.IMREAD_COLOR)
        elif self.portal_template is not None:
            template = self.portal_template
        else:
            return False, (0, 0)
        
        if template is None:
            return False, (0, 0)
        
        full_screen = np.array(sct.grab(sct.monitors[1]))
        img_bgr = cv2.cvtColor(full_screen, cv2.COLOR_BGRA2BGR)
        
        h, w = template.shape[:2]
        if h > img_bgr.shape[0] or w > img_bgr.shape[1]:
            return False, (0, 0)
        
        res = cv2.matchTemplate(img_bgr, template, cv2.TM_CCOEFF_NORMED)
        _, val, _, loc = cv2.minMaxLoc(res)
        
        if val > 0.8:
            center_x = loc[0] + w // 2
            center_y = loc[1] + h // 2
            return True, (center_x, center_y)
        
        return False, (0, 0)
    
    def click_map_device(self):
        """点击制图仪"""
        map_device_coord = self.config.get("coordinates", {}).get("map_device", [0, 0])
        if map_device_coord[0] == 0 and map_device_coord[1] == 0:
            print("[MAP] 制图仪坐标未配置")
            return False
        
        print(f"[MAP] 点击制图仪: {map_device_coord}")
        pydirectinput.click(int(map_device_coord[0]), int(map_device_coord[1]))
        time.sleep(0.5)
        return True
    
    def click_start_map_btn(self):
        """点击开图按钮"""
        start_btn_coord = self.config.get("coordinates", {}).get("start_map_btn", [0, 0])
        if start_btn_coord[0] == 0 and start_btn_coord[1] == 0:
            print("[MAP] 开图按钮坐标未配置")
            return False
        
        print(f"[MAP] 点击开图按钮: {start_btn_coord}")
        pydirectinput.click(int(start_btn_coord[0]), int(start_btn_coord[1]))
        time.sleep(0.5)
        return True
    
    def open_map_sequence(self, sct, stash_controller):
        """自动化开图流"""
        print("[MAP] 开始自动化开图流...")
        
        stash_coord = self.config.get("coordinates", {}).get("stash", [0, 0])
        if stash_coord[0] == 0 and stash_coord[1] == 0:
            print("[MAP] 仓库坐标未配置")
            return False
        
        print("[MAP] 打开仓库")
        pydirectinput.click(int(stash_coord[0]), int(stash_coord[1]))
        time.sleep(0.5)
        
        print("[MAP] 切换至地图页（占位符）")
        stash_controller.switch_stash_tab(0)
        time.sleep(0.3)
        
        print("[MAP] 取出地图（占位符）")
        stash_controller.take_item(0, 0)
        time.sleep(0.3)
        
        print("[MAP] 切换至圣甲虫页（占位符）")
        stash_controller.switch_stash_tab(1)
        time.sleep(0.3)
        
        print("[MAP] 取出圣甲虫（占位符）")
        for i in range(4):
            stash_controller.take_item(i, 0)
            time.sleep(0.2)
        
        print("[MAP] 移动至制图仪")
        self.click_map_device()
        time.sleep(0.5)
        
        print("[MAP] 放入地图（占位符）")
        time.sleep(0.3)
        
        print("[MAP] 点击开启按钮")
        self.click_start_map_btn()
        time.sleep(0.5)
        
        print("[MAP] 等待传送门出现...")
        portal_found = False
        portal_pos = (0, 0)
        
        start_time = time.time()
        while time.time() - start_time < 10:
            portal_found, portal_pos = self.detect_portal(sct)
            if portal_found:
                print(f"[MAP] 检测到传送门: {portal_pos}")
                break
            time.sleep(0.5)
        
        if portal_found:
            print(f"[MAP] 点击传送门: {portal_pos}")
            pydirectinput.click(int(portal_pos[0]), int(portal_pos[1]))
            time.sleep(2)
            return True
        else:
            print("[MAP] 未检测到传送门")
            return False
