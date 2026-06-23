import time
import mss
from npc_handler import NPC_Handler
from config_manager import config_manager

# 加载配置和资源
print("加载配置和资源...")
config_manager.load_all()

# 初始化NPC处理器
print("初始化NPC处理器...")
npc_handler = NPC_Handler(
    config_manager.NPC_CFG, 
    config_manager.API_KEY, 
    config_manager.npc_template, 
    config_manager.tet_template,
    config_manager.tele_template
)

# 测试NPC交互
print("开始测试NPC交互...")
print("按Enter键开始执行NPC交互序列")
input()

with mss.mss() as sct:
    print("执行NPC交互序列...")
    result = npc_handler.execute_npc_sequence(sct)
    print(f"交互结果: {result}")

print("测试完成")
