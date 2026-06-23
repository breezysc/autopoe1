import requests
import base64
import json
import time
import pydirectinput
import keyboard

# 1. 填入阿里的 API Key
API_KEY = "sk-e7fd8fabc0a14dfbaf044c0c5b4b142b"
# 2. 图片路径
IMAGE_PATH = r"d:/trae/test.jpg"
# 3. 词缀注册表路径
AFFIX_REGISTRY_PATH = r"d:/trae/词缀注册表.json"
# 4. 优先级设置路径
PRIORITY_SETTINGS_PATH = r"d:/trae/优先级设置.json"
# 5. 未知词缀保存路径
UNKNOWN_AFFIX_PATH = r"d:/trae/未知词缀.txt"

# 全局变量
affix_db = {}  # 词缀数据库
priority_settings = {}  # 优先级配置

# 自动执行相关变量
auto_mode = False  # 自动模式开关，默认关闭
last_affix = None  # 上一次识别的词缀
consecutive_count = 0  # 连续识别同一词缀的次数
COOLDOWN_TIME = 2  # 点击后冷却时间（秒）
CLICK_OFFSET = (0, 0)  # 点击偏移量（相对于当前鼠标位置）

# 加载词缀注册表
def load_affix_registry():
    global affix_db
    try:
        with open(AFFIX_REGISTRY_PATH, "r", encoding="utf-8") as f:
            affix_db = json.load(f)
        print(f"成功加载词缀注册表，共 {len(affix_db)} 个词缀")
    except Exception as e:
        print(f"加载词缀注册表失败: {e}")
        affix_db = {}

# 加载优先级设置
def load_priority_settings():
    global priority_settings
    try:
        with open(PRIORITY_SETTINGS_PATH, "r", encoding="utf-8") as f:
            settings = json.load(f)
            priority_settings = settings.get("图片配置", {})
        print(f"成功加载优先级设置，共 {len(priority_settings)} 个词缀")
    except Exception as e:
        print(f"加载优先级设置失败: {e}")
        priority_settings = {}

# 模糊匹配词缀
def match_affix(clean_res):
    """模糊匹配词缀，返回匹配结果、变种属性、优先级和高危词缀状态"""
    if not clean_res:
        return None, None, None, None, None
    
    # 首先尝试匹配词缀注册表
    for key, value in affix_db.items():
        # 清理键名（移除.webp后缀）
        clean_key = key.split('.')[0]
        # 双向包含判断，容错OCR识别错误
        if clean_key in clean_res or clean_res in clean_key:
            variant = value.get('变种', '真')
            # 同时检查优先级设置
            priority_info = None
            high_risk = None
            priority = None
            
            for p_key, p_value in priority_settings.items():
                p_clean_key = p_key.split('.')[0]
                if p_clean_key in clean_res or clean_res in p_clean_key:
                    priority_info = p_key
                    high_risk = p_value.get('高危词缀', '假')
                    priority = p_value.get('优先级', 0)
                    break
            
            return key, variant, priority_info, high_risk, priority
    
    # 如果词缀注册表中没有匹配，尝试直接匹配优先级设置
    for p_key, p_value in priority_settings.items():
        p_clean_key = p_key.split('.')[0]
        if p_clean_key in clean_res or clean_res in p_clean_key:
            priority_info = p_key
            high_risk = p_value.get('高危词缀', '假')
            priority = p_value.get('优先级', 0)
            return None, None, priority_info, high_risk, priority
    
    return None, None, None, None, None

# 保存未知词缀
def save_unknown_affix(affix_name):
    try:
        with open(UNKNOWN_AFFIX_PATH, "a", encoding="utf-8") as f:
            f.write(affix_name + "\n")
        print(f"未知词缀已保存: {affix_name}")
    except Exception as e:
        print(f"保存未知词缀失败: {e}")

# 处理键盘输入，切换自动模式
def check_keyboard():
    global auto_mode
    if keyboard.is_pressed('z'):
        auto_mode = not auto_mode
        status = "开启" if auto_mode else "关闭"
        print(f"\033[93m" + f"自动模式已{status}" + "\033[0m")
        # 防止重复触发
        time.sleep(0.5)

