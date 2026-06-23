import cv2
import numpy as np
import mss
import time
import os
import pydirectinput
import ctypes

# =================配置与全局变量=================
config_file = 'config.json'

# 初始默认值
map_x_from_right = 6
map_y_from_top = 40
map_size = 380

# 窗口位置
user32 = ctypes.windll.user32
sw, sh = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
win_x, win_y, win_w, win_h = 50, sh - 350, 600, 300

# 祭坛交互 - 锚点定位测试相关
ritual_anchor_template = None
ritual_anchor_detected = False
ritual_anchor_position = None
# 静态坐标库：词缀相对于标题中心点的固定偏移量（根据1080p分辨率调整）
# 需要根据实际游戏截图调整这些值
OFFSET_1 = (0, 60)   # 第一个词缀的偏移量
OFFSET_2 = (80, 60)  # 第二个词缀的偏移量
OFFSET_3 = (160, 60) # 第三个词缀的偏移量
# 词缀图标位置
ritual_affix_positions = []

# 加载配置
def load_config():
    global map_x_from_right, map_y_from_top, map_size
    if os.path.exists(config_file):
        try:
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                c = json.load(f)
                map_x_from_right = c.get('map_x_from_right', map_x_from_right)
                map_y_from_top = c.get('map_y_from_top', map_y_from_top)
                map_size = c.get('map_size', map_size)
        except:
            pass

# 加载锚点模板
def load_ritual_anchor_template():
    global ritual_anchor_template
    anchor_path = 'ritual_anchor.png'
    if os.path.exists(anchor_path):
        try:
            ritual_anchor_template = cv2.imread(anchor_path, cv2.IMREAD_COLOR)
            if ritual_anchor_template is not None:
                print(f"[RITUAL] 加载锚点模板: {anchor_path}")
            else:
                print("[RITUAL] 无法加载锚点模板")
        except:
            print("[RITUAL] 加载锚点模板时出错")
    else:
        print("[RITUAL] 未找到锚点模板，请确保 ritual_anchor.png 存在")

