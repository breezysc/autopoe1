import cv2
import numpy as np
import mss

print("测试模板匹配")
print("=" * 50)

# 加载模板
start_template = cv2.imread('start.png', cv2.IMREAD_COLOR)
ritual_anchor_template = cv2.imread('ritual_anchor.png', cv2.IMREAD_COLOR)

if start_template is not None:
    print(f"start.png 模板尺寸: {start_template.shape[1]}x{start_template.shape[0]}")
else:
    print("无法加载 start.png")

if ritual_anchor_template is not None:
    print(f"ritual_anchor.png 模板尺寸: {ritual_anchor_template.shape[1]}x{ritual_anchor_template.shape[0]}")
else:
    print("无法加载 ritual_anchor.png")

print("=" * 50)
print("开始捕获屏幕并测试匹配...")

with mss.mss() as sct:
    # 捕获全屏
    monitor = sct.monitors[1]
    full_screen = np.array(sct.grab(monitor))
    img_bgr = cv2.cvtColor(full_screen, cv2.COLOR_BGRA2BGR)
    
    print(f"屏幕尺寸: {img_bgr.shape[1]}x{img_bgr.shape[0]}")
    
    # 测试 start.png 匹配
    if start_template is not None:
        res = cv2.matchTemplate(img_bgr, start_template, cv2.TM_CCOEFF_NORMED)
        _, val, _, loc = cv2.minMaxLoc(res)
        print(f"start.png 匹配度: {val:.3f}")
        print(f"匹配位置: {loc}")
    
    # 测试 ritual_anchor.png 匹配
    if ritual_anchor_template is not None:
        res = cv2.matchTemplate(img_bgr, ritual_anchor_template, cv2.TM_CCOEFF_NORMED)
        _, val, _, loc = cv2.minMaxLoc(res)
        print(f"ritual_anchor.png 匹配度: {val:.3f}")
        print(f"匹配位置: {loc}")

print("测试完成")
