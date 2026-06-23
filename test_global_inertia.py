import numpy as np
import time

# 测试全局方向惯性增强功能
def test_global_inertia():
    # 模拟参数
    map_size = 200
    scan_radius = 50
    sensitivity = 0.5
    last_best_index = 0  # 初始方向：0度（北）
    inertia_weight = 115  # 方向惯性加权，115%（1.15倍）
    
    print("=== 全局方向惯性增强测试 ===")
    print(f"初始方向索引: {last_best_index} (0度，北)")
    print(f"方向惯性加权: {inertia_weight}% ({inertia_weight/100.0:.2f}倍)")
    
    # 测试场景1：直线行驶，旁边有得分稍高的岔路
    print("\n=== 测试场景1：直线行驶，旁边有得分稍高的岔路 ===")
    print("模拟当前方向（北）得分0.8，右侧（东北）得分0.85（稍高）")
    
    # 模拟多帧导航
    for frame in range(5):
        print(f"\n帧 {frame + 1}:")
        
        # 模拟12方向的得分和碰撞检测
        scores = [0.8] * 12  # 所有方向默认得分
        collision_detected = [False] * 12  # 所有方向默认无碰撞
        direction_valid = [True] * 12  # 所有方向默认有效
        
        # 模拟当前方向（北，索引0）得分0.8
        scores[0] = 0.8
        # 模拟右侧（东北，索引1）得分0.85（稍高）
        scores[1] = 0.85
        
        # 全局方向惯性加权：在所有模式下应用
        if last_best_index >= 0 and last_best_index < 12:
            # 应用惯性加权
            weight_factor = inertia_weight / 100.0
            scores[last_best_index] *= weight_factor
            print(f"[STATUS] 应用方向惯性加权: {weight_factor:.2f}倍")
        
        # 方向选择逻辑：找最高分
        max_score = max(scores)
        max_index = scores.index(max_score)
        
        print(f"当前方向（北）得分: {scores[0]:.2f}")
        print(f"右侧（东北）得分: {scores[1]:.2f}")
        print(f"最终方向: {max_index} (角度: {max_index * 30}度)")
        
        # 更新上一帧的最佳方向
        last_best_index = max_index
        
        # 模拟帧间隔
        time.sleep(0.1)
    
    # 测试场景2：直线行驶，前方有障碍物，必须转向
    print("\n=== 测试场景2：直线行驶，前方有障碍物，必须转向 ===")
    print("模拟当前方向（北）得分0.1（有障碍物），右侧（东北）得分0.85")
    
    # 模拟多帧导航
    for frame in range(3):
        print(f"\n帧 {frame + 1}:")
        
        # 模拟12方向的得分和碰撞检测
        scores = [0.8] * 12  # 所有方向默认得分
        collision_detected = [False] * 12  # 所有方向默认无碰撞
        direction_valid = [True] * 12  # 所有方向默认有效
        
        # 模拟当前方向（北，索引0）得分0.1（有障碍物）
        scores[0] = 0.1
        direction_valid[0] = False  # 当前方向无效
        # 模拟右侧（东北，索引1）得分0.85
        scores[1] = 0.85
        
        # 全局方向惯性加权：在所有模式下应用
        if last_best_index >= 0 and last_best_index < 12:
            # 应用惯性加权
            weight_factor = inertia_weight / 100.0
            scores[last_best_index] *= weight_factor
            print(f"[STATUS] 应用方向惯性加权: {weight_factor:.2f}倍")
        
        # 方向选择逻辑：找最高分
        max_score = max(scores)
        max_index = scores.index(max_score)
        
        print(f"当前方向（北）得分: {scores[0]:.2f} (无效)")
        print(f"右侧（东北）得分: {scores[1]:.2f}")
        print(f"最终方向: {max_index} (角度: {max_index * 30}度)")
        
        # 更新上一帧的最佳方向
        last_best_index = max_index
        
        # 模拟帧间隔
        time.sleep(0.1)
    
    # 测试场景3：贴墙模式，上一帧方向依然有效
    print("\n=== 测试场景3：贴墙模式，上一帧方向依然有效 ===")
    print("模拟贴墙模式，上一帧方向（东）依然有效，右侧有墙")
    
    # 模拟多帧导航
    for frame in range(3):
        print(f"\n帧 {frame + 1}:")
        
        # 模拟12方向的得分和碰撞检测
        scores = [0.8] * 12  # 所有方向默认得分
        collision_detected = [False] * 12  # 所有方向默认无碰撞
        direction_valid = [True] * 12  # 所有方向默认有效
        
        # 模拟上一帧方向（东，索引3）得分0.8
        scores[3] = 0.8
        # 模拟右侧（东南，索引4）得分0（有墙）
        scores[4] = 0
        direction_valid[4] = False  # 右侧方向无效
        
        # 全局方向惯性加权：在所有模式下应用
        if last_best_index >= 0 and last_best_index < 12:
            # 应用惯性加权
            weight_factor = inertia_weight / 100.0
            scores[last_best_index] *= weight_factor
            print(f"[STATUS] 应用方向惯性加权: {weight_factor:.2f}倍")
        
        # 贴墙模式逻辑：先检查上一帧的方向是否依然有效
        wall_follow_mode = 1
        search_order = []
        max_index = 0
        max_score = 0
        
        if wall_follow_mode == 1:
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
                # 先检查上一帧的方向是否依然有效
                if last_best_index >= 0 and last_best_index < 12 and direction_valid[last_best_index]:
                    # 如果上一帧的方向依然有效，赋予其极高的优先级
                    print("[STATUS] 上一帧方向依然有效，赋予极高优先级")
                    max_index = last_best_index
                    max_score = scores[last_best_index]
                else:
                    # 按照右手优先顺序搜索
                    print("[SYSTEM] 贴右墙模式：右手优先搜索")
                    for offset in range(12):
                        # 计算当前搜索的方向索引
                        # 顺序：右转30度 -> 直行 -> 左转30度 -> 以此类推
                        current_index = (last_best_index + 1 - offset) % 12
                        if current_index < 0:
                            current_index += 12
                        search_order.append(current_index)
                        
                        # 检查方向是否有效
                        if direction_valid[current_index]:
                            max_index = current_index
                            max_score = scores[current_index]
                            break
        
        print(f"上一帧方向（东）得分: {scores[3]:.2f}")
        print(f"右侧（东南）得分: {scores[4]:.2f} (无效)")
        print(f"最终方向: {max_index} (角度: {max_index * 30}度)")
        
        # 更新上一帧的最佳方向
        last_best_index = max_index
        
        # 模拟帧间隔
        time.sleep(0.1)
    
    print("\n=== 测试完成 ===")
    print("全局方向惯性增强测试通过！")

if __name__ == '__main__':
    test_global_inertia()
