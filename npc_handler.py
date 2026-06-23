import time
import cv2
import numpy as np
import pydirectinput

class NPC_Handler:
    def __init__(self, npc_cfg, api_key, npc_template, tet_template, tele_template):
        """
        初始化 NPC 处理器
        tele_template 对应 main.py 传入的 target2_template
        """
        self.npc_cfg = npc_cfg
        self.api_key = api_key
        self.npc_template = npc_template
        self.tet_template = tet_template
        self.tele_template = tele_template

    def find_and_click(self, sct, template, label, threshold=0.8):
        """通用视觉识别点击函数"""
        if template is None:
            return False
        
        # 截取全屏并转换颜色空间
        img = np.array(sct.grab(sct.monitors[1]))
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        # 模板匹配
        res = cv2.matchTemplate(img_bgr, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        
        if max_val > threshold:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            print(f"[{label}] 识别成功 ({max_val:.2f})，执行点击: ({center_x}, {center_y})")
            pydirectinput.click(center_x, center_y)
            return True
        return False

    def execute_npc_sequence(self, sct):
        """执行 NPC 交互序列：识别 -> 补刀 -> 转场"""
        print("[NPC] 启动自动交互流程...")
        # 给游戏渲染 NPC.png 留出时间
        print("[NPC] 等待 1 秒让游戏渲染 UI...")
        time.sleep(1.0)

        # --- 阶段 1: 3 秒循环寻找 NPC ---
        npc_found = False
        start_time = time.time()
        timeout = 3.0  # 3秒超时
        
        print(f"[NPC] 开始寻找 NPC，将在 {timeout} 秒内持续搜索")
        
        while time.time() - start_time < timeout:
            # 截取全屏并转换颜色空间
            img = np.array(sct.grab(sct.monitors[1]))
            img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            # 模板匹配
            if self.npc_template is not None:
                res = cv2.matchTemplate(img_bgr, self.npc_template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(res)
                print(f"[NPC_DEBUG] 寻找NPC中，当前最大匹配度: {max_val:.2f}")
                
                # 匹配度阈值
                threshold = 0.8
                if max_val > threshold:
                    h, w = self.npc_template.shape[:2]
                    center_x = max_loc[0] + w // 2
                    center_y = max_loc[1] + h // 2
                    print(f"[NPC] 识别成功 ({max_val:.2f})，执行点击: ({center_x}, {center_y})")
                    pydirectinput.click(center_x, center_y)
                    npc_found = True
                    break
            
            # 短暂等待后继续搜索
            time.sleep(0.5)
        
        if npc_found:
            print("[NPC] 阶段 1: 已点击 NPC 图标，等待 UI 弹出...")
            time.sleep(1.5)  # 给对话框弹出的时间
        else:
            print("[NPC] 阶段 1: 未发现 NPC 脸部图标，直接进入补刀步骤")

        # --- 阶段 2: 固定坐标补刀 ---
        # 确保即使没点到 NPC 也能触发对话
        print("[NPC] 阶段 2: 执行固定位置补刀点击")
        pydirectinput.click(830, 750)
        time.sleep(0.2)
        pydirectinput.click(1150, 1150)
        time.sleep(6.0)  # 等待传送门生成

        # --- 阶段 3: 视觉转场 (解决往返跑的关键) ---
        # 只有点到了传送门图标，才算真正交互完成
        print("[NPC] 阶段 3: 启动扫描，寻找 target2 转场图标...")
        start_time = time.time()
        timeout = 20  # 20秒超时
        
        while time.time() - start_time < timeout:
            # 1. 检查是否出现中断图标 tet.png
            if self.find_and_click(sct, self.tet_template, "TET"):
                print("[NPC] 识别到中断信号，提前结束")
                return True
                
            # 2. 检查并点击传送门 target2.png
            if self.find_and_click(sct, self.tele_template, "TELE/TARGET2"):
                print("[NPC] 成功点击转场图标，准备进入下一场景")
                time.sleep(2)  # 等待过图加载
                return True
            
            time.sleep(0.5)  # 降低 CPU 占用

        print("[NPC] 警告：阶段 3 扫描超时，未发现转场目标")
        return True

    def reset(self):
        """重置状态（保留接口供 main.py 调用）"""
        pass
