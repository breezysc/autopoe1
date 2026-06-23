import time
from pynput import mouse, keyboard

# 全局变量
anchor = None
coordinates = []

print("测试坐标记录系统")
print("按F键记录坐标")
print("第1次按F: 记录锚点")
print("第2-4次按F: 记录词缀坐标")
print("按ESC键退出")

# 鼠标控制器
mouse_controller = mouse.Controller()

# 按键回调
from pynput.keyboard import Key

def on_press(key):
    global anchor, coordinates
    try:
        if key.char == 'f':
            x, y = mouse_controller.position
            if not anchor:
                anchor = (x, y)
                print(f"锚点坐标: {anchor}")
            else:
                if len(coordinates) < 3:
                    coordinates.append((x, y))
                    print(f"词缀坐标 #{len(coordinates)}: ({x}, {y})")
                    if len(coordinates) >= 3:
                        print("坐标记录完成")
                        # 计算偏移量
                        if anchor:
                            offsets = []
                            for coord in coordinates:
                                offset_x = coord[0] - anchor[0]
                                offset_y = coord[1] - anchor[1]
                                offsets.append([offset_x, offset_y])
                            print(f"偏移量: {offsets}")
    except AttributeError:
        if key == Key.esc:
            print("退出测试")
            return False

# 启动监听
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
