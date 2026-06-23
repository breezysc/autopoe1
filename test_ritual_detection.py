import cv2
import numpy as np
import mss
import time

print("[TEST] 测试试炼祭坛检测功能...")

# 测试模板加载
def test_ritual_template_loading():
    print("[TEST] 测试试炼祭坛模板加载...")
    ritual_path = 'ritual_icon.png'
    if cv2.os.path.exists(ritual_path):
        try:
            template = cv2.imread(ritual_path, cv2.IMREAD_COLOR)
            if template is not None:
                print(f"[TEST] 成功加载试炼祭坛模板: {ritual_path}")
                print(f"[TEST] 模板尺寸: {template.shape}")
                return template
            else:
                print(f"[TEST] 无法加载试炼祭坛模板")
                return None
        except Exception as e:
            print(f"[TEST] 加载模板时出错: {e}")
            return None
    else:
        print(f"[TEST] 模板文件不存在: {ritual_path}")
        return None

# 测试模板匹配
def test_ritual_template_matching(template):
    print("[TEST] 测试试炼祭坛模板匹配...")
    if template is None:
        print("[TEST] 模板不存在，跳过匹配测试")
        return
    
    try:
        # 创建测试图像
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        # 在图像中绘制一个模拟的试炼祭坛图标
        cv2.circle(test_img, (50, 50), 10, (0, 255, 255), -1)
        
        # 执行模板匹配
        result = cv2.matchTemplate(test_img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        print(f"[TEST] 模板匹配得分: {max_val}")
        print(f"[TEST] 匹配位置: {max_loc}")
        
        # 绘制结果
        h, w = template.shape[:2]
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(test_img, top_left, bottom_right, (0, 255, 0), 2)
        cv2.imwrite('test_ritual_match.png', test_img)
        print("[TEST] 匹配结果已保存为 test_ritual_match.png")
        return True
    except Exception as e:
        print(f"[TEST] 模板匹配出错: {e}")
        return False

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
                'width': 200,
                'height': 200
            }
            screenshot = sct.grab(test_monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            print(f"[TEST] 捕获图像尺寸: {img.shape}")
            cv2.imwrite('test_screen_capture.png', img)
            print("[TEST] 屏幕捕获结果已保存为 test_screen_capture.png")
            return True
    except Exception as e:
        print(f"[TEST] 屏幕捕获出错: {e}")
        return False

if __name__ == '__main__':
    print("[TEST] 开始测试试炼祭坛检测功能...")
    template = test_ritual_template_loading()
    test_ritual_template_matching(template)
    
    # 添加延迟，让用户有时间切到游戏界面
    print("[TEST] 请在5秒内切换到游戏界面...")
    for i in range(5, 0, -1):
        print(f"[TEST] {i}...")
        time.sleep(1)
    
    test_screen_capture()
    print("[TEST] 测试完成!")
