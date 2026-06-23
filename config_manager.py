import os
import json
import cv2

# 配置字典
NAV_CFG = {
    'map_x_from_right': 6,
    'map_y_from_top': 40,
    'map_size': 380,
    'threshold': 100,
    'scan_radius': 44,
    'sensitivity': 0.5,
    'click_distance': 250,
    'click_delay': 200,
    'wall_thickness': 3,
    'wall_follow_mode': 1,
    'safe_padding': 15,
    'inertia_weight': 150,
    'search_radius': 100,
    'blind_zone_threshold': 0.1,
    'blind_zone_distance': 30,
    'wall_follow_threshold': 0.4,
    'wall_nearby_distance': 30,
    'min_obstacle_width': 50,
    'direction_lock_threshold': 0.5,
    'direction_lock_time': 2.0,
    'blind_zone_inertia_weight': 0.8,
    'blind_zone_inertia_decay': 0.95,
    'wall_distance_maintain': 20,
    'wall_anchor_distance': 40,
    'tangent_smoothing_factor': 0.3,
    'global_inertia_weight': 0.8,
    'global_inertia_decay': 0.9,
    'coordinate_sync_threshold': 0.6,
    'coordinate_sync_offset': 5,
    'target_found_angle_range': 30,
    'priority_lock_time': 1.0,
    'priority_lock_distance': 50,
    'obstacle_avoidance_distance': 40,
    'dynamic_obstacle_threshold': 0.6,
    'dynamic_obstacle_debounce': 0.5,
    'click_radius': 100,
    'character_height_offset': 10,
    'icon_detection_threshold': 0.6,
    'icon_stop_distance': 20,
    'pole_brake_distance': 30,
    'dynamic_click_distance': 50
}

RITUAL_CFG = {
    'ritual_points_v1': [],
    'start_button_offset_v1': [50, 25],
    'ritual_points_v2': [],
    'start_button_offset_v2': [50, 25],
    'priority': ['通货', '地图', '幸运'],
    'word2_x': 100,
    'word2_y': 100,
    'ocr_dx': 0,
    'ocr_dy': 0,
    'ocr_w': 300,
    'ocr_h': 100
}

NPC_CFG = {
    'tet_distance': 150,
    'tet_threshold': 0.75,
    'tet_offset_x': 200,
    'tet_offset_y': 100,
    'npc_click_x': 830,
    'npc_click_y': 750,
    'portal_search_duration': 10,
    'ocr_timeout': 5,
    'portal_search_interval': 1,
    'portal_ocr_roi_top': 400,
    'portal_ocr_roi_left': 800,
    'portal_ocr_roi_width': 400,
    'portal_ocr_roi_height': 200,
    'tele_offset_distance': 45
}

# 全局变量
affix_db = {}
priority_settings = {}
start_template = None
round_templates = []
target2_template = None
tet_template = None
anchor_templates = []
anchor_filenames = []
API_KEY = "sk-12345678901234567890123456789012345678901234567"

