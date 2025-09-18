# -*- coding: utf-8 -*-
"""
Dota聊天机器人配置系统 - 整合版
"""
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Optional
import pyautogui
from PIL import Image, ImageTk

class Config:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.default_config = {
            # API配置
            "api": {
                "deepseek_api_key": "your_api_key_here",
                "api_base_url": "https://api.deepseek.com/v1/chat/completions",
                "model": "deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 200,
                "timeout": 10
            },
            
            # OCR配置
            "ocr": {
                "tesseract_path": r"D:\Tesseract-OCR\tesseract.exe",
                "tessdata_path": r"D:\Tesseract-OCR\tessdata",
                "language": "eng+chi_sim",
                "detection_interval": 3.0,  # 聊天/击杀采集间隔（秒）
                "engine": "tesseract",  # OCR引擎选择: tesseract, easyocr, paddleocr
                "gray_saturation_threshold": 80,
                "gray_value_min": 30,
                "portrait_roi_ratio": 0.8,
                "gray_fraction_threshold": 0.10,
                "gray_fraction_delta": 0.06,
                "chat_min_chars": 2
            },
            
            # 检测区域配置
            "detection_areas": {
                "kill_detection_area": {
                    "x": 100,
                    "y": 100,
                    "width": 200,
                    "height": 50,
                    "enabled": True
                },
                "chat_detection_area": {
                    "x": 100,
                    "y": 200,
                    "width": 300,
                    "height": 100,
                    "enabled": True
                }
            },
            
            # 冷却时间配置
            "cooldowns": {
                "kill_cooldown": 5.0,  # 击杀检测冷却时间（秒）
                "chat_cooldown": 3.0,  # 对话检测冷却时间（秒）
                "encouragement_cooldown": 10.0,  # 鼓励语冷却时间（秒）
                "min_chat_interval": 2.0  # 最短聊天间隔（秒）
            },
            
            # 功能开关
            "features": {
                "encouragement_enabled": True,
                "auto_response_enabled": True,
                "kill_detection_enabled": True,
                "chat_detection_enabled": True,
                "check_kill_after_chat": True,  # 聊天后检测击杀
                "enable_chat_interaction": True,  # 启用击杀/死亡后的聊天交流
                "debug_mode": False
            },
            
            # 游戏配置
            "game": {
                "game_name": "Dota 2",
                "window_mode": "windowed",  # fullscreen, windowed, borderless
                "chat_hotkey": "shift+enter"  # 聊天快捷键（示例：shift+enter, enter, t）
            },
            
            # 鼓励语配置
            "encouragement": {
                "use_ai_generation": True,  # 是否使用AI生成鼓励语
                "force_ai_generation": True,  # 强制使用AI生成，不使用预设信息
                "custom_prompt": "你是一个专业的Dota 2游戏助手，具有以下特点：\n1. 专业术语丰富，了解游戏机制\n2. 战术分析能力强，能给出具体建议\n3. 鼓励队友时使用专业术语\n4. 回复简洁有力，不超过20字\n5. 始终保持积极正面的态度",  # 全局自定义prompt，用于所有AI对话
                "ai_prompts": {
                    "kill_prompt": "请为Dota 2游戏中的队友击杀生成一句简短的中文鼓励语，要求积极正面，不超过20字，不要包含{player}占位符，直接输出鼓励语内容。",
                    "death_prompt": "请为Dota 2游戏中的队友死亡生成一句简短的中文安慰语，要求积极正面，不超过20字，不要包含{player}占位符，直接输出安慰语内容。",
                    "general_prompt": "请为Dota 2游戏生成一句简短的中文团队鼓励语，要求积极正面，不超过15字，直接输出鼓励语内容。"
                }
            },
            
            # 日志配置
            "logging": {
                "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR
                "log_file": "bot.log",
                "max_log_size": 10485760,  # 10MB
                "backup_count": 5,
                "console_output": True
            },
            
