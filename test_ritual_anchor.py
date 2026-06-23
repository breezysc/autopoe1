import cv2
import numpy as np
import os

print("[TEST] 测试试炼祭坛锚点检测功能...")

# 测试锚点模板加载
def test_anchor_template_loading():
    print("[TEST] 测试锚点模板加载...")
    anchor_path = 'ritual_anchor.png'
    if os.path.exists(anchor_path):
        try:
            template = cv2.imread(anchor_path, cv2.IMREAD_COLOR)
            if template is not None:
                print(f"[TEST] 成功加载锚点模板: {anchor_path}")
                print(f"[TEST] 模板尺寸: {template.shape}")
                return template
            else:
                print(f"[TEST] 无法加载锚点模板")
                return None
        except Exception as e:
            print(f"[TEST] 加载模板时出错: {e}")
            return None
    else:
        print(f"[TEST] 模板文件不存在: {anchor_path}")
        return None

# 测试模板匹配
def test_anchor_template_matching(template):
    print("[TEST] 测试锚点模板匹配...")
    if template is None:
        print("[TEST] 模板不存在，跳过匹配测试")
        return
    
    try:
        # 创建测试图像
        test_img = np.zeros((200, 200, 3), dtype=np.uint8)
        # 在图像中绘制一个模拟的锚点
        cv2.putText(test_img, "击败的怪物波次", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
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
        cv2.imwrite('test_anchor_match.png', test_img)
        print("[TEST] 匹配结果已保存为 test_anchor_match.png")
        return True
    except Exception as e:
        print(f"[TEST] 模板匹配出错: {e}")
        return False

if __name__ == '__main__':
    print("[TEST] 开始测试试炼祭坛锚点检测功能...")
    template = test_anchor_template_loading()
    test_anchor_template_matching(template)
    print("[TEST] 测试完成!")
