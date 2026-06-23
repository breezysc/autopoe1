import time
from pynput import mouse

# 简单的坐标采集测试
print("简单坐标采集测试")
print("=" * 50)

# 鼠标控制器
mouse_controller = mouse.Controller()

# 采集坐标
coordinates = []

print("请按Enter键记录坐标，按Ctrl+C退出")
print("\n1. 请将鼠标移动到锚点位置，按Enter")

for i in range(5):
    try:
        input()
        screen_x, screen_y = mouse_controller.position
        coordinates.append((screen_x, screen_y))
        if i == 0:
            print(f"锚点坐标: ({screen_x}, {screen_y})")
            print("\n2. 请将鼠标移动到第一个词缀位置，按Enter")
        elif i < 3:
            print(f"词缀坐标 #{i}: ({screen_x}, {screen_y})")
            if i == 2:
                print("\n3. 请将鼠标移动到开始按钮位置，按Enter")
        else:
            print(f"开始按钮坐标: ({screen_x}, {screen_y})")
            print("\n坐标采集完成！")
    except KeyboardInterrupt:
        break

# 输出结果
print("\n采集结果:")
print("=" * 50)
if len(coordinates) >= 4:
    print(f"锚点坐标: {coordinates[0]}")
    for i in range(1, 3):
        print(f"词缀坐标 #{i}: {coordinates[i]}")
    print(f"开始按钮坐标: {coordinates[3]}")
else:
    print("坐标采集不完整")

print("\n测试完成")