def aliyun_ocr():
    # 读取图片转 Base64
    with open(IMAGE_PATH, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode('utf-8')

    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "qwen-vl-ocr", # 必须是这个模型
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"image": f"data:image/jpeg;base64,{img_base64}"},
                        # 提示词一针见血：要求逐字还原，不准总结
                        {"text": "请精确识别图中的所有中文文字，保持原有的排版和换行，不要输出任何解释，直接给文字内容。"}
                    ]
                }
            ]
        }
    }

    print("正在请求阿里服务器...")
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        res_data = response.json()
        # 提取文字结果
        text_result = res_data['output']['choices'][0]['message']['content'][0]['text']
        
        # 清理识别结果
        clean_res = text_result.strip().replace(" ", "").replace("\n", "")
        
        with open(r"d:/trae/result.txt", "w", encoding="utf-8") as f:
            f.write(text_result)
        print("识别成功！")
        print("识别结果：")
        print("=" * 50)
        print(text_result)
        print("=" * 50)
        print("清理后的结果：" + clean_res)
        
        # 匹配词缀
        matched_key, variant, priority_info, high_risk, priority = match_affix(clean_res)
        
        # 处理连续识别判定
        global last_affix, consecutive_count
        current_affix = priority_info or matched_key
        
        if current_affix:
            if current_affix == last_affix:
                consecutive_count += 1
            else:
                consecutive_count = 1
                last_affix = current_affix
            print(f"连续识别次数: {consecutive_count}")
        else:
            consecutive_count = 0
            last_affix = None
        
        if priority_info:
            # 显示优先级
            print(f"优先级: {priority}")
            
            # 显示高危词缀状态
            if high_risk == "假":
                print("\033[92m" + "✅  安全：准备点击" + "\033[0m")
            elif high_risk == "真":
                print("\033[91m" + "⚠️  危险：禁止点击" + "\033[0m")
            
            # 显示词缀信息
            if matched_key:
                print(f"匹配到词缀: {matched_key}，变种: {variant}")
            print(f"优先级设置: {priority_info}，高危词缀: {high_risk}")
            
            # 自动执行逻辑
            if auto_mode and high_risk == "假" and consecutive_count >= 3:
                print("\033[92m" + "[自动执行] 触发点击..." + "\033[0m")
                # 获取当前鼠标位置
                current_x, current_y = pydirectinput.position()
                # 计算点击位置
                click_x = current_x + CLICK_OFFSET[0]
                click_y = current_y + CLICK_OFFSET[1]
                # 平滑移动鼠标
                pydirectinput.moveTo(click_x, click_y, duration=0.5)
                # 执行点击
                pydirectinput.click()
                print(f"[自动执行] 已点击位置: ({click_x}, {click_y})")
                # 冷却保护
                print(f"[自动执行] 冷却中... {COOLDOWN_TIME}秒")
                time.sleep(COOLDOWN_TIME)
                # 重置连续计数
                consecutive_count = 0
            else:
                # 性能优化：匹配成功后停止识别0.5秒
                print("\n性能优化：暂停0.5秒...")
                time.sleep(0.5)
        elif matched_key:
            # 只匹配到词缀注册表，没有匹配到优先级设置
            if variant == "假":
                print("\033[91m" + "红色警告：假词缀，跳过！" + "\033[0m")
            elif variant == "真":
                print("\033[92m" + "绿色提示：真词缀，准备点击" + "\033[0m")
            print(f"匹配到词缀: {matched_key}，变种: {variant}")
            
            # 性能优化：匹配成功后停止识别0.5秒
            print("\n性能优化：暂停0.5秒...")
            time.sleep(0.5)
        else:
            print("\033[93m" + "未知词缀" + "\033[0m")
            save_unknown_affix(clean_res)
        
        print("结果已保存到 d:/trae/result.txt")
    else:
        print(f"失败，错误码: {response.status_code}")
        print(response.text)

def main():
    # 加载词缀注册表
    load_affix_registry()
    # 加载优先级设置
    load_priority_settings()
    
    print("按 'Z' 键切换自动模式")
    print(f"当前自动模式: {'开启' if auto_mode else '关闭'}")
    
    # 持续运行
    while True:
        try:
            # 检查键盘输入
            check_keyboard()
            
            aliyun_ocr()
            # 每次识别后等待1秒
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n程序已停止")
            break
        except Exception as e:
            print(f"错误: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()