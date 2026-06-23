import numpy as np
import time

# 核心导航算法
def navigation_core():
    # 模拟参数
    map_size = 200
    scan_radius = 50
    sensitivity = 0.5
    last_best_index = 0
    
    # 模拟二值化图像（0=黑色迷雾，255=白色墙壁/路径）
    # 创建一个简单的模拟场景：中心是已探索区域，周围是迷雾，右上角有一个墙壁
    binary = np.zeros((map_size, map_size), dtype=np.uint8)
    center_x = map_size // 2
    center_y = map_size // 2
    
    # 创建已探索区域
    for y in range(center_y - 30, center_y + 30):
        for x in range(center_x - 30, center_x + 30):
            if 0 <= x < map_size and 0 <= y < map_size:
                binary[y, x] = 255
    
    # 在右上角添加一个墙壁
    for y in range(center_y - 20, center_y + 20):
        for x in range(center_x + 30, center_x + 50):
            if 0 <= x < map_size and 0 <= y < map_size:
                binary[y, x] = 255
    
    print("=== PoE 导航算法核心测试 ===")
    print(f"地图大小: {map_size}x{map_size}")
    print(f"中心坐标: ({center_x}, {center_y})")
    print(f"扫描半径: {scan_radius}")
    print(f"灵敏度: {sensitivity}")
    print("\n模拟场景: 中心已探索，右上角有墙壁")
    
    # 测试多帧导航
    for frame in range(10):
        print(f"\n=== 帧 {frame + 1} ===")
        
        # 12方向扇形采样
        scores = []
        collision_detected = [False] * 12
        
        for i in range(12):
            angle = i * 30
            
            # 模拟扇形得分计算
            # 这里使用基于角度的得分，模拟不同方向的迷雾密度
            if i in [1, 2]:  # 30度和60度（右上角）
                score = 0.3  # 得分较低，因为有墙壁
            elif i in [4, 5, 6, 7]:  # 120-210度（下方）
                score = 0.8  # 得分较高，模拟更多迷雾
            else:
                score = 0.6  # 其他方向
            
            # 射线碰撞检测
            collision = False
            rad = np.deg2rad(angle)
            
            # 等距选取3个检测点（0.3R, 0.6R, 0.9R）
            for ratio in [0.3, 0.6, 0.9]:
                distance = int(scan_radius * ratio)
                check_x = int(center_x + distance * np.cos(rad))
                check_y = int(center_y + distance * np.sin(rad))
                
                # 确保检测点在图像范围内
                if 0 <= check_x < map_size and 0 <= check_y < map_size:
                    # 检查是否为白色像素（墙壁）
                    if binary[check_y, check_x] == 255:
                        collision = True
                        break
            
            # 如果检测到碰撞，将得分设为0
            if collision:
                score = 0
                collision_detected[i] = True
            
            scores.append(score)
            print(f"方向 {i} (角度 {angle}度): 得分 = {score:.2f}, 碰撞 = {collision}")
        
        # 方向惯性逻辑：给上一帧的最佳方向增加权重
        if last_best_index >= 0 and last_best_index < 12:
            original_score = scores[last_best_index]
            scores[last_best_index] *= 1.15  # 增加15%的权重
            print(f"给方向 {last_best_index} 增加15%权重，从 {original_score:.2f} 变为 {scores[last_best_index]:.2f}")
        
        # 找到得分最高的方向
        max_score = max(scores)
        max_index = scores.index(max_score)
        
        print(f"最佳方向: {max_index} (得分: {max_score:.2f})")
        
        # 更新上一帧的最佳方向
        last_best_index = max_index
        
        # 模拟帧间隔
        time.sleep(0.3)

if __name__ == '__main__':
    navigation_core()
