import time
import json
import os
import ctypes

# 导入各个模块
from stash_controller import StashController
from map_processor import MapProcessor

# 强制 DPI 感知
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

# 状态枚举
STATE_HIDEOUT = "HIDEOUT"
STATE_STASH = "STASH"
STATE_MAP_DEVICE = "MAP_DEVICE"
STATE_WAITING_PORTAL = "WAITING_PORTAL"

class HideoutManager:
    def __init__(self, config_file="hideout_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.state = STATE_HIDEOUT
        self.stash_controller = StashController(config_file)
        self.map_processor = MapProcessor(config_file)
        self.is_initialized = False
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[HIDEOUT] 加载配置失败: {e}")
        return {}
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print(f"[HIDEOUT] 配置已保存")
            return True
        except Exception as e:
            print(f"[HIDEOUT] 保存配置失败: {e}")
            return False
    
    def initialize(self, sct):
        """初始化"""
        if not self.is_initialized:
            print("[HIDEOUT] 初始化藏身处管理器")
            self.map_processor.load_templates()
            self.is_initialized = True
    
    def run_logic(self, sct):
        """执行藏身处逻辑 - 主协调器"""
        self.initialize(sct)
        
        print(f"[HIDEOUT] 当前状态: {self.state}")
        
        if self.state == STATE_HIDEOUT:
            self.handle_hideout_state(sct)
        elif self.state == STATE_STASH:
            self.handle_stash_state(sct)
        elif self.state == STATE_MAP_DEVICE:
            self.handle_map_device_state(sct)
        elif self.state == STATE_WAITING_PORTAL:
            result = self.handle_waiting_portal_state(sct)
            if result == "MAP_MODE":
                return "MAP_MODE"
        
        time.sleep(0.5)
        return None
    
    def handle_hideout_state(self, sct):
        """处理藏身处状态"""
        print("[HIDEOUT] 在藏身处，准备下一步操作")
        
        hotkeys = self.config.get("hotkeys", {})
        
        # 这里可以添加快捷键监听逻辑
        # 例如：按下 Q 键触发存包，按下 W 键触发开图
        
        # 默认先存包，再开图
        print("[HIDEOUT] 切换到仓库状态")
        self.state = STATE_STASH
    
    def handle_stash_state(self, sct):
        """处理仓库状态"""
        print("[HIDEOUT] 处理仓库逻辑")
        
        success = self.stash_controller.dump_inventory(sct)
        
        if success:
            print("[HIDEOUT] 存包完成，切换到制图仪状态")
            self.state = STATE_MAP_DEVICE
        else:
            print("[HIDEOUT] 存包失败，保持在仓库状态")
    
    def handle_map_device_state(self, sct):
        """处理制图仪状态"""
        print("[HIDEOUT] 处理制图仪逻辑")
        
        success = self.map_processor.open_map_sequence(sct, self.stash_controller)
        
        if success:
            print("[HIDEOUT] 开图完成，等待传送门")
            self.state = STATE_WAITING_PORTAL
        else:
            print("[HIDEOUT] 开图失败，回到藏身处状态")
            self.state = STATE_HIDEOUT
    
    def handle_waiting_portal_state(self, sct):
        """等待传送门状态"""
        print("[HIDEOUT] 等待传送门出现")
        
        portal_found, portal_pos = self.map_processor.detect_portal(sct)
        
        if portal_found:
            print(f"[HIDEOUT] 检测到传送门: {portal_pos}")
            return "MAP_MODE"
        
        return None
    
    def reset(self):
        """重置状态"""
        self.state = STATE_HIDEOUT
        self.is_initialized = False
        print("[HIDEOUT] 藏身处模式重置")

# 创建全局藏身处管理器实例
hideout_manager = HideoutManager()
