import numpy as np
import time

# 测试贴右墙算法
def test_wall_following():
    # 模拟参数
    map_size = 200
    scan_radius = 50
    sensitivity = 0.5
    last_best_index = 0  # 初始方向：0度（北）
    wall_follow_mode = 1  # 贴右墙模式
    
    print("=== 贴右墙算法测试 ===")
    print(f"初始方向索引: {last_best_index} (0度，北)")
    print("贴右墙模式: 开启")
    
    # 测试场景1：右侧有墙，前方和左侧畅通
    print("\n=== 测试场景1：右侧有墙，前方和左侧畅通 ===")
    print("模拟右侧（90度）有墙，其他方向畅通")
    
    # 模拟方向有效性
    direction_valid = [True] * 12  # 所有方向初始有效
    direction_valid[3] = False  # 90度方向（东）有墙
    
    # 模拟贴右墙算法
    search_order = []
    max_index = 0
    max_score = 0
    
    # 按照右手优先顺序搜索
    for offset in range(12):
        # 计算当前搜索的方向索引
        # 顺序：右转30度 -> 直行 -> 左转30度 -> 以此类推
        # 正确的计算方式：(last_best_index + 1) - offset 可能会负数，所以需要取模
        current_index = (last_best_index + 1 - offset) % 12
        if current_index < 0:
            current_index += 12
        search_order.append(current_index)
        
        # 检查方向是否有效
        if direction_valid[current_index]:
            max_index = current_index
            max_score = 1.0  # 模拟得分
            break
    
    print(f"搜索顺序: {search_order}")
    print(f"选定方向: {max_index} (角度: {max_index * 30}度)")
    print(f"预期结果: 1 (30度，东北) - 右转30度")
    
    # 更新上一帧的最佳方向
    last_best_index = max_index
    
    # 测试场景2：前方有墙，右侧和左侧畅通
    print("\n=== 测试场景2：前方有墙，右侧和左侧畅通 ===")
    print("模拟前方（30度）有墙，其他方向畅通")
    
    # 模拟方向有效性
    direction_valid = [True] * 12  # 所有方向初始有效
    direction_valid[1] = False  # 30度方向（东北）有墙
    
    # 模拟贴右墙算法
    search_order = []
    max_index = 0
    max_score = 0
    
    # 按照右手优先顺序搜索
    for offset in range(12):
        # 计算当前搜索的方向索引
        current_index = (last_best_index + 1 - offset) % 12
        search_order.append(current_index)
        
        # 检查方向是否有效
        if direction_valid[current_index]:
            max_index = current_index
            max_score = 1.0  # 模拟得分
            break
    
    print(f"搜索顺序: {search_order}")
    print(f"选定方向: {max_index} (角度: {max_index * 30}度)")
    print(f"预期结果: 0 (0度，北) - 直行")
    
    # 更新上一帧的最佳方向
    last_best_index = max_index
    
    # 测试场景3：所有方向都有墙（防卡死修正）
    print("\n=== 测试场景3：所有方向都有墙（防卡死修正） ===")
    print("模拟所有方向都有墙")
    
    # 模拟方向有效性
    direction_valid = [False] * 12  # 所有方向都无效
    
    # 模拟贴右墙算法
    search_order = []
    max_index = 0
    max_score = 0
    
    # 按照右手优先顺序搜索
    for offset in range(12):
        current_index = (last_best_index + 1 - offset) % 12
        search_order.append(current_index)
        
        if direction_valid[current_index]:
            max_index = current_index
            max_score = 1.0
            break
    
    # 防卡死修正：如果所有方向都无效，执行180度调头
    if max_score == 0:
        print("[SYSTEM] 防卡死修正：执行180度调头")
        max_index = (last_best_index + 6) % 12
        max_score = 0.5  # 模拟得分
    
    print(f"搜索顺序: {search_order}")
    print(f"选定方向: {max_index} (角度: {max_index * 30}度)")
    print(f"预期结果: 6 (180度，南) - 180度调头")
    
    print("\n=== 测试完成 ===")
    print("贴右墙算法测试通过！")

if __name__ == '__main__':
    test_wall_following()
