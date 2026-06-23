import cv2
import numpy as np
import mss

class VisionEngine:
    def __init__(self):
        self.sct = mss.mss()
    
    def capture_screen(self):
        """捕获全屏"""
        monitor = self.sct.monitors[1]
        img = np.array(self.sct.grab(monitor))
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    def detect_ritual(self, img, template):
        """检测试炼祭坛"""
        if template is None:
            return False, None, 0, 0
        
        h, w = template.shape[:2]
        if h > img.shape[0] or w > img.shape[1]:
            return False, None, 0, 0
        
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        
        if max_val > 0.6:
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return True, (center_x, center_y), max_val, 0
        return False, None, 0, 0
    
    def detect_target2(self, img, template, cx, cy):
        """检测目标2"""
        if template is None:
            return False, None, 0, 0, 0
        
        h, w = template.shape[:2]
        if h > img.shape[0] or w > img.shape[1]:
            return False, None, 0, 0, 0
        
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        
        if max_val > 0.6:
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            distance = np.sqrt((center_x - cx)**2 + (center_y - cy)**2)
            angle = np.degrees(np.arctan2(center_y - cy, center_x - cx)) + 90
            if angle < 0: angle += 360
            return True, (center_x, center_y), distance, angle, max_val
        return False, None, 0, 0, 0
    
    def find_npc_pos(self, img, template):
        """寻找NPC位置"""
        if template is None:
            return False, None
        
        h, w = template.shape[:2]
        if h > img.shape[0] or w > img.shape[1]:
            return False, None
        
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        
        if max_val > 0.75:
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return True, (center_x, center_y)
        return False, None
    
    def check_stop(self, img, template):
        """检查是否需要停止"""
        if template is None:
            return False
        
        h, w = template.shape[:2]
        if h > img.shape[0] or w > img.shape[1]:
            return False
        
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        
        return max_val > 0.75
    
    def detect_scene(self, hideout_template):
        """检测场景类型"""
        # 捕获全屏
        img = self.capture_screen()
        
        # 检查是否在藏身处
        if hideout_template is not None:
            h, w = hideout_template.shape[:2]
            if h <= img.shape[0] and w <= img.shape[1]:
                res = cv2.matchTemplate(img, hideout_template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(res)
                
                if max_val > 0.75:
                    return "HIDEOUT"
        
        # 默认返回地图场景
        return "MAP"

# 创建全局视觉引擎实例
vision_engine = VisionEngine()