            # 界面配置
            "ui": {
                "window_width": 800,
                "window_height": 600,
                "theme": "default",  # default, dark, light
                "auto_save": True,
                "save_interval": 30  # 自动保存间隔（秒）
            }
        }
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 直接将字典转换为对象属性
                    self._dict_to_attributes(config)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                self.reset_to_default()
        else:
            self.reset_to_default()
            self.save_config()  # 创建默认配置文件
    
    def _merge_config(self, default: Dict[str, Any], loaded: Dict[str, Any]):
        """递归合并配置"""
        for key, value in default.items():
            if key in loaded:
                if isinstance(value, dict) and isinstance(loaded[key], dict):
                    # 递归合并嵌套字典
                    merged_dict = value.copy()
                    self._merge_config(merged_dict, loaded[key])
                    setattr(self, key, merged_dict)
                else:
                    setattr(self, key, loaded[key])
            else:
                setattr(self, key, value)
    
    def _dict_to_attributes(self, config_dict: Dict[str, Any]):
        """将字典转换为对象属性"""
        for key, value in config_dict.items():
            if isinstance(value, dict):
                # 创建嵌套对象
                nested_obj = type('ConfigSection', (), {})()
                self._dict_to_attributes_recursive(value, nested_obj)
                setattr(self, key, nested_obj)
            else:
                setattr(self, key, value)
    
    def _dict_to_attributes_recursive(self, config_dict: Dict[str, Any], obj):
        """递归将字典转换为对象属性"""
        for key, value in config_dict.items():
            if isinstance(value, dict):
                nested_obj = type('ConfigSection', (), {})()
                self._dict_to_attributes_recursive(value, nested_obj)
                setattr(obj, key, nested_obj)
            else:
                setattr(obj, key, value)
    
    def save_config(self):
        """保存配置文件"""
        config_dict = {}
        for key in self.default_config.keys():
            if hasattr(self, key):
                value = getattr(self, key)
                if hasattr(value, '__dict__'):
                    # 如果是对象，转换为字典
                    config_dict[key] = self._object_to_dict(value)
                else:
                    config_dict[key] = value
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, ensure_ascii=False, indent=4)
            print(f"配置文件已保存到: {self.config_file}")
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def _object_to_dict(self, obj):
        """将对象转换为字典"""
        if hasattr(obj, '__dict__'):
            result = {}
            for key, value in obj.__dict__.items():
                if hasattr(value, '__dict__'):
                    result[key] = self._object_to_dict(value)
                else:
                    result[key] = value
            return result
        else:
            return obj
    
    def reset_to_default(self):
        """重置为默认配置"""
        self._dict_to_attributes(self.default_config)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """获取嵌套配置值，支持点号分隔的路径"""
        keys = key_path.split('.')
        value = self
        
        try:
            for key in keys:
                if hasattr(value, key):
                    value = getattr(value, key)
                elif isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            return value
        except (AttributeError, KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """设置嵌套配置值，支持点号分隔的路径"""
        keys = key_path.split('.')
        config = self
        
        # 导航到目标位置
        for key in keys[:-1]:
            if not hasattr(config, key):
                setattr(config, key, {})
            config = getattr(config, key)
            if not isinstance(config, dict):
                setattr(config, key, {})
                config = getattr(config, key)
        
        # 设置最终值
        if len(keys) == 1:
            setattr(self, keys[0], value)
        else:
            config[keys[-1]] = value
        # 设置后立即保存
        try:
            self.save_config()
        except Exception:
            pass

    # ====== OCR区域专用便捷API ======
    def get_ocr_area(self, area_type: str) -> Dict[str, Any]:
        """获取OCR识别区域配置
        
        Args:
            area_type: 'kill' 或 'chat'
        Returns:
            包含 x, y, width, height, enabled 的字典
        """
        area_name = f"{area_type}_detection_area"
        if hasattr(self, 'detection_areas'):
            areas = getattr(self, 'detection_areas')
            if hasattr(areas, area_name):
                area = getattr(areas, area_name)
                if isinstance(area, dict):
                    return area
                # 兼容 ConfigSection
                return {
                    'x': getattr(area, 'x', 0),
                    'y': getattr(area, 'y', 0),
                    'width': getattr(area, 'width', 100),
                    'height': getattr(area, 'height', 50),
                    'enabled': getattr(area, 'enabled', False)
                }
            elif isinstance(areas, dict) and area_name in areas:
                return areas[area_name]
        # 默认返回
        return {'x': 0, 'y': 0, 'width': 100, 'height': 50, 'enabled': False}

    def set_ocr_area(self, area_type: str, x: int, y: int, width: int, height: int, enabled: Optional[bool] = True):
        """设置OCR识别区域并持久化到config.json
        
        Args:
            area_type: 'kill' 或 'chat'
            x, y, width, height: 区域参数
            enabled: 是否启用
        """
        area_name = f"{area_type}_detection_area"
        area_config = {
            'x': int(x),
            'y': int(y),
            'width': int(width),
            'height': int(height),
            'enabled': bool(enabled)
        }
        # 确保 detection_areas 容器存在
        if not hasattr(self, 'detection_areas'):
            setattr(self, 'detection_areas', {})
        areas = getattr(self, 'detection_areas')
        if hasattr(areas, '__dict__'):
            setattr(areas, area_name, area_config)
        elif isinstance(areas, dict):
            areas[area_name] = area_config
        # 立即保存
        self.save_config()
    
    def update_from_dict(self, config_dict: Dict[str, Any]):
        """从字典更新配置"""
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def export_config(self, export_file: str = "config_export.json"):
        """导出配置文件"""
        try:
            config_dict = {}
            for key in self.default_config.keys():
                if hasattr(self, key):
                    config_dict[key] = getattr(self, key)
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, ensure_ascii=False, indent=4)
            print(f"配置已导出到: {export_file}")
        except Exception as e:
            print(f"导出配置失败: {e}")
    
    def import_config(self, import_file: str):
        """导入配置文件"""
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self._merge_config(self.default_config, config)
            print(f"配置已从 {import_file} 导入")
        except Exception as e:
            print(f"导入配置失败: {e}")
    
    def validate_config(self) -> bool:
        """验证配置的有效性"""
        errors = []
        
        # 检查必要的路径
        if not os.path.exists(self.ocr.tesseract_path):
            errors.append(f"Tesseract路径不存在: {self.ocr.tesseract_path}")
        
        if not os.path.exists(self.ocr.tessdata_path):
            errors.append(f"Tessdata路径不存在: {self.ocr.tessdata_path}")
        
        # 检查API密钥
        if not self.api.deepseek_api_key:
            errors.append("DeepSeek API密钥未设置")
        
        # 检查数值范围
        if self.cooldowns.kill_cooldown < 0:
            errors.append("击杀冷却时间不能为负数")
        
        if self.cooldowns.chat_cooldown < 0:
            errors.append("聊天冷却时间不能为负数")
        
        if errors:
            print("配置验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    def __str__(self):
        """返回配置的字符串表示"""
        return f"Config(file={self.config_file}, valid={self.validate_config()})"

class AreaPicker:
    """区域选择器 - 集成版"""
    def __init__(self, parent, config, area_type):
        self.parent = parent
        self.config = config
        self.area_type = area_type  # 'kill' 或 'chat'
        self.picker_window = None
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.selecting = False
        self.canvas = None
        self.rect_id = None
        
    def start_picking(self):
        """开始区域选择"""
        if self.picker_window:
            self.picker_window.destroy()
        
        # 获取屏幕尺寸
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        
        # 创建全屏覆盖窗口
        self.picker_window = tk.Toplevel(self.parent)
        
        # 设置窗口属性
        self.picker_window.attributes('-fullscreen', True)
        self.picker_window.attributes('-alpha', 0.3)
        self.picker_window.attributes('-topmost', True)  # 置顶显示
        self.picker_window.configure(bg='black')
        self.picker_window.overrideredirect(True)
        
        # 设置窗口位置和大小，确保覆盖整个屏幕
        self.picker_window.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # 确保窗口在屏幕最前面
        self.picker_window.lift()
        self.picker_window.focus_force()
        
        # 创建画布，确保覆盖整个屏幕
        self.canvas = tk.Canvas(
            self.picker_window,
            width=screen_width,
            height=screen_height,
            highlightthickness=0,
            bg='black',
            scrollregion=(0, 0, screen_width, screen_height)
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 确保画布能接收所有鼠标事件
        self.canvas.configure(cursor="crosshair")
        
        # 添加屏幕截图背景（可选）
        try:
            # 获取屏幕截图
            screenshot = pyautogui.screenshot()
            # 调整截图大小以匹配画布
            screenshot = screenshot.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
            # 降低透明度
            screenshot.putalpha(128)
            # 转换为PhotoImage
            self.bg_image = ImageTk.PhotoImage(screenshot)
            # 在画布上显示背景
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image)
        except Exception as e:
            print(f"无法获取屏幕截图: {e}")
            # 如果截图失败，使用纯色背景
            self.bg_image = None
        
        # 绑定鼠标事件
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.drag)
        self.canvas.bind('<ButtonRelease-1>', self.end_drag)
        self.canvas.bind('<Button-3>', self.confirm_selection)  # 右键确认
        
        # 绑定键盘事件到窗口
        self.picker_window.bind('<Escape>', self.cancel_picking)
        self.picker_window.bind('<Return>', self.confirm_selection)
        self.picker_window.bind('<KeyPress-Return>', self.confirm_selection)
        
        # 也绑定到画布
        self.canvas.bind('<Escape>', self.cancel_picking)
        self.canvas.bind('<Return>', self.confirm_selection)
        self.canvas.bind('<KeyPress-Return>', self.confirm_selection)
        
        # 添加键盘事件测试
        self.canvas.bind('<KeyPress>', self.on_key_press)
        
        # 添加说明文字
        self.canvas.create_text(
            screen_width // 2,
            50,
            text=f"选择{self.area_type}检测区域",
            fill='white',
            font=('Arial', 16, 'bold')
        )
        
        self.canvas.create_text(
            screen_width // 2,
            80,
            text="拖拽鼠标选择区域，右键或按Enter确认，按ESC取消",
            fill='yellow',
            font=('Arial', 12)
        )
        
        # 添加屏幕边界指示
        self.canvas.create_rectangle(0, 0, screen_width-1, screen_height-1, outline='white', width=2, tags='screen_border')
        
        # 显示当前区域信息
        current_area = self._get_current_area()
        if current_area:
            # 处理ConfigSection对象和字典两种情况
            if hasattr(current_area, 'x'):
                area_text = f"当前区域: ({current_area.x}, {current_area.y}) {current_area.width}x{current_area.height}"
            else:
                area_text = f"当前区域: ({current_area['x']}, {current_area['y']}) {current_area['width']}x{current_area['height']}"
            
            self.canvas.create_text(
                screen_width // 2,
                110,
                text=area_text,
                fill='cyan',
                font=('Arial', 10)
            )
        
        # 设置焦点
        self.picker_window.focus_set()
        self.canvas.focus_set()
        
        # 确保画布可以接收键盘事件
        self.canvas.configure(takefocus=True)
    
    def on_key_press(self, event):
        """键盘按下事件处理"""
        if event.keysym == 'Return' or event.keysym == 'KP_Enter':
            self.confirm_selection(event)
        elif event.keysym == 'Escape':
            self.cancel_picking(event)
        
    def _get_current_area(self):
        """获取当前区域配置"""
        area_name = f"{self.area_type}_detection_area"
        if hasattr(self.config.detection_areas, area_name):
            return getattr(self.config.detection_areas, area_name)
        elif isinstance(self.config.detection_areas, dict):
            return self.config.detection_areas.get(area_name)
        return None
    
    def start_drag(self, event):
        """开始拖拽"""
        self.start_x = event.x
        self.start_y = event.y
        self.selecting = True
        
        # 清除之前的矩形
        if self.rect_id:
            self.canvas.delete(self.rect_id)
    
    def drag(self, event):
        """拖拽过程中"""
        if self.selecting:
            # 清除之前的矩形
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            
            # 确保坐标在屏幕范围内
            x1 = max(0, min(self.start_x, event.x))
            y1 = max(0, min(self.start_y, event.y))
            x2 = min(self.picker_window.winfo_screenwidth(), max(self.start_x, event.x))
            y2 = min(self.picker_window.winfo_screenheight(), max(self.start_y, event.y))
            
            # 绘制新矩形
            self.rect_id = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline='red', width=3, tags='selection_rect'
            )
            
            # 显示尺寸信息
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            
            # 清除之前的尺寸文字
            self.canvas.delete('size_text')
            
            # 显示尺寸，确保文字在屏幕范围内
            text_x = min(x2 + 10, self.picker_window.winfo_screenwidth() - 100)
            text_y = max(y1 - 10, 20)
            
            self.canvas.create_text(
                text_x, text_y,
                text=f"{width}x{height}",
                fill='white',
                font=('Arial', 10, 'bold'),
                tags='size_text'
            )
    
    def end_drag(self, event):
        """结束拖拽"""
        if self.selecting:
            self.end_x = event.x
            self.end_y = event.y
            self.selecting = False
            
            # 确保坐标在屏幕范围内
            x = max(0, min(self.start_x, self.end_x))
            y = max(0, min(self.start_y, self.end_y))
            width = min(self.picker_window.winfo_screenwidth() - x, abs(self.end_x - self.start_x))
            height = min(self.picker_window.winfo_screenheight() - y, abs(self.end_y - self.start_y))
            
            if width > 10 and height > 10:  # 最小区域检查
                # 显示确认信息
                try:
                    self.canvas.delete('confirm_text')
                    self.canvas.create_text(
                        self.picker_window.winfo_screenwidth() // 2,
                        self.picker_window.winfo_screenheight() - 100,
                        text=f"区域: ({x}, {y}) {width}x{height} - 右键或按Enter确认，按ESC取消",
                        fill='lime',
                        font=('Arial', 12, 'bold'),
                        tags='confirm_text'
                    )
                except:
                    pass  # 忽略画布错误
            else:
                messagebox.showwarning("警告", "选择的区域太小，请重新选择")
                try:
                    self.canvas.delete(self.rect_id)
                    self.rect_id = None
                except:
                    pass  # 忽略画布错误
    
    def confirm_selection(self, event=None):
        """确认选择"""
        if not self.rect_id:
            messagebox.showwarning("警告", "请先选择一个区域")
            return
        
        # 计算最终区域，确保坐标在屏幕范围内
        x = max(0, min(self.start_x, self.end_x))
        y = max(0, min(self.start_y, self.end_y))
        width = min(self.picker_window.winfo_screenwidth() - x, abs(self.end_x - self.start_x))
        height = min(self.picker_window.winfo_screenheight() - y, abs(self.end_y - self.start_y))
        
        if width > 10 and height > 10:
            # 保存区域设置
            area_name = f"{self.area_type}_detection_area"
            area_config = {
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'enabled': True
            }
            
            # 更新配置
            if hasattr(self.config.detection_areas, area_name):
                setattr(self.config.detection_areas, area_name, area_config)
            elif isinstance(self.config.detection_areas, dict):
                self.config.detection_areas[area_name] = area_config
            
            # 保存配置
            if hasattr(self.config, 'save_config'):
                self.config.save_config()
            
            # 关闭选择窗口
            self.picker_window.destroy()
            self.picker_window = None
            
            # 恢复父窗口状态
            self.parent.lift()
            self.parent.focus_force()
            
            messagebox.showinfo("成功", f"{self.area_type}检测区域已设置: ({x}, {y}) {width}x{height}")
        else:
            messagebox.showwarning("警告", "选择的区域太小，请重新选择")
    
    def cancel_picking(self, event=None):
        """取消选择"""
        if self.picker_window:
            # 恢复父窗口状态
            self.parent.lift()
            self.parent.focus_force()
            self.picker_window.destroy()
            self.picker_window = None

