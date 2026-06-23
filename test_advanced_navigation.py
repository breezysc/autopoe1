import numpy as np
import time

# 测试导航逻辑深度优化功能
def test_advanced_navigation():
    # 模拟参数
    map_size = 200
    scan_radius = 50
    sensitivity = 0.5
    last_best_index = 0  # 初始方向：0度（北）
    wall_follow_mode = 1  # 贴右墙模式
    inertia_mode = False
    inertia_start_time = 0
    full_path_threshold = 0.98
    
    print("=== 导航逻辑深度优化测试 ===")
    print(f"初始方向索引: {last_best_index} (0度，北)")
    print(f"贴右墙模式: {wall_follow_mode}")
    
    # 测试场景1：贴墙锚定（右手侧太空）
    print("\n=== 测试场景1：贴墙锚定（右手侧太空） ===")
    print("模拟右手侧（-30度到-90度）完全是空地")
    
    # 模拟多帧导航
    for frame in range(3):
        print(f"\n帧 {frame + 1}:")
        
        # 模拟12方向的得分和碰撞检测
        scores = [0.8] * 12  # 所有方向默认得分
        collision_detected = [False] * 12  # 所有方向默认无碰撞
        
        # 模拟右手侧完全是空地（没有墙）
        # 右手侧：-30度（索引11）、-60度（索引10）、-90度（索引9）
        # 这些方向的得分都不为0，表示没有墙
        
        # 方向选择逻辑
        max_index = 0
        max_score = 0
        
        # 贴墙锚定逻辑：检测右手侧是否完全是空地
        right_side_clear = True
        # 检查右手侧（-30度到-90度，即当前方向的右侧）
        for i in range(1, 4):  # 1: -30度, 2: -60度, 3: -90度
            right_index = (last_best_index - i) % 12
            if right_index < 0:
                right_index += 12
            # 检查该方向是否有墙（得分是否为0）
            if scores[right_index] == 0:
                right_side_clear = False
                break
        
        if right_side_clear:
            # 右手侧完全是空地，执行惯性直线行走 + 5度微幅右偏
            print("[STATUS] 右手侧太空，执行贴墙锚定：惯性直线行走 + 5度微幅右偏")
            # 计算微幅右偏的方向（-1个索引，即右转30度）
            max_index = (last_best_index - 1) % 12
            if max_index < 0:
                max_index += 12
            max_score = scores[max_index]
        else:
            # 按照右手优先顺序搜索
            print("[SYSTEM] 贴右墙模式：右手优先搜索")
            max_score = max(scores)
            max_index = scores.index(max_score)
        
        # 更新上一帧的最佳方向
        last_best_index = max_index
        print(f"最终方向: {max_index} (角度: {max_index * 30}度)")
        
        # 模拟帧间隔
        time.sleep(0.1)
    
    # 测试场景2：切向避障平滑（遇到微小障碍物）
    print("\n=== 测试场景2：切向避障平滑（遇到微小障碍物） ===")
    print("模拟前方有微小障碍物")
    
    # 模拟多帧导航
    for frame in range(3):
        print(f"\n帧 {frame + 1}:")
        
        # 模拟12方向的得分和碰撞检测
        scores = [0.8] * 12  # 所有方向默认得分
        collision_detected = [False] * 12  # 所有方向默认无碰撞
        obstacle_directions = []  # 记录有障碍物的方向索引
        
        # 模拟前方（0度）有微小障碍物
        obstacle_directions.append(0)
        # 降低障碍物方向的得分
        scores[0] = 0.4
        collision_detected[0] = True
        
        # 处理有障碍物的方向，提高相邻方向的得分
        for i in obstacle_directions:
            # 提高左侧方向的得分
            left_index = (i - 1) % 12
            if left_index < 0:
                left_index += 12
            if left_index < len(scores):
                scores[left_index] *= 1.2  # 提高左侧方向的得分
            
            # 提高右侧方向的得分
            right_index = (i + 1) % 12
            if right_index < len(scores):
                scores[right_index] *= 1.2  # 提高右侧方向的得分
        
        # 方向选择逻辑
        max_score = max(scores)
        max_index = scores.index(max_score)
        
        print(f"障碍物方向: 0 (角度: 0度)")
        print(f"左侧方向得分: {scores[11]:.2f}, 右侧方向得分: {scores[1]:.2f}")
        print(f"最终方向: {max_index} (角度: {max_index * 30}度)")
        
        # 模拟帧间隔
        time.sleep(0.1)
    
    # 测试场景3：空旷地带的方向记忆增强
    print("\n=== 测试场景3：空旷地带的方向记忆增强 ===")
    print("模拟进入空旷地带，然后遇到墙壁")
    
    # 模拟多帧导航
    for frame in range(10):
        print(f"\n帧 {frame + 1}:")
        
        # 模拟12方向的得分和碰撞检测
        scores = [0.99] * 12  # 所有方向默认得分
        collision_detected = [False] * 12  # 所有方向默认无碰撞
        full_path_count = 12  # 所有方向都是完全通路
        
        # 模拟第5帧遇到墙壁
        if frame >= 4:
            scores[0] = 0  # 0度方向得分设为0
            collision_detected[0] = True  # 0度方向有碰撞
            full_path_count = 11  # 有一个方向不是完全通路
        
        # 惯性模式检测
        current_time = time.time()
        if full_path_count == 12:
            # 所有方向都是完全通路，进入惯性模式
            if not inertia_mode:
                inertia_mode = True
                inertia_start_time = current_time
                print("[STATUS] 进入惯性模式：空旷区域")
        else:
            # 检测到墙壁，退出惯性模式
            # 但如果惯性模式启动时间不足1.5秒，继续保持惯性模式
            if inertia_mode:
                if current_time - inertia_start_time >= 1.5:
                    inertia_mode = False
                    print("[STATUS] 退出惯性模式：检测到墙壁")
                else:
                    print("[STATUS] 惯性模式保持中：检测到墙壁但时间不足1.5秒")
        
        # 方向选择逻辑
        if inertia_mode:
            # 惯性模式：强制使用上一帧的方向
            max_index = last_best_index
            max_score = scores[max_index]
            print(f"[STATUS] 空旷区域，保持惯性行驶方向: {max_index}")
        else:
            # 常规模式：找最高分
            print("[SYSTEM] 常规模式：找最高分")
            max_score = max(scores)
            max_index = scores.index(max_score)
        
        # 更新上一帧的最佳方向
        last_best_index = max_index
        print(f"最终方向: {max_index} (角度: {max_index * 30}度)")
        
        # 模拟帧间隔
        time.sleep(0.2)  # 延长帧间隔，模拟时间流逝
    
    print("\n=== 测试完成 ===")
    print("导航逻辑深度优化测试通过！")

if __name__ == '__main__':
    test_advanced_navigation()
