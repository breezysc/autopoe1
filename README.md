# AutoPoE1 - PoE 自动化辅助系统

## 项目简介
AutoPoE1 是一个基于 Python 的 **Path of Exile (PoE)** 游戏自动化辅助工具。它利用计算机视觉（CV）和阿里云 DashScope 大语言模型，实现了在游戏中的智能导航、物品（神谕石）自动鉴定与处理、NPC 自动交互以及藏身处（Hideout）自动管理等功能。

## 核心特性
1.  **智能导航 (Auto-Navigation)**
    *   基于 OpenCV 的小地图实时分析。
    *   具备墙壁跟随、避障和惯性导航算法。
2.  **AI 驱动的神谕石处理 (AI-Powered Ritual Handling)**
    *   调用 DashScope 多模态 API 对神谕石进行 OCR 识别。
    *   AI 自动决策词缀（增伤/加法/暴击等），执行使用、重组或出售操作。
3.  **NPC 自动交互 (Auto-NPC Interaction)**
    *   自动识别 NPC 图标并点击对话。
    *   识别传送门图标，自动前往下一场景。
4.  **藏身处管理 (Hideout Management)**
    *   模块化设计，支持一键存包（避开保护区）。
    *   自动取出地图和圣甲虫，并放入制图仪开启。
5.  **状态机架构 (State Machine Architecture)**
    *   清晰的状态管理（地图模式、藏身处模式、交互模式），避免逻辑冲突。

## 技术栈
*   **语言**: Python 3.10+
*   **核心库**:
    *   `opencv-python`: 图像处理与模板匹配
    *   `numpy`: 数值计算
    *   `mss`: 高性能屏幕截图
    *   `pydirectinput`: 模拟键鼠操作
    *   `pynput`: 监听键盘事件
*   **AI API**: 阿里云 DashScope (Multimodal Generation)

## 项目结构
```plaintext
autopoe1/
├── main.py              # 主程序入口，包含主循环和状态机
├── config_manager.py    # 配置管理器，加载 JSON 和图片模板
├── vision_engine.py     # 视觉引擎，封装截图、场景检测和模板匹配
├── ritual_manager.py    # 仪式管理器，调用 AI API 进行词缀识别和决策
├── npc_handler.py       # NPC 处理器，负责与 NPC 的自动交互
├── hideout_manager.py   # 藏身处管理器，协调藏身处内的各种操作
├── stash_controller.py  # 仓库控制器，负责存取物品逻辑
├── map_processor.py     # 地图处理器，负责地图和圣甲虫的取出与放入
├── hideout_gui.py       # 图形化配置界面，用于手动标定坐标
├── navigation_core.py   # 导航核心算法
└── poe_navigation_debugger.py # 导航调试工具
```

## 安装与配置

### 1. 环境要求
*   Windows 操作系统
*   Python 3.10+

### 2. 安装依赖
在项目根目录下执行：
```bash
pip install -r requirements.txt
```
*(如果没有 `requirements.txt`，请手动安装上述技术栈中的库)*

### 3. 配置文件
*   **API Key**: 需要在代码或配置中设置您的 DashScope API Key。
*   **坐标标定**: 首次使用前，建议运行 `python hideout_gui.py` 来手动标定仓库、制图仪等关键位置的坐标。

## 使用说明
1.  **启动程序**: 在终端运行 `python main.py`。
2.  **切换状态**: 程序启动后会自动接管游戏。按 `P` 键可以暂停/继续脚本运行。
3.  **退出程序**: 按 `ESC` 键退出。

## 免责声明
本项目仅供学习和研究使用。使用任何自动化工具可能违反游戏的服务条款，请自行评估风险。
