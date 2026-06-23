import time
from pynput import mouse
from pynput import keyboard

# 测试坐标采集
print("测试坐标采集功能")
print("=" * 50)
print("按F键记录坐标，按ESC退出")

clicks = []

# 鼠标控制器
mouse_controller = mouse.Controller()

# 按键回调
current_time = 0

print("开始采集坐标...")
print("请按F键记录4个坐标：")
print("1. 锚点坐标")
print("2-4. 词缀坐标")
print("5. 开始按钮坐标")

# 按键监听
running = True

# 按键回调
last_press_time = 0

# 记录坐标
coordinates = []

# 按键监听
class HotkeyListener(keyboard.Listener):
    def __init__(self):
        super().__init__(on_press=self.on_press, on_release=self.on_release)
        self.running = True
    
    def on_press(self, key):
        global last_press_time
        try:
            if key.char == 'f' and self.running:
                current_time = time.time()
                if current_time - last_press_time > 0.5:
                    last_press_time = current_time
                    screen_x, screen_y = mouse_controller.position
                    coordinates.append((screen_x, screen_y))
                    print(f"记录坐标 #{len(coordinates)}: ({screen_x}, {screen_y})")
                    if len(coordinates) == 4:
                        print("坐标采集完成！")
                        self.running = False
                        return False
            elif key == keyboard.Key.esc:
                self.running = False
                return False
        except AttributeError:
            pass
    
    def on_release(self, key):
        pass

# 启动监听
listener = HotkeyListener()
listener.start()

# 等待监听结束
while listener.running:
    time.sleep(0.1)

# 输出结果
print("\n采集结果:")
print("=" * 50)
if len(coordinates) >= 4:
    print(f"锚点坐标: {coordinates[0]}")
    for i in range(1, 4):
        print(f"词缀坐标 #{i}: {coordinates[i]}")
    print(f"开始按钮坐标: {coordinates[3]}")
else:
    print("坐标采集不完整")

print("\n测试完成")