class ConfigManager:
    def __init__(self):
        self.NAV_CFG = NAV_CFG
        self.RITUAL_CFG = RITUAL_CFG
        self.NPC_CFG = NPC_CFG
        self.affix_db = affix_db
        self.priority_settings = priority_settings
        self.start_template = start_template
        self.round_templates = round_templates
        self.ritual_template = None
        self.target2_template = target2_template
        self.tet_template = tet_template
        self.npc_template = None
        self.tele_template = None
        self.hideout_template = None
        self.anchor_templates = anchor_templates
        self.anchor_filenames = anchor_filenames
        self.API_KEY = API_KEY
    
    def load_configs(self):
        """加载配置文件"""
        # 加载导航配置
        if os.path.exists('nav_config.json'):
            try:
                with open('nav_config.json', 'r', encoding='utf-8') as f:
                    nav_config = json.load(f)
                    for key, value in nav_config.items():
                        if key in self.NAV_CFG:
                            self.NAV_CFG[key] = value
                    print("[CONFIG] 成功加载导航配置")
            except Exception as e:
                print(f"[CONFIG] 加载导航配置失败: {e}")
        
        # 加载锚点配置
        if os.path.exists('anchor_config.json'):
            try:
                with open('anchor_config.json', 'r', encoding='utf-8') as f:
                    anchor_config = json.load(f)
                    # 读取新的字段名
                    if 'ritual_points_v1' in anchor_config:
                        self.RITUAL_CFG['ritual_points_v1'] = anchor_config['ritual_points_v1']
                    if 'start_button_offset_v1' in anchor_config:
                        self.RITUAL_CFG['start_button_offset_v1'] = anchor_config['start_button_offset_v1']
                    if 'ritual_points_v2' in anchor_config:
                        self.RITUAL_CFG['ritual_points_v2'] = anchor_config['ritual_points_v2']
                    if 'start_button_offset_v2' in anchor_config:
                        self.RITUAL_CFG['start_button_offset_v2'] = anchor_config['start_button_offset_v2']
                    if 'priority' in anchor_config:
                        self.RITUAL_CFG['priority'] = anchor_config['priority']
                    print("[CONFIG] 成功加载锚点配置")
            except Exception as e:
                print(f"[CONFIG] 加载锚点配置失败: {e}")
        
        # 加载API密钥
        if os.path.exists('api_key.txt'):
            try:
                with open('api_key.txt', 'r', encoding='utf-8') as f:
                    self.API_KEY = f.read().strip()
                print("[CONFIG] 成功加载API密钥")
            except Exception as e:
                print(f"[CONFIG] 加载API密钥失败: {e}")
    
    def load_altar_templates(self):
        """加载祭坛模板"""
        # 加载试炼祭坛模板 (ritual_icon.png)
        ritual_path = os.path.join(os.getcwd(), 'ritual_icon.png')
        print(f"[CONFIG] 正在加载试炼祭坛模板: {ritual_path}")
        if os.path.exists(ritual_path):
            try:
                self.ritual_template = cv2.imread(ritual_path, cv2.IMREAD_COLOR)
                if self.ritual_template is not None:
                    print(f"[ALTAR] 成功加载试炼祭坛模板: {ritual_path}")
                else:
                    error_msg = f"[ERROR] 无法加载ritual_icon.png，请检查文件格式: {ritual_path}"
                    print(error_msg)
                    raise Exception(error_msg)
            except Exception as e:
                error_msg = f"[ERROR] 加载试炼祭坛模板失败: {e}"
                print(error_msg)
                raise
        else:
            error_msg = f"[ERROR] ritual_icon.png 不存在，请确保试炼祭坛模板文件在当前目录: {ritual_path}"
            print(error_msg)
            raise Exception(error_msg)
        
        # 加载第二个目标模板 (target2.png)
        target2_path = os.path.join(os.getcwd(), 'target2.png')
        print(f"[CONFIG] 正在加载第二个目标模板: {target2_path}")
        if os.path.exists(target2_path):
            try:
                self.target2_template = cv2.imread(target2_path, cv2.IMREAD_COLOR)
                if self.target2_template is not None:
                    print(f"[ALTAR] 成功加载第二个目标模板: {target2_path}")
                else:
                    error_msg = f"[ERROR] 无法加载target2.png，请检查文件格式: {target2_path}"
                    print(error_msg)
                    raise Exception(error_msg)
            except Exception as e:
                error_msg = f"[ERROR] 加载第二个目标模板失败: {e}"
                print(error_msg)
                raise
        else:
            error_msg = f"[ERROR] target2.png 不存在，请确保第二个目标模板文件在当前目录: {target2_path}"
            print(error_msg)
            raise Exception(error_msg)
    
    def load_ritual_resources(self):
        """加载仪式资源"""
        # 加载词缀注册表
        if os.path.exists('词缀注册表.json'):
            try:
                with open('词缀注册表.json', 'r', encoding='utf-8') as f:
                    self.affix_db = json.load(f)
                print(f"成功加载词缀注册表，共 {len(self.affix_db)} 个词缀")
            except Exception as e:
                print(f"加载词缀注册表失败: {e}")
        
        # 加载优先级设置
        if os.path.exists('优先级设置.json'):
            try:
                with open('优先级设置.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.priority_settings = settings.get("图片配置", {})
                print(f"成功加载优先级设置，共 {len(self.priority_settings)} 个词缀")
            except Exception as e:
                print(f"加载优先级设置失败: {e}")
    
    def load_npc_resources(self):
        """加载NPC资源"""
        # 加载NPC.png模板
        npc_path = 'NPC.png'
        if os.path.exists(npc_path):
            try:
                self.npc_template = cv2.imread(npc_path, cv2.IMREAD_COLOR)
                if self.npc_template is not None:
                    print(f"[NPC] 加载NPC模板: {npc_path}")
                    print(f"NPC.png 模板尺寸: {self.npc_template.shape[1]}x{self.npc_template.shape[0]}")
                else:
                    print(f"[NPC] 无法加载NPC.png，请检查文件格式")
            except Exception as e:
                print(f"[NPC] 加载NPC模板失败: {e}")
        else:
            print(f"[WARNING] NPC.png 不存在")
        
        # 加载tet.png中断检测模板
        tet_path = 'tet.png'
        if os.path.exists(tet_path):
            try:
                self.tet_template = cv2.imread(tet_path, cv2.IMREAD_COLOR)
                if self.tet_template is not None:
                    print(f"[NPC] 加载中断检测模板: {tet_path}")
            except Exception as e:
                print(f"[NPC] 加载中断检测模板失败: {e}")
        else:
            print(f"[WARNING] tet.png 不存在")
        
        # 加载hideout_anchor.png藏身处模板
        hideout_path = 'hideout_anchor.png'
        if os.path.exists(hideout_path):
            try:
                self.hideout_template = cv2.imread(hideout_path, cv2.IMREAD_COLOR)
                if self.hideout_template is not None:
                    print(f"[HIDEOUT] 加载藏身处模板: {hideout_path}")
                    print(f"hideout_anchor.png 模板尺寸: {self.hideout_template.shape[1]}x{self.hideout_template.shape[0]}")
                else:
                    print(f"[HIDEOUT] 无法加载hideout_anchor.png，请检查文件格式")
            except Exception as e:
                print(f"[HIDEOUT] 加载藏身处模板失败: {e}")
        else:
            print(f"[WARNING] hideout_anchor.png 不存在")
    
    def load_affix_resources(self):
        """加载锚点模板"""
        # 加载start.png
        start_png_path = os.path.join(os.getcwd(), 'start.png')
        if os.path.exists(start_png_path):
            try:
                self.start_template = cv2.imread(start_png_path, cv2.IMREAD_COLOR)
                if self.start_template is not None:
                    print(f"成功加载第一轮锚点模板: {start_png_path}")
                    print(f"start.png 模板尺寸: {self.start_template.shape[1]}x{self.start_template.shape[0]}")
                else:
                    raise Exception(f"无法加载start.png，请检查文件格式")
            except Exception as e:
                print(f"加载锚点模板 {start_png_path} 失败: {e}")
                raise
        else:
            error_msg = f"[ERROR] start.png 不存在，请确保开始按钮模板文件在当前目录: {start_png_path}"
            print(error_msg)
            raise Exception(error_msg)
        
        # 加载所有ritual_anchor开头的图片
        self.round_templates = []
        self.anchor_filenames = []
        current_dir = os.getcwd()
        print(f"[CONFIG] 正在 {current_dir} 目录中查找ritual_anchor开头的图片")
        found_ritual_anchors = False
        for file in os.listdir('.'):
            if file.startswith('ritual_anchor') and file.endswith('.png'):
                found_ritual_anchors = True
                file_path = os.path.join(current_dir, file)
                try:
                    template = cv2.imread(file_path, cv2.IMREAD_COLOR)
                    if template is not None:
                        self.round_templates.append(template)
                        print(f"成功加载次轮锚点模板: {file_path}")
                        print(f"{file} 模板尺寸: {template.shape[1]}x{template.shape[0]}")
                    else:
                        print(f"警告: 无法加载 {file}，请检查文件格式")
                except Exception as e:
                    print(f"加载锚点模板 {file_path} 失败: {e}")
        
        if not found_ritual_anchors:
            print("[WARNING] 未找到任何ritual_anchor开头的图片")
        
        # 准备锚点模板列表：第一个是start_template，后面是round_templates
        self.anchor_templates = []
        self.anchor_filenames = []
        if self.start_template is not None:
            self.anchor_templates.append(self.start_template)
            self.anchor_filenames.append('start.png')
        for i, template in enumerate(self.round_templates):
            self.anchor_templates.append(template)
            # 查找对应的文件名
            for file in os.listdir('.'):
                if file.startswith('ritual_anchor') and file.endswith('.png'):
                    file_path = os.path.join(os.getcwd(), file)
                    temp_template = cv2.imread(file_path, cv2.IMREAD_COLOR)
                    if temp_template is not None and temp_template.shape == template.shape:
                        self.anchor_filenames.append(file)
                        break
        
        # 检查锚点数量
        total_anchors = len(self.anchor_templates)
        print(f"[CONFIG] 总共加载了 {total_anchors} 个锚点模板")
        print(f"[CONFIG] 锚点文件名列表: {self.anchor_filenames}")
        if total_anchors < 4:
            print(f"[WARNING] 加载到的锚点数量少于 4 张，当前只有 {total_anchors} 张")
    
    def load_all(self):
        """加载所有配置和资源"""
        self.load_configs()
        # 加载保存的配置
        self.load_saved_configs()
        self.load_affix_resources()
        self.load_altar_templates()
        self.load_ritual_resources()
        self.load_npc_resources()
    
    def load_saved_configs(self):
        """加载保存的配置"""
        config_file = 'config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    # 加载保存的导航配置
                    if 'NAV_CFG' in saved_config:
                        self.NAV_CFG.update(saved_config['NAV_CFG'])
                        print("[CONFIG] 成功加载保存的导航配置")
                    # 加载保存的仪式配置
                    if 'RITUAL_CFG' in saved_config:
                        self.RITUAL_CFG.update(saved_config['RITUAL_CFG'])
                        print("[CONFIG] 成功加载保存的仪式配置")
            except Exception as e:
                print(f"[CONFIG] 加载保存的配置失败: {e}")
    
    def save_configs(self):
        """保存配置到JSON文件"""
        config_file = 'config.json'
        try:
            saved_config = {
                'NAV_CFG': self.NAV_CFG,
                'RITUAL_CFG': self.RITUAL_CFG
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(saved_config, f, ensure_ascii=False, indent=2)
            print("[CONFIG] 配置已保存到 config.json")
        except Exception as e:
            print(f"[CONFIG] 保存配置失败: {e}")

# 创建全局配置管理器实例
config_manager = ConfigManager()