class AreaManager:
    """区域管理器 - 集成版"""
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.manager_window = None
        
    def show_area_manager(self):
        """显示区域管理器"""
        if self.manager_window:
            self.manager_window.destroy()
        
        self.manager_window = tk.Toplevel(self.parent)
        self.manager_window.title("区域管理器")
        self.manager_window.geometry("600x500")
        
        # 创建主框架
        main_frame = ttk.Frame(self.manager_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 击杀检测区域管理
        kill_frame = ttk.LabelFrame(main_frame, text="击杀检测区域")
        kill_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.create_area_controls(kill_frame, 'kill')
        
        # 聊天检测区域管理
        chat_frame = ttk.LabelFrame(main_frame, text="聊天检测区域")
        chat_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.create_area_controls(chat_frame, 'chat')
        
        # 预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="区域预览")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_text = tk.Text(preview_frame, height=10, width=60)
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 刷新预览
        self.refresh_preview()
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="刷新预览", 
                  command=self.refresh_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="重置所有区域", 
                  command=self.reset_all_areas).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", 
                  command=self.manager_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def create_area_controls(self, parent, area_type):
        """创建区域控制组件"""
        # 当前区域信息
        area_name = f"{area_type}_detection_area"
        if hasattr(self.config.detection_areas, area_name):
            area = getattr(self.config.detection_areas, area_name)
        elif isinstance(self.config.detection_areas, dict):
            area = self.config.detection_areas.get(area_name, {})
        else:
            area = {}
        
        # 创建区域信息显示框架
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 动态更新标签
        self.info_labels = getattr(self, 'info_labels', {})
        self.info_labels[area_type] = {
            'position': ttk.Label(info_frame, text=f"位置: ({area.get('x', 0)}, {area.get('y', 0)})"),
            'size': ttk.Label(info_frame, text=f"大小: {area.get('width', 0)}x{area.get('height', 0)}"),
            'status': ttk.Label(info_frame, text=f"状态: {'启用' if area.get('enabled', False) else '禁用'}")
        }
        
        self.info_labels[area_type]['position'].pack(side=tk.LEFT, padx=5)
        self.info_labels[area_type]['size'].pack(side=tk.LEFT, padx=5)
        self.info_labels[area_type]['status'].pack(side=tk.LEFT, padx=5)
        
        # 控制按钮
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="选择区域", 
                  command=lambda: self.pick_area(area_type)).pack(side=tk.LEFT, padx=5)
        
        # 启用/禁用开关
        self.enabled_vars = getattr(self, 'enabled_vars', {})
        self.enabled_vars[area_type] = tk.BooleanVar(value=area.get('enabled', False))
        ttk.Checkbutton(button_frame, text="启用检测", 
                       variable=self.enabled_vars[area_type],
                       command=lambda: self.toggle_area(area_type, self.enabled_vars[area_type].get())).pack(side=tk.LEFT, padx=5)
        
        # 手动输入坐标
        coord_frame = ttk.Frame(parent)
        coord_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(coord_frame, text="X:").pack(side=tk.LEFT, padx=2)
        self.coord_vars = getattr(self, 'coord_vars', {})
        self.coord_vars[area_type] = {
            'x': tk.IntVar(value=area.get('x', 0)),
            'y': tk.IntVar(value=area.get('y', 0)),
            'width': tk.IntVar(value=area.get('width', 100)),
            'height': tk.IntVar(value=area.get('height', 50))
        }
        
        ttk.Spinbox(coord_frame, from_=0, to=2000, textvariable=self.coord_vars[area_type]['x'], width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(coord_frame, text="Y:").pack(side=tk.LEFT, padx=2)
        ttk.Spinbox(coord_frame, from_=0, to=2000, textvariable=self.coord_vars[area_type]['y'], width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(coord_frame, text="宽:").pack(side=tk.LEFT, padx=2)
        ttk.Spinbox(coord_frame, from_=10, to=1000, textvariable=self.coord_vars[area_type]['width'], width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(coord_frame, text="高:").pack(side=tk.LEFT, padx=2)
        ttk.Spinbox(coord_frame, from_=10, to=1000, textvariable=self.coord_vars[area_type]['height'], width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(coord_frame, text="应用", 
                  command=lambda: self.update_area(area_type, 
                                                 self.coord_vars[area_type]['x'].get(),
                                                 self.coord_vars[area_type]['y'].get(),
                                                 self.coord_vars[area_type]['width'].get(),
                                                 self.coord_vars[area_type]['height'].get())).pack(side=tk.LEFT, padx=5)
    
    def pick_area(self, area_type):
        """选择区域"""
        picker = AreaPicker(self.manager_window, self.config, area_type)
        picker.start_picking()
        # 等待选择完成
        self.manager_window.after(100, self.refresh_preview)
        self.manager_window.after(200, lambda: self.update_area_display(area_type))
    
    def toggle_area(self, area_type, enabled):
        """切换区域启用状态"""
        area_name = f"{area_type}_detection_area"
        if hasattr(self.config.detection_areas, area_name):
            area = getattr(self.config.detection_areas, area_name)
            area['enabled'] = enabled
        elif isinstance(self.config.detection_areas, dict):
            if area_name in self.config.detection_areas:
                self.config.detection_areas[area_name]['enabled'] = enabled
        
        if hasattr(self.config, 'save_config'):
            self.config.save_config()
        self.refresh_preview()
        self.update_area_display(area_type)
    
    def update_area_display(self, area_type):
        """更新区域显示信息"""
        if not hasattr(self, 'info_labels') or area_type not in self.info_labels:
            return
            
        # 获取当前区域信息
        area_name = f"{area_type}_detection_area"
        if hasattr(self.config.detection_areas, area_name):
            area = getattr(self.config.detection_areas, area_name)
        elif isinstance(self.config.detection_areas, dict):
            area = self.config.detection_areas.get(area_name, {})
        else:
            area = {}
        
        # 更新标签显示
        self.info_labels[area_type]['position'].config(text=f"位置: ({area.get('x', 0)}, {area.get('y', 0)})")
        self.info_labels[area_type]['size'].config(text=f"大小: {area.get('width', 0)}x{area.get('height', 0)}")
        self.info_labels[area_type]['status'].config(text=f"状态: {'启用' if area.get('enabled', False) else '禁用'}")
        
        # 更新坐标输入框
        if hasattr(self, 'coord_vars') and area_type in self.coord_vars:
            self.coord_vars[area_type]['x'].set(area.get('x', 0))
            self.coord_vars[area_type]['y'].set(area.get('y', 0))
            self.coord_vars[area_type]['width'].set(area.get('width', 100))
            self.coord_vars[area_type]['height'].set(area.get('height', 50))
        
        # 更新启用状态
        if hasattr(self, 'enabled_vars') and area_type in self.enabled_vars:
            self.enabled_vars[area_type].set(area.get('enabled', False))
    
    def update_area(self, area_type, x, y, width, height):
        """更新区域坐标"""
        area_name = f"{area_type}_detection_area"
        if hasattr(self.config.detection_areas, area_name):
            area = getattr(self.config.detection_areas, area_name)
            area['x'] = x
            area['y'] = y
            area['width'] = width
            area['height'] = height
        elif isinstance(self.config.detection_areas, dict):
            if area_name in self.config.detection_areas:
                self.config.detection_areas[area_name]['x'] = x
                self.config.detection_areas[area_name]['y'] = y
                self.config.detection_areas[area_name]['width'] = width
                self.config.detection_areas[area_name]['height'] = height
        
        if hasattr(self.config, 'save_config'):
            self.config.save_config()
        self.refresh_preview()
        self.update_area_display(area_type)
        messagebox.showinfo("成功", f"{area_type}区域已更新")
    
    def reset_all_areas(self):
        """重置所有区域"""
        if messagebox.askyesno("确认", "确定要重置所有区域为默认值吗？"):
            # 重置为默认值
            if hasattr(self.config.detection_areas, 'kill_detection_area'):
                self.config.detection_areas.kill_detection_area = {
                    'x': 100, 'y': 100, 'width': 200, 'height': 50, 'enabled': True
                }
                self.config.detection_areas.chat_detection_area = {
                    'x': 100, 'y': 200, 'width': 300, 'height': 100, 'enabled': True
                }
            elif isinstance(self.config.detection_areas, dict):
                self.config.detection_areas['kill_detection_area'] = {
                    'x': 100, 'y': 100, 'width': 200, 'height': 50, 'enabled': True
                }
                self.config.detection_areas['chat_detection_area'] = {
                    'x': 100, 'y': 200, 'width': 300, 'height': 100, 'enabled': True
                }
            
            if hasattr(self.config, 'save_config'):
                self.config.save_config()
            self.refresh_preview()
            # 更新所有区域的显示
            self.update_area_display('kill')
            self.update_area_display('chat')
            messagebox.showinfo("成功", "所有区域已重置为默认值")
    
    def refresh_preview(self):
        """刷新预览"""
        self.preview_text.delete("1.0", tk.END)
        
        preview = "当前区域配置:\n\n"
        
        # 获取区域信息
        if hasattr(self.config.detection_areas, 'kill_detection_area'):
            kill_area = self.config.detection_areas.kill_detection_area
            chat_area = self.config.detection_areas.chat_detection_area
        elif isinstance(self.config.detection_areas, dict):
            kill_area = self.config.detection_areas.get('kill_detection_area', {})
            chat_area = self.config.detection_areas.get('chat_detection_area', {})
        else:
            kill_area = {}
            chat_area = {}
        
        # 击杀检测区域
        preview += f"击杀检测区域:\n"
        preview += f"  位置: ({kill_area.get('x', 0)}, {kill_area.get('y', 0)})\n"
        preview += f"  大小: {kill_area.get('width', 0)}x{kill_area.get('height', 0)}\n"
        preview += f"  状态: {'启用' if kill_area.get('enabled', False) else '禁用'}\n\n"
        
        # 聊天检测区域
        preview += f"聊天检测区域:\n"
        preview += f"  位置: ({chat_area.get('x', 0)}, {chat_area.get('y', 0)})\n"
        preview += f"  大小: {chat_area.get('width', 0)}x{chat_area.get('height', 0)}\n"
        preview += f"  状态: {'启用' if chat_area.get('enabled', False) else '禁用'}\n\n"
        
        preview += "使用说明:\n"
        preview += "1. 点击'选择区域'按钮进行可视化选择\n"
        preview += "2. 或手动输入坐标和尺寸\n"
        preview += "3. 可以单独启用/禁用每个检测区域\n"
        preview += "4. 建议选择文字清晰、背景对比度高的区域"
        
        self.preview_text.insert(tk.END, preview)

class ConfigManager:
    """配置管理界面 - 整合版"""
    
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.config_window = None
        
    def show_config_window(self):
        """显示配置管理窗口"""
        if self.config_window:
            self.config_window.destroy()
        
        self.config_window = tk.Toplevel(self.parent)
        self.config_window.title("配置管理")
        self.config_window.geometry("800x600")
        
        # 创建标签页
        notebook = ttk.Notebook(self.config_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # API配置标签页
        self.create_api_tab(notebook)
        
        # OCR配置标签页
        self.create_ocr_tab(notebook)
        
        # 检测区域配置标签页
        self.create_detection_tab(notebook)
        
        # 区域选择标签页
        self.create_area_selection_tab(notebook)
        
        # 功能配置标签页
        self.create_features_tab(notebook)
        
        # 鼓励语配置标签页
        self.create_encouragement_tab(notebook)
        
        # 按钮框架
        button_frame = ttk.Frame(self.config_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="保存配置", command=self.save_all_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="重置为默认", command=self.reset_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="导入配置", command=self.import_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="导出配置", command=self.export_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="验证配置", command=self.validate_config).pack(side=tk.LEFT, padx=5)
        
    def create_api_tab(self, parent):
        """创建API配置标签页"""
        api_tab = ttk.Frame(parent)
        parent.add(api_tab, text="API配置")
        
        # API密钥
        ttk.Label(api_tab, text="DeepSeek API密钥:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.api_key_var = tk.StringVar(value=self.config.api.deepseek_api_key)
        api_key_entry = ttk.Entry(api_tab, textvariable=self.api_key_var, width=50, show="*")
        api_key_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # API基础URL
        ttk.Label(api_tab, text="API基础URL:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.api_url_var = tk.StringVar(value=self.config.api.api_base_url)
        ttk.Entry(api_tab, textvariable=self.api_url_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        
        # 模型名称
        ttk.Label(api_tab, text="模型名称:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.model_var = tk.StringVar(value=self.config.api.model)
        ttk.Entry(api_tab, textvariable=self.model_var, width=50).grid(row=2, column=1, padx=5, pady=5)
        
        # 温度参数
        ttk.Label(api_tab, text="温度参数:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.temperature_var = tk.DoubleVar(value=self.config.api.temperature)
        ttk.Spinbox(api_tab, from_=0.0, to=2.0, increment=0.1, textvariable=self.temperature_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 最大令牌数
        ttk.Label(api_tab, text="最大令牌数:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_tokens_var = tk.IntVar(value=self.config.api.max_tokens)
        ttk.Spinbox(api_tab, from_=50, to=2000, increment=50, textvariable=self.max_tokens_var, width=10).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 超时时间
        ttk.Label(api_tab, text="超时时间(秒):").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.timeout_var = tk.IntVar(value=self.config.api.timeout)
        ttk.Spinbox(api_tab, from_=5, to=60, increment=5, textvariable=self.timeout_var, width=10).grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
    def create_ocr_tab(self, parent):
        """创建OCR配置标签页"""
        ocr_tab = ttk.Frame(parent)
        parent.add(ocr_tab, text="OCR配置")
        
        # Tesseract路径
        ttk.Label(ocr_tab, text="Tesseract路径:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.tesseract_path_var = tk.StringVar(value=self.config.ocr.tesseract_path)
        ttk.Entry(ocr_tab, textvariable=self.tesseract_path_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(ocr_tab, text="浏览", command=self.browse_tesseract_path).grid(row=0, column=2, padx=5, pady=5)
        
        # Tessdata路径
        ttk.Label(ocr_tab, text="Tessdata路径:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.tessdata_path_var = tk.StringVar(value=self.config.ocr.tessdata_path)
        ttk.Entry(ocr_tab, textvariable=self.tessdata_path_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(ocr_tab, text="浏览", command=self.browse_tessdata_path).grid(row=1, column=2, padx=5, pady=5)
        
        # 语言设置
        ttk.Label(ocr_tab, text="语言设置:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.language_var = tk.StringVar(value=self.config.ocr.language)
        ttk.Entry(ocr_tab, textvariable=self.language_var, width=50).grid(row=2, column=1, padx=5, pady=5)
        
        # 检测间隔
        ttk.Label(ocr_tab, text="检测间隔(秒):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.detection_interval_var = tk.DoubleVar(value=self.config.ocr.detection_interval)
        ttk.Spinbox(ocr_tab, from_=0.01, to=1.0, increment=0.01, textvariable=self.detection_interval_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # OCR引擎选择
        ttk.Label(ocr_tab, text="OCR引擎:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.ocr_engine_var = tk.StringVar(value=self.config.ocr.engine)
        engine_combo = ttk.Combobox(ocr_tab, textvariable=self.ocr_engine_var, width=20, state="readonly")
        engine_combo['values'] = ('tesseract', 'easyocr', 'paddleocr')
        engine_combo.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # OCR引擎说明
        engine_info = ttk.Label(ocr_tab, text="tesseract: 谷歌开源OCR | easyocr: 中文识别效果好 | paddleocr: 百度开发，精度高", 
                               font=("Arial", 8), foreground="gray")
        engine_info.grid(row=5, column=0, columnspan=3, sticky=tk.W, padx=5, pady=2)
        
    def create_detection_tab(self, parent):
        """创建检测区域配置标签页"""
        detection_tab = ttk.Frame(parent)
        parent.add(detection_tab, text="检测区域")
        
        # 提示信息
        info_frame = ttk.Frame(detection_tab)
        info_frame.grid(row=0, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Label(info_frame, text="检测区域配置", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        ttk.Label(info_frame, text="建议使用区域管理器进行可视化配置，这里仅显示当前设置").pack(anchor=tk.W)
        
        # 当前区域状态显示
        status_frame = ttk.LabelFrame(detection_tab, text="当前区域状态")
        status_frame.grid(row=1, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # 击杀检测区域状态
        kill_status_frame = ttk.Frame(status_frame)
        kill_status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(kill_status_frame, text="击杀检测区域:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.kill_status_label = ttk.Label(kill_status_frame, text="")
        self.kill_status_label.pack(anchor=tk.W, padx=20)
        
        # 聊天检测区域状态
        chat_status_frame = ttk.Frame(status_frame)
        chat_status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(chat_status_frame, text="聊天检测区域:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.chat_status_label = ttk.Label(chat_status_frame, text="")
        self.chat_status_label.pack(anchor=tk.W, padx=20)
        
        # 区域管理器按钮
        manager_frame = ttk.Frame(detection_tab)
        manager_frame.grid(row=2, column=0, sticky=tk.W+tk.E, padx=5, pady=10)
        
        ttk.Button(manager_frame, text="打开区域管理器", 
                  command=self.open_area_manager).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(manager_frame, text="刷新状态", 
                  command=self.refresh_detection_status).pack(side=tk.LEFT, padx=5)
        
        # 快速区域选择
        quick_frame = ttk.LabelFrame(detection_tab, text="快速区域选择")
        quick_frame.grid(row=3, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Button(quick_frame, text="选择击杀检测区域", 
                  command=lambda: self.quick_select_area('kill')).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(quick_frame, text="选择聊天检测区域", 
                  command=lambda: self.quick_select_area('chat')).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 直接编辑区域
        edit_frame = ttk.LabelFrame(detection_tab, text="直接编辑区域")
        edit_frame.grid(row=4, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # 击杀区域编辑行
        kill_edit = ttk.Frame(edit_frame)
        kill_edit.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(kill_edit, text="击杀区域").pack(side=tk.LEFT, padx=(0, 8))
        kill = self.config.get_ocr_area('kill') if hasattr(self.config, 'get_ocr_area') else {'x':0,'y':0,'width':100,'height':50,'enabled':False}
        self.kill_x_var = tk.IntVar(value=kill.get('x', 0))
        self.kill_y_var = tk.IntVar(value=kill.get('y', 0))
        self.kill_w_var = tk.IntVar(value=kill.get('width', 100))
        self.kill_h_var = tk.IntVar(value=kill.get('height', 50))
        self.kill_enabled_var = tk.BooleanVar(value=kill.get('enabled', False))
        
        ttk.Label(kill_edit, text="X:").pack(side=tk.LEFT)
        ttk.Spinbox(kill_edit, from_=0, to=10000, textvariable=self.kill_x_var, width=8).pack(side=tk.LEFT, padx=(0,6))
        ttk.Label(kill_edit, text="Y:").pack(side=tk.LEFT)
        ttk.Spinbox(kill_edit, from_=0, to=10000, textvariable=self.kill_y_var, width=8).pack(side=tk.LEFT, padx=(0,6))
        ttk.Label(kill_edit, text="宽:").pack(side=tk.LEFT)
        ttk.Spinbox(kill_edit, from_=10, to=10000, textvariable=self.kill_w_var, width=8).pack(side=tk.LEFT, padx=(0,6))
        ttk.Label(kill_edit, text="高:").pack(side=tk.LEFT)
        ttk.Spinbox(kill_edit, from_=10, to=10000, textvariable=self.kill_h_var, width=8).pack(side=tk.LEFT, padx=(0,10))
        ttk.Checkbutton(kill_edit, text="启用检测", variable=self.kill_enabled_var).pack(side=tk.LEFT, padx=(0,10))
        ttk.Button(kill_edit, text="保存", command=lambda: self.save_area_changes('kill')).pack(side=tk.LEFT)
        ttk.Button(kill_edit, text="可视化选择", command=lambda: self.quick_select_area('kill')).pack(side=tk.LEFT, padx=(6,0))
        
        # 聊天区域编辑行
        chat_edit = ttk.Frame(edit_frame)
        chat_edit.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(chat_edit, text="聊天区域").pack(side=tk.LEFT, padx=(0, 8))
        chat = self.config.get_ocr_area('chat') if hasattr(self.config, 'get_ocr_area') else {'x':0,'y':0,'width':100,'height':50,'enabled':False}
        self.chat_x_var = tk.IntVar(value=chat.get('x', 0))
        self.chat_y_var = tk.IntVar(value=chat.get('y', 0))
        self.chat_w_var = tk.IntVar(value=chat.get('width', 100))
        self.chat_h_var = tk.IntVar(value=chat.get('height', 50))
        self.chat_enabled_var = tk.BooleanVar(value=chat.get('enabled', False))
        
        ttk.Label(chat_edit, text="X:").pack(side=tk.LEFT)
        ttk.Spinbox(chat_edit, from_=0, to=10000, textvariable=self.chat_x_var, width=8).pack(side=tk.LEFT, padx=(0,6))
        ttk.Label(chat_edit, text="Y:").pack(side=tk.LEFT)
        ttk.Spinbox(chat_edit, from_=0, to=10000, textvariable=self.chat_y_var, width=8).pack(side=tk.LEFT, padx=(0,6))
        ttk.Label(chat_edit, text="宽:").pack(side=tk.LEFT)
        ttk.Spinbox(chat_edit, from_=10, to=10000, textvariable=self.chat_w_var, width=8).pack(side=tk.LEFT, padx=(0,6))
        ttk.Label(chat_edit, text="高:").pack(side=tk.LEFT)
        ttk.Spinbox(chat_edit, from_=10, to=10000, textvariable=self.chat_h_var, width=8).pack(side=tk.LEFT, padx=(0,10))
        ttk.Checkbutton(chat_edit, text="启用检测", variable=self.chat_enabled_var).pack(side=tk.LEFT, padx=(0,10))
        ttk.Button(chat_edit, text="保存", command=lambda: self.save_area_changes('chat')).pack(side=tk.LEFT)
        ttk.Button(chat_edit, text="可视化选择", command=lambda: self.quick_select_area('chat')).pack(side=tk.LEFT, padx=(6,0))
        
        # 初始化状态显示
        self.refresh_detection_status()
        # 同步编辑框显示
        if hasattr(self, 'sync_detection_edit_fields'):
            self.sync_detection_edit_fields()
        
    def create_area_selection_tab(self, parent):
        """创建区域选择标签页"""
        area_tab = ttk.Frame(parent)
        parent.add(area_tab, text="区域选择")
        
        # 区域管理器按钮
        ttk.Button(area_tab, text="打开区域管理器", 
                  command=self.open_area_manager).pack(padx=10, pady=10)
        
        # 快速区域选择
        quick_frame = ttk.LabelFrame(area_tab, text="快速区域选择")
        quick_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(quick_frame, text="选择击杀检测区域", 
                  command=lambda: self.quick_select_area('kill')).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(quick_frame, text="选择聊天检测区域", 
                  command=lambda: self.quick_select_area('chat')).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 区域状态显示
        status_frame = ttk.LabelFrame(area_tab, text="当前区域状态")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.area_status_text = tk.Text(status_frame, height=10, width=60)
        area_scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.area_status_text.yview)
        self.area_status_text.configure(yscrollcommand=area_scrollbar.set)
        
        self.area_status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        area_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 刷新区域状态
        self.refresh_area_status()
        
    def create_features_tab(self, parent):
        """创建功能配置标签页"""
        features_tab = ttk.Frame(parent)
        parent.add(features_tab, text="功能配置")
        
        # 功能开关
        self.encouragement_enabled_var = tk.BooleanVar(value=self.config.features.encouragement_enabled)
        ttk.Checkbutton(features_tab, text="启用鼓励语", variable=self.encouragement_enabled_var).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.auto_response_enabled_var = tk.BooleanVar(value=self.config.features.auto_response_enabled)
        ttk.Checkbutton(features_tab, text="启用自动回复", variable=self.auto_response_enabled_var).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.kill_detection_enabled_var = tk.BooleanVar(value=self.config.features.kill_detection_enabled)
        ttk.Checkbutton(features_tab, text="启用击杀检测", variable=self.kill_detection_enabled_var).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.chat_detection_enabled_var = tk.BooleanVar(value=self.config.features.chat_detection_enabled)
        ttk.Checkbutton(features_tab, text="启用聊天检测", variable=self.chat_detection_enabled_var).grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.check_kill_after_chat_var = tk.BooleanVar(value=getattr(self.config.features, 'check_kill_after_chat', True))
        ttk.Checkbutton(features_tab, text="聊天后检测击杀", variable=self.check_kill_after_chat_var).grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.enable_chat_interaction_var = tk.BooleanVar(value=getattr(self.config.features, 'enable_chat_interaction', True))
        ttk.Checkbutton(features_tab, text="启用击杀/死亡后聊天交流", variable=self.enable_chat_interaction_var).grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.debug_mode_var = tk.BooleanVar(value=self.config.features.debug_mode)
        ttk.Checkbutton(features_tab, text="调试模式", variable=self.debug_mode_var).grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        
        # 自定义prompt设置
        prompt_frame = ttk.LabelFrame(features_tab, text="自定义AI Prompt")
        prompt_frame.grid(row=7, column=0, sticky=tk.W+tk.E, padx=5, pady=10)
        
        ttk.Label(prompt_frame, text="自定义Prompt (作用于所有AI对话):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.custom_prompt_var = tk.StringVar(value=getattr(self.config.encouragement, 'custom_prompt', ''))
        self.custom_prompt_entry = tk.Text(prompt_frame, height=4, width=60)
        self.custom_prompt_entry.grid(row=1, column=0, sticky=tk.W+tk.E, padx=5, pady=2)
        self.custom_prompt_entry.insert('1.0', self.custom_prompt_var.get())
        
        # 详细说明
        explanation_text = """作用范围：
• 聊天回复：与队友对话时的AI回复
• 击杀鼓励语：检测到队友击杀时的鼓励
• 死亡安慰语：检测到队友死亡时的安慰
• 一般鼓励语：其他游戏情况的鼓励

提示：留空使用默认prompt，填写后所有AI对话都会使用此prompt作为系统角色设定"""
        
        ttk.Label(prompt_frame, text=explanation_text, 
                 font=('Arial', 8), justify=tk.LEFT).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        
        # 冷却时间设置
        cooldown_frame = ttk.LabelFrame(features_tab, text="冷却时间设置")
        cooldown_frame.grid(row=8, column=0, sticky=tk.W+tk.E, padx=5, pady=10)
        
        ttk.Label(cooldown_frame, text="击杀冷却时间(秒):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.kill_cooldown_var = tk.DoubleVar(value=self.config.cooldowns.kill_cooldown)
        ttk.Spinbox(cooldown_frame, from_=0.1, to=60.0, increment=0.1, textvariable=self.kill_cooldown_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(cooldown_frame, text="聊天冷却时间(秒):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.chat_cooldown_var = tk.DoubleVar(value=self.config.cooldowns.chat_cooldown)
        ttk.Spinbox(cooldown_frame, from_=0.1, to=60.0, increment=0.1, textvariable=self.chat_cooldown_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(cooldown_frame, text="鼓励语冷却时间(秒):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.encouragement_cooldown_var = tk.DoubleVar(value=self.config.cooldowns.encouragement_cooldown)
        ttk.Spinbox(cooldown_frame, from_=0.1, to=60.0, increment=0.1, textvariable=self.encouragement_cooldown_var, width=10).grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(cooldown_frame, text="最短聊天间隔(秒):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.min_chat_interval_var = tk.DoubleVar(value=getattr(self.config.cooldowns, 'min_chat_interval', 2.0))
        ttk.Spinbox(cooldown_frame, from_=0.5, to=10.0, increment=0.1, textvariable=self.min_chat_interval_var, width=10).grid(row=3, column=1, padx=5, pady=2)
        
    def create_encouragement_tab(self, parent):
        """创建鼓励语配置标签页"""
        encouragement_tab = ttk.Frame(parent)
        parent.add(encouragement_tab, text="鼓励语配置")
        
        # AI生成设置
        ai_frame = ttk.LabelFrame(encouragement_tab, text="AI生成设置")
        ai_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.use_ai_generation_var = tk.BooleanVar(value=self.config.encouragement.use_ai_generation)
        ttk.Checkbutton(ai_frame, text="使用AI生成鼓励语", 
                       variable=self.use_ai_generation_var).pack(anchor=tk.W, padx=5, pady=5)
        
        # AI提示词配置
        prompt_frame = ttk.LabelFrame(encouragement_tab, text="AI提示词配置")
        prompt_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 击杀提示词
        ttk.Label(prompt_frame, text="击杀提示词:").pack(anchor=tk.W, padx=5, pady=2)
        self.kill_prompt_var = tk.StringVar(value=self.config.encouragement.ai_prompts.kill_prompt)
        kill_prompt_entry = ttk.Entry(prompt_frame, textvariable=self.kill_prompt_var, width=80)
        kill_prompt_entry.pack(fill=tk.X, padx=5, pady=2)
        
        # 死亡提示词
        ttk.Label(prompt_frame, text="死亡提示词:").pack(anchor=tk.W, padx=5, pady=2)
        self.death_prompt_var = tk.StringVar(value=self.config.encouragement.ai_prompts.death_prompt)
        death_prompt_entry = ttk.Entry(prompt_frame, textvariable=self.death_prompt_var, width=80)
        death_prompt_entry.pack(fill=tk.X, padx=5, pady=2)
        
        # 通用提示词
        ttk.Label(prompt_frame, text="通用提示词:").pack(anchor=tk.W, padx=5, pady=2)
        self.general_prompt_var = tk.StringVar(value=self.config.encouragement.ai_prompts.general_prompt)
        general_prompt_entry = ttk.Entry(prompt_frame, textvariable=self.general_prompt_var, width=80)
        general_prompt_entry.pack(fill=tk.X, padx=5, pady=2)
        
        # 全局自定义prompt配置
        global_prompt_frame = ttk.LabelFrame(encouragement_tab, text="全局自定义Prompt")
        global_prompt_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(global_prompt_frame, text="全局Prompt (作用于所有AI对话):").pack(anchor=tk.W, padx=5, pady=2)
        self.global_prompt_text = tk.Text(global_prompt_frame, height=8, width=80)
        global_prompt_scrollbar = ttk.Scrollbar(global_prompt_frame, orient=tk.VERTICAL, command=self.global_prompt_text.yview)
        self.global_prompt_text.configure(yscrollcommand=global_prompt_scrollbar.set)
        
        self.global_prompt_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        global_prompt_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 加载全局自定义prompt
        global_prompt = getattr(self.config.encouragement, 'custom_prompt', '')
        self.global_prompt_text.insert(tk.END, global_prompt)
        
        # 说明文字
        explanation_text = """全局Prompt说明：
• 此Prompt将应用于所有AI对话（聊天回复、击杀鼓励语、死亡安慰语等）
• 定义了AI助手的角色特征和行为风格
• 留空则使用默认的Dota 2游戏助手角色
• 建议描述AI的专业领域、语言风格和回复特点"""
        
        ttk.Label(global_prompt_frame, text=explanation_text, 
                 font=('Arial', 8), justify=tk.LEFT).pack(anchor=tk.W, padx=5, pady=2)
        
    def browse_tesseract_path(self):
        """浏览Tesseract路径"""
        filename = filedialog.askopenfilename(
            title="选择Tesseract可执行文件",
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
        )
        if filename:
            self.tesseract_path_var.set(filename)
    
    def browse_tessdata_path(self):
        """浏览Tessdata路径"""
        dirname = filedialog.askdirectory(title="选择Tessdata目录")
        if dirname:
            self.tessdata_path_var.set(dirname)
    
    
    
    def open_area_manager(self):
        """打开区域管理器"""
        area_manager = AreaManager(self.config_window, self.config)
        area_manager.show_area_manager()
        # 等待区域管理器关闭后刷新状态
        self.config_window.after(100, self.refresh_detection_status)
        self.config_window.after(100, self.refresh_area_status)
    
    def quick_select_area(self, area_type):
        """快速选择区域"""
        picker = AreaPicker(self.config_window, self.config, area_type)
        picker.start_picking()
        # 等待选择完成
        self.config_window.after(100, self.refresh_area_status)
        self.config_window.after(100, self.refresh_detection_status)
        self.config_window.after(120, self.sync_detection_edit_fields)

    def save_area_changes(self, area_type: str):
        """从编辑框保存区域设置到配置并写盘"""
        try:
            if area_type == 'kill':
                x = self.kill_x_var.get()
                y = self.kill_y_var.get()
                w = self.kill_w_var.get()
                h = self.kill_h_var.get()
                enabled = self.kill_enabled_var.get()
            else:
                x = self.chat_x_var.get()
                y = self.chat_y_var.get()
                w = self.chat_w_var.get()
                h = self.chat_h_var.get()
                enabled = self.chat_enabled_var.get()
            
            if w < 10 or h < 10:
                messagebox.showwarning("警告", "宽和高必须至少为10")
                return
            
            if hasattr(self.config, 'set_ocr_area'):
                self.config.set_ocr_area(area_type, x, y, w, h, enabled)
            else:
                # 回退：直接写入对象并保存
                area_name = f"{area_type}_detection_area"
                if hasattr(self.config, 'detection_areas'):
                    areas = getattr(self.config, 'detection_areas')
                    area_cfg = {'x': x, 'y': y, 'width': w, 'height': h, 'enabled': enabled}
                    if hasattr(areas, '__dict__'):
                        setattr(areas, area_name, area_cfg)
                    elif isinstance(areas, dict):
                        areas[area_name] = area_cfg
                    if hasattr(self.config, 'save_config'):
                        self.config.save_config()
            
            self.refresh_detection_status()
            self.refresh_area_status()
            messagebox.showinfo("成功", ("击杀" if area_type=='kill' else "聊天") + "区域已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存区域失败: {e}")

    def sync_detection_edit_fields(self):
        """同步编辑框值为最新配置"""
        try:
            if hasattr(self.config, 'get_ocr_area'):
                k = self.config.get_ocr_area('kill')
                c = self.config.get_ocr_area('chat')
            else:
                k = {}
                c = {}
            if hasattr(self, 'kill_x_var'):
                self.kill_x_var.set(k.get('x', 0))
                self.kill_y_var.set(k.get('y', 0))
                self.kill_w_var.set(k.get('width', 100))
                self.kill_h_var.set(k.get('height', 50))
                self.kill_enabled_var.set(k.get('enabled', False))
            if hasattr(self, 'chat_x_var'):
                self.chat_x_var.set(c.get('x', 0))
                self.chat_y_var.set(c.get('y', 0))
                self.chat_w_var.set(c.get('width', 100))
                self.chat_h_var.set(c.get('height', 50))
                self.chat_enabled_var.set(c.get('enabled', False))
        except Exception:
            pass
    
    def refresh_detection_status(self):
        """刷新检测区域状态显示"""
        try:
            # 更新击杀检测区域状态
            kill_area = self.config.detection_areas.kill_detection_area
            if hasattr(kill_area, 'x'):
                kill_status = f"位置: ({kill_area.x}, {kill_area.y}) | 大小: {kill_area.width}x{kill_area.height} | 状态: {'启用' if kill_area.enabled else '禁用'}"
            else:
                kill_status = f"位置: ({kill_area['x']}, {kill_area['y']}) | 大小: {kill_area['width']}x{kill_area['height']} | 状态: {'启用' if kill_area['enabled'] else '禁用'}"
            self.kill_status_label.config(text=kill_status)
            
            # 更新聊天检测区域状态
            chat_area = self.config.detection_areas.chat_detection_area
            if hasattr(chat_area, 'x'):
                chat_status = f"位置: ({chat_area.x}, {chat_area.y}) | 大小: {chat_area.width}x{chat_area.height} | 状态: {'启用' if chat_area.enabled else '禁用'}"
            else:
                chat_status = f"位置: ({chat_area['x']}, {chat_area['y']}) | 大小: {chat_area['width']}x{chat_area['height']} | 状态: {'启用' if chat_area['enabled'] else '禁用'}"
            self.chat_status_label.config(text=chat_status)
        except Exception as e:
            print(f"刷新检测区域状态失败: {e}")
    
    def refresh_area_status(self):
        """刷新区域状态显示"""
        self.area_status_text.delete("1.0", tk.END)
        
        status = "当前区域状态:\n\n"
        
        try:
            # 击杀检测区域
            kill_area = self.config.detection_areas.kill_detection_area
            status += f"击杀检测区域:\n"
            if hasattr(kill_area, 'x'):
                status += f"  位置: ({kill_area.x}, {kill_area.y})\n"
                status += f"  大小: {kill_area.width}x{kill_area.height}\n"
                status += f"  状态: {'启用' if kill_area.enabled else '禁用'}\n\n"
            else:
                status += f"  位置: ({kill_area['x']}, {kill_area['y']})\n"
                status += f"  大小: {kill_area['width']}x{kill_area['height']}\n"
                status += f"  状态: {'启用' if kill_area['enabled'] else '禁用'}\n\n"
            
            # 聊天检测区域
            chat_area = self.config.detection_areas.chat_detection_area
            status += f"聊天检测区域:\n"
            if hasattr(chat_area, 'x'):
                status += f"  位置: ({chat_area.x}, {chat_area.y})\n"
                status += f"  大小: {chat_area.width}x{chat_area.height}\n"
                status += f"  状态: {'启用' if chat_area.enabled else '禁用'}\n\n"
            else:
                status += f"  位置: ({chat_area['x']}, {chat_area['y']})\n"
                status += f"  大小: {chat_area['width']}x{chat_area['height']}\n"
                status += f"  状态: {'启用' if chat_area['enabled'] else '禁用'}\n\n"
        except Exception as e:
            status += f"获取区域信息失败: {e}\n\n"
        
        status += "使用说明:\n"
        status += "1. 点击'快速区域选择'进行可视化选择\n"
        status += "2. 点击'区域管理器'进行高级配置\n"
        status += "3. 建议选择文字清晰、背景对比度高的区域\n"
        status += "4. 可以单独启用/禁用每个检测区域"
        
        self.area_status_text.insert(tk.END, status)
    
    def save_all_config(self):
        """保存所有配置"""
        try:
            # 保存API配置
            self.config.api.deepseek_api_key = self.api_key_var.get()
            self.config.api.api_base_url = self.api_url_var.get()
            self.config.api.model = self.model_var.get()
            self.config.api.temperature = self.temperature_var.get()
            self.config.api.max_tokens = self.max_tokens_var.get()
            self.config.api.timeout = self.timeout_var.get()
            
            # 保存OCR配置
            self.config.ocr.tesseract_path = self.tesseract_path_var.get()
            self.config.ocr.tessdata_path = self.tessdata_path_var.get()
            self.config.ocr.language = self.language_var.get()
            self.config.ocr.detection_interval = self.detection_interval_var.get()
            self.config.ocr.engine = self.ocr_engine_var.get()
            
            # 检测区域配置由区域管理器管理，这里不需要手动保存
            
            # 保存功能配置
            self.config.features.encouragement_enabled = self.encouragement_enabled_var.get()
            self.config.features.auto_response_enabled = self.auto_response_enabled_var.get()
            self.config.features.kill_detection_enabled = self.kill_detection_enabled_var.get()
            self.config.features.chat_detection_enabled = self.chat_detection_enabled_var.get()
            self.config.features.check_kill_after_chat = self.check_kill_after_chat_var.get()
            self.config.features.enable_chat_interaction = self.enable_chat_interaction_var.get()
            self.config.features.debug_mode = self.debug_mode_var.get()
            
            # 保存自定义prompt
            self.config.encouragement.custom_prompt = self.custom_prompt_entry.get('1.0', tk.END).strip()
            
            # 保存冷却时间配置
            self.config.cooldowns.kill_cooldown = self.kill_cooldown_var.get()
            self.config.cooldowns.chat_cooldown = self.chat_cooldown_var.get()
            self.config.cooldowns.encouragement_cooldown = self.encouragement_cooldown_var.get()
            self.config.cooldowns.min_chat_interval = self.min_chat_interval_var.get()
            
            # 保存鼓励语配置
            self.config.encouragement.use_ai_generation = self.use_ai_generation_var.get()
            
            # 保存AI提示词
            self.config.encouragement.ai_prompts.kill_prompt = self.kill_prompt_var.get()
            self.config.encouragement.ai_prompts.death_prompt = self.death_prompt_var.get()
            self.config.encouragement.ai_prompts.general_prompt = self.general_prompt_var.get()
            
            # 保存全局自定义prompt
            self.config.encouragement.custom_prompt = self.global_prompt_text.get('1.0', tk.END).strip()
            
            # 保存到文件
            self.config.save_config()
            messagebox.showinfo("成功", "配置已保存")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def reset_config(self):
        """重置配置为默认值"""
        if messagebox.askyesno("确认", "确定要重置所有配置为默认值吗？"):
            self.config.reset_to_default()
            self.config_window.destroy()
            self.show_config_window()
    
    def import_config(self):
        """导入配置文件"""
        filename = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if filename:
            try:
                self.config.import_config(filename)
                messagebox.showinfo("成功", "配置导入成功")
                self.config_window.destroy()
                self.show_config_window()
            except Exception as e:
                messagebox.showerror("错误", f"导入配置失败: {e}")
    
    def export_config(self):
        """导出配置文件"""
        filename = filedialog.asksaveasfilename(
            title="保存配置文件",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if filename:
            try:
                self.config.export_config(filename)
                messagebox.showinfo("成功", f"配置已导出到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"导出配置失败: {e}")
    
    def validate_config(self):
        """验证配置"""
        if self.config.validate_config():
            messagebox.showinfo("验证结果", "配置验证通过！")
        else:
            messagebox.showwarning("验证结果", "配置验证失败，请检查错误信息。")
    
    def get_detection_areas_from_manager(self):
        """从区域管理器获取检测区域配置"""
        # 这个方法可以被其他模块调用来获取最新的检测区域配置
        return {
            'kill_detection_area': self.config.detection_areas.kill_detection_area,
            'chat_detection_area': self.config.detection_areas.chat_detection_area
        }
    
    def update_detection_areas_from_manager(self, areas):
        """从区域管理器更新检测区域配置"""
        if 'kill_detection_area' in areas:
            self.config.detection_areas.kill_detection_area = areas['kill_detection_area']
        if 'chat_detection_area' in areas:
            self.config.detection_areas.chat_detection_area = areas['chat_detection_area']
        
        # 刷新显示
        self.refresh_detection_status()
        self.refresh_area_status()

if __name__ == "__main__":
    # 配置操作面板
    root = tk.Tk()
    root.title("配置操作面板")
    root.geometry("420x260")
    
    cfg = Config()
    
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
    
    # 按钮区
    btns = ttk.Frame(main_frame)
    btns.pack(fill=tk.X, pady=6)
    
    def open_config_manager():
        try:
            manager = ConfigManager(root, cfg)
            manager.show_config_window()
        except Exception as e:
            messagebox.showerror("错误", f"打开配置管理器失败: {e}")
    
    def open_area_manager():
        try:
            am = AreaManager(root, cfg)
            am.show_area_manager()
        except Exception as e:
            messagebox.showerror("错误", f"打开区域管理器失败: {e}")
    
    def quick_pick(area_type: str):
        try:
            picker = AreaPicker(root, cfg, area_type)
            picker.start_picking()
        except Exception as e:
            messagebox.showerror("错误", f"选择区域失败: {e}")
    
    ttk.Button(btns, text="打开配置管理器", command=open_config_manager).pack(side=tk.LEFT, padx=5)
    ttk.Button(btns, text="打开区域管理器", command=open_area_manager).pack(side=tk.LEFT, padx=5)
    
    # 快速选择
    quick = ttk.LabelFrame(main_frame, text="快速区域操作")
    quick.pack(fill=tk.X, pady=10)
    ttk.Button(quick, text="选择击杀区域", command=lambda: quick_pick('kill')).pack(side=tk.LEFT, padx=5, pady=6)
    ttk.Button(quick, text="选择聊天区域", command=lambda: quick_pick('chat')).pack(side=tk.LEFT, padx=5, pady=6)
    
    # 当前区域展示
    info = ttk.LabelFrame(main_frame, text="当前区域")
    info.pack(fill=tk.BOTH, expand=True)
    info_text = tk.Text(info, height=6, width=48)
    sb = ttk.Scrollbar(info, orient=tk.VERTICAL, command=info_text.yview)
    info_text.configure(yscrollcommand=sb.set)
    info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    
    def refresh_info():
        try:
            kill_area = cfg.get_ocr_area('kill') if hasattr(cfg, 'get_ocr_area') else {}
            chat_area = cfg.get_ocr_area('chat') if hasattr(cfg, 'get_ocr_area') else {}
            text = "当前区域配置:\n\n"
            text += f"击杀区域: x={kill_area.get('x',0)}, y={kill_area.get('y',0)}, w={kill_area.get('width',0)}, h={kill_area.get('height',0)}, 启用={kill_area.get('enabled',False)}\n"
            text += f"聊天区域: x={chat_area.get('x',0)}, y={chat_area.get('y',0)}, w={chat_area.get('width',0)}, h={chat_area.get('height',0)}, 启用={chat_area.get('enabled',False)}\n"
            info_text.delete('1.0', tk.END)
            info_text.insert(tk.END, text)
        except Exception as e:
            info_text.delete('1.0', tk.END)
            info_text.insert(tk.END, f"读取失败: {e}")
    
    # 操作区
    ops = ttk.Frame(main_frame)
    ops.pack(fill=tk.X, pady=6)
    ttk.Button(ops, text="刷新", command=refresh_info).pack(side=tk.LEFT, padx=5)
    ttk.Button(ops, text="退出", command=root.destroy).pack(side=tk.RIGHT, padx=5)
    
    refresh_info()
    root.mainloop()
