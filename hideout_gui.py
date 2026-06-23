import cv2
import numpy as np
import json
import os
import ctypes

# 强制 DPI 感知
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

def get_screen_resolution():
    """动态获取屏幕分辨率"""
    try:
        user32 = ctypes.windll.user32
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        return width, height
    except:
        return 2560, 1600

class HideoutGUI:
    def __init__(self, config_file="hideout_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.capturing_coordinate = None
        self.window_name = "藏身处配置中心"
        self.preview_img = None
        
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[GUI] 加载配置失败: {e}")
        return self.get_default_config()
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            "hotkeys": {"inventory_dump": "Q", "open_map_sequence": "W"},
            "coordinates": {
                "stash": [0, 0], "map_device": [0, 0], "start_map_btn": [0, 0],
                "npc_lily": [0, 0], "portal": [0, 0]
            },
            "protected_slots": [[0, 0], [1, 0], [2, 0], [3, 0]],
            "resource_paths": {
                "stash_icon": "assets/stash.png", "portal_icon": "assets/portal.png",
                "map_device_icon": "assets/map_device.png", "lily_icon": "assets/lily.png"
            }
        }
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print(f"[GUI] 配置已保存到 {self.config_file}")
            return True
        except Exception as e:
            print(f"[GUI] 保存配置失败: {e}")
            return False
    
    def set_coordinate(self, name, x, y):
        """设置坐标"""
        if name in self.config["coordinates"]:
            self.config["coordinates"][name] = [x, y]
            print(f"[GUI] 设置 {name} 坐标: ({x}, {y})")
            self.save_config()
    
    def set_hotkey(self, action, key):
        """设置快捷键"""
        if action in self.config["hotkeys"]:
            self.config["hotkeys"][action] = key
            print(f"[GUI] 设置 {action} 快捷键: {key}")
            self.save_config()
    
    def start_capture(self, coordinate_name):
        """开始捕获坐标"""
        self.capturing_coordinate = coordinate_name
        print(f"[GUI] 请点击 {coordinate_name} 位置，按 ESC 取消")
    
    def mouse_callback(self, event, x, y, flags, param):
        """鼠标回调函数"""
        if event == cv2.EVENT_LBUTTONDOWN and self.capturing_coordinate:
            self.set_coordinate(self.capturing_coordinate, x, y)
            self.capturing_coordinate = None
    
    def draw_gui(self):
        """绘制 GUI 界面"""
        screen_width, screen_height = get_screen_resolution()
        img = np.zeros((600, 800, 3), dtype=np.uint8)
        
        # 标题
        cv2.putText(img, "藏身处配置中心", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        # 坐标配置
        y_pos = 70
        coord_names = ["stash", "map_device", "start_map_btn", "npc_lily", "portal"]
        coord_labels = ["仓库", "制图仪", "开图按钮", "NPC 莉莉", "传送门"]
        
        for name, label in zip(coord_names, coord_labels):
            coord = self.config["coordinates"].get(name, [0, 0])
            cv2.putText(img, f"{label}: {coord}", (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(img, f"[C] 捕获 {label}", (400, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            y_pos += 40
        
        # 快捷键配置
        y_pos += 20
        cv2.putText(img, "快捷键配置:", (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        y_pos += 40
        
        hotkey_actions = ["inventory_dump", "open_map_sequence"]
        hotkey_labels = ["存包", "开图序列"]
        
        for action, label in zip(hotkey_actions, hotkey_labels):
            key = self.config["hotkeys"].get(action, "")
            cv2.putText(img, f"{label}: {key}", (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(img, f"[K] 设置 {label}", (400, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            y_pos += 40
        
        # 操作提示
        y_pos += 20
        cv2.putText(img, "操作提示:", (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        y_pos += 40
        cv2.putText(img, "1-5: 捕获对应坐标  Q/W: 设置对应快捷键  ESC: 退出", (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # 捕获状态提示
        if self.capturing_coordinate:
            cv2.putText(img, f"正在捕获: {self.capturing_coordinate}", (20, 580), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        return img
    
    def run(self):
        """运行 GUI"""
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        print("[GUI] 藏身处配置中心已启动")
        print("[GUI] 操作提示: 1-5 捕获坐标, Q/W 设置快捷键, ESC 退出")
        
        coord_names = ["stash", "map_device", "start_map_btn", "npc_lily", "portal"]
        hotkey_actions = ["inventory_dump", "open_map_sequence"]
        
        while True:
            img = self.draw_gui()
            cv2.imshow(self.window_name, img)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC
                break
            
            # 坐标捕获快捷键 (1-5)
            if ord('1') <= key <= ord('5'):
                idx = key - ord('1')
                if idx < len(coord_names):
                    self.start_capture(coord_names[idx])
            
            # 快捷键设置 (Q, W)
            if key == ord('q') or key == ord('Q'):
                self.set_hotkey(hotkey_actions[0], 'Q')
            elif key == ord('w') or key == ord('W'):
                self.set_hotkey(hotkey_actions[1], 'W')
            
            # 保存快捷键
            if key == ord('s') or key == ord('S'):
                self.save_config()
        
        cv2.destroyAllWindows()
        print("[GUI] 藏身处配置中心已关闭")

if __name__ == "__main__":
    gui = HideoutGUI()
    gui.run()
