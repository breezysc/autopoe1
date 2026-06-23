import cv2
import numpy as np
import mss
import time
import pydirectinput

class TeleTest:
    def __init__(self):
        self.sct = mss.mss()
        self.tet1_template = None
        self.tet2_template = None
    
    def load_templates(self):
        """加载模板"""
        # 加载tet1.png模板
        tet1_path = 'tet1.png'
        if cv2.os.path.exists(tet1_path):
            try:
                self.tet1_template = cv2.imread(tet1_path, cv2.IMREAD_COLOR)
                if self.tet1_template is not None:
                    print(f"[TEST] 加载tet1.png模板成功，尺寸: {self.tet1_template.shape[1]}x{self.tet1_template.shape[0]}")
                else:
                    print(f"[TEST] 无法加载tet1.png，请检查文件格式")
            except Exception as e:
                print(f"[TEST] 加载tet1.png模板失败: {e}")
        else:
            print(f"[TEST] tet1.png 不存在")
        
        # 加载tet2.png模板
        tet2_path = 'tet2.png'
        if cv2.os.path.exists(tet2_path):
            try:
                self.tet2_template = cv2.imread(tet2_path, cv2.IMREAD_COLOR)
                if self.tet2_template is not None:
                    print(f"[TEST] 加载tet2.png模板成功，尺寸: {self.tet2_template.shape[1]}x{self.tet2_template.shape[0]}")
                else:
                    print(f"[TEST] 无法加载tet2.png，请检查文件格式")
            except Exception as e:
                print(f"[TEST] 加载tet2.png模板失败: {e}")
        else:
            print(f"[TEST] tet2.png 不存在")
    
    def detect_tet(self):
        """检测tet1.png和tet2.png"""
        # 捕获全屏
        monitor = self.sct.monitors[1]
        img = np.array(self.sct.grab(monitor))
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        # 检测tet1.png
        if self.tet1_template is not None:
            res1 = cv2.matchTemplate(img_bgr, self.tet1_template, cv2.TM_CCOEFF_NORMED)
            _, max_val1, _, max_loc1 = cv2.minMaxLoc(res1)
            print(f"[TEST] tet1.png 匹配度: {max_val1:.4f}")
            
            if max_val1 > 0.38:
                h, w = self.tet1_template.shape[:2]
                center_x = max_loc1[0] + w // 2
                center_y = max_loc1[1] + h // 2
                print(f"[TEST] 检测到tet1.png，中心坐标: ({center_x}, {center_y})")
                return True, (center_x, center_y), "tet1.png"
        else:
            print("[TEST] 未加载tet1.png模板，跳过检测")
        
        # 检测tet2.png
        if self.tet2_template is not None:
            res2 = cv2.matchTemplate(img_bgr, self.tet2_template, cv2.TM_CCOEFF_NORMED)
            _, max_val2, _, max_loc2 = cv2.minMaxLoc(res2)
            print(f"[TEST] tet2.png 匹配度: {max_val2:.4f}")
            
            if max_val2 > 0.52:
                h, w = self.tet2_template.shape[:2]
                center_x = max_loc2[0] + w // 2
                center_y = max_loc2[1] + h // 2
                print(f"[TEST] 检测到tet2.png，中心坐标: ({center_x}, {center_y})")
                return True, (center_x, center_y), "tet2.png"
        else:
            print("[TEST] 未加载tet2.png模板，跳过检测")
        
        print("[TEST] 未检测到tet1.png和tet2.png")
        return False, None, None
    
    def run(self):
        """运行测试"""
        print("[TEST] 开始运行tele1.py测试脚本")
        
        # 加载模板
        self.load_templates()
        
        # 延迟2秒
        print("[TEST] 延迟2秒...")
        for i in range(2, 0, -1):
            print(f"[TEST] {i}...")
            time.sleep(1)
        
        # 检测tet1.png和tet2.png
        print("[TEST] 开始检测tet1.png和tet2.png...")
        detected, pos, template_name = self.detect_tet()
        
        # 如果检测到，点击下方30坐标的位置
        if detected and pos:
            click_x, click_y = pos[0], pos[1] + 30
            print(f"[TEST] 准备点击位置: ({click_x}, {click_y}) (在{template_name}下方30像素)")
            pydirectinput.click(click_x, click_y)
            print(f"[TEST] 已点击位置: ({click_x}, {click_y})")
        
        print("[TEST] 测试完成")

if __name__ == '__main__':
    test = TeleTest()
    test.run()
