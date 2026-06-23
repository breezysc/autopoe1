import time
from config_manager import config_manager
from vision_engine import vision_engine

# 加载配置和资源
print("加载配置和资源...")
config_manager.load_all()

# 测试场景检测
print("开始测试场景检测...")
for i in range(5):
    scene = vision_engine.detect_scene(config_manager.hideout_template)
    print(f"场景检测结果 #{i+1}: {scene}")
    time.sleep(1)

print("测试完成")