# 检测锚点和词缀位置
def detect_ritual_anchor(img):
    global ritual_anchor_detected, ritual_anchor_position, ritual_affix_positions
    ritual_anchor_detected = False
    ritual_anchor_position = None
    ritual_affix_positions = []
    
    if ritual_anchor_template is None:
        return
    
    h, w = ritual_anchor_template.shape[:2]
    if h > img.shape[0] or w > img.shape[1]:
        return
    
    result = cv2.matchTemplate(img, ritual_anchor_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # 检查匹配得分
    if max_val < 0.7:
        print("[RITUAL] 请靠近祭坛直到出现标题")
        return
    
    # 匹配得分足够高，继续处理
    if max_val > 0.7:
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        
        ritual_anchor_detected = True
        ritual_anchor_position = (center_x, center_y)
        
        # 计算三个词缀图标的位置（使用固定偏移量）
        affix1_x = center_x + OFFSET_1[0]
        affix1_y = center_y + OFFSET_1[1]
        
        affix2_x = center_x + OFFSET_2[0]
        affix2_y = center_y + OFFSET_2[1]
        
        affix3_x = center_x + OFFSET_3[0]
        affix3_y = center_y + OFFSET_3[1]
        
        ritual_affix_positions = [(affix1_x, affix1_y), (affix2_x, affix2_y), (affix3_x, affix3_y)]
        print(f"[RITUAL] 发现锚点，位置: ({center_x}, {center_y})")
        print(f"[RITUAL] 词缀位置: {ritual_affix_positions}")

# 测试悬停功能
def test_ritual_hover():
    """测试悬停功能：鼠标依次移动到三个词缀图标位置"""
    global ritual_affix_positions, map_x_from_right, map_y_from_top, map_size
    
    if not ritual_affix_positions:
        print("[RITUAL] 未检测到词缀位置，无法执行测试悬停")
        return
    
    print("[RITUAL] 开始测试悬停...")
    
    # 获取屏幕尺寸
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    
    # 计算小地图在屏幕上的实际位置
    mx = screen_width - map_x_from_right - map_size
    my = map_y_from_top
    
    for i, (affix_x, affix_y) in enumerate(ritual_affix_positions):
        # 计算词缀在屏幕上的实际位置
        screen_x = mx + int(affix_x)
        screen_y = my + int(affix_y)
        
        print(f"[RITUAL] 移动鼠标到词缀 {i+1} 位置: ({screen_x}, {screen_y})")
        
        # 移动鼠标到词缀位置
        try:
            pydirectinput.moveTo(screen_x, screen_y)
            # 停留0.5秒
            time.sleep(0.5)
        except Exception as e:
            print(f"[RITUAL] 移动鼠标时出错: {e}")
    
    print("[RITUAL] 测试悬停完成")

# 鼠标点击回调函数
def on_mouse_click(event, x, y, flags, param):
    """鼠标点击回调函数"""
    if event == cv2.EVENT_LBUTTONDOWN:
        # 简单的按钮检测（假设按钮在左上角）
        if 10 <= x <= 180 and 10 <= y <= 50:
            test_ritual_hover()

# 主函数
def main():
    
    load_config()
    load_ritual_anchor_template()
    
    # 创建 GUI 窗口
    cv2.namedWindow('Ritual Anchor Test', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('Ritual Anchor Test', cv2.WND_PROP_TOPMOST, 1)
    
    # 设置鼠标点击回调
    cv2.setMouseCallback('Ritual Anchor Test', on_mouse_click)
    
    # 窗口初始化与定位
    hwnd = ctypes.windll.user32.FindWindowW(None, 'Ritual Anchor Test')
    if hwnd:
        ctypes.windll.user32.MoveWindow(hwnd, win_x, win_y, win_w, win_h, True)
    
    # 移除滑动条，使用固定偏移量
    
    with mss.mss() as sct:
        while True:
            if cv2.waitKey(1) == 27: break
            
            # 获取屏幕尺寸
            monitor = sct.monitors[1]
            mx = monitor['width'] - map_x_from_right - map_size
            
            # 捕获小地图区域
            screenshot = sct.grab({'top': map_y_from_top, 'left': mx, 'width': map_size, 'height': map_size})
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)
            
            # 检测锚点
            detect_ritual_anchor(img)
            
            # 绘制
            res_img = img.copy()
            
            # 绘制锚点和词缀位置
            if ritual_anchor_detected and ritual_anchor_position:
                # 绘制锚点位置
                x, y = ritual_anchor_position
                cv2.circle(res_img, (x, y), 5, (0, 255, 0), -1)
                cv2.putText(res_img, "ANCHOR", (x+10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                # 绘制词缀位置
                for i, (affix_x, affix_y) in enumerate(ritual_affix_positions):
                    cv2.circle(res_img, (int(affix_x), int(affix_y)), 8, (255, 0, 255), 2)
                    cv2.putText(res_img, f"AFFIX {i+1}", (int(affix_x)+10, int(affix_y)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
            
            # 绘制自动悬停扫描按钮
            cv2.rectangle(res_img, (10, 10), (180, 50), (0, 128, 255), -1)
            cv2.putText(res_img, "自动悬停扫描", (30, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # 显示结果
            cv2.imshow('Ritual Anchor Test', res_img)
    
    cv2.destroyAllWindows()

if __name__ == '__main__':
    print("[SYSTEM] 启动试炼祭坛锚点测试...")
    print("[SYSTEM] 请在5秒内切换到游戏界面...")
    for i in range(5, 0, -1):
        print(f"[SYSTEM] {i}...")
        time.sleep(1)
    try:
        main()
    except Exception as e:
        print(f"[ERROR] 程序异常: {e}")
        import traceback
        traceback.print_exc()
