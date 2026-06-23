import cv2
import numpy as np
import mss
import time

print("[TEST] 测试基本功能...")

# 测试模板加载
def test_template_loading():
    print("[TEST] 测试模板加载...")
    template_paths = ['altar_yellow.png', 'altar_purple.png']
    for path in template_paths:
        if cv2.os.path.exists(path):
            try:
                template = cv2.imread(path, cv2.IMREAD_COLOR)
                if template is not None:
                    print(f"[TEST] 成功加载模板: {path}")
                else:
                    print(f"[TEST] 无法加载模板: {path}")
            except Exception as e:
                print(f"[TEST] 加载模板时出错: {e}")
        else:
            print(f"[TEST] 模板文件不存在: {path}")

# 测试屏幕捕获
def test_screen_capture():
    print("[TEST] 测试屏幕捕获...")
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            print(f"[TEST] 屏幕尺寸: {monitor['width']}x{monitor['height']}")
            # 捕获小区域
            test_monitor = {
                'top': 100,
                'left': 100,
                'width': 100,
                'height': 100
            }
            screenshot = sct.grab(test_monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            print(f"[TEST] 捕获图像尺寸: {img.shape}")
            return True
    except Exception as e:
        print(f"[TEST] 屏幕捕获出错: {e}")
        return False

# 测试模板匹配
def test_template_matching():
    print("[TEST] 测试模板匹配...")
    try:
        # 创建测试图像
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        # 在图像中绘制一个黄色方块作为测试
        cv2.rectangle(test_img, (30, 30), (70, 70), (0, 255, 255), -1)
        
        # 创建模板
        template = np.zeros((20, 20, 3), dtype=np.uint8)
        cv2.rectangle(template, (0, 0), (20, 20), (0, 255, 255), -1)
        
        # 执行模板匹配
        result = cv2.matchTemplate(test_img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        print(f"[TEST] 模板匹配得分: {max_val}")
        print(f"[TEST] 匹配位置: {max_loc}")
        return True
    except Exception as e:
        print(f"[TEST] 模板匹配出错: {e}")
        return False

if __name__ == '__main__':
    print("[TEST] 开始测试...")
    test_template_loading()
    test_screen_capture()
    test_template_matching()
    print("[TEST] 测试完成!")
