# -*- coding: utf-8 -*-
"""
Dota聊天机器人主程序
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import pyautogui
from config import Config, ConfigManager, AreaPicker, AreaManager
from ocr_detector import OCRDetector
from deepseek_api import DeepSeekAPI

class DotaChatBot:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dota聊天机器人")
        self.root.geometry("800x600")
        
        # 禁用PyAutoGUI安全机制
        pyautogui.FAILSAFE = False
        
        # 初始化配置和组件
        self.config = Config()
        self.ocr_detector = OCRDetector(self.config)
        self.deepseek_api = DeepSeekAPI(self.config)
        self.config_manager = ConfigManager(self.root, self.config)
        self.area_manager = AreaManager(self.root, self.config)
        
        # 运行状态
        self.running = False
        self.detection_thread = None
        
        # 聊天间隔控制
        self.last_chat_time = 0
        
        # 创建界面
        self.create_ui()
        
        # 启动检测线程
        self.start_detection()
        
    def create_ui(self):
        """创建用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建标签页
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 主控制标签页
        self.create_main_tab(notebook)
        
        # 设置标签页
        self.create_settings_tab(notebook)
        
        # 配置管理标签页
        self.create_config_tab(notebook)
        
        # 日志标签页
        self.create_log_tab(notebook)
        
    def create_main_tab(self, parent):
        """创建主控制标签页"""
        main_tab = ttk.Frame(parent)
        parent.add(main_tab, text="主控制")
        
        # 状态显示
        status_frame = ttk.LabelFrame(main_tab, text="运行状态")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="状态: 已停止", foreground="red")
        self.status_label.pack(pady=5)
        
        # 控制按钮
        control_frame = ttk.Frame(main_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_btn = ttk.Button(control_frame, text="开始运行", command=self.start_bot)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="停止运行", command=self.stop_bot, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # 功能开关
        switch_frame = ttk.LabelFrame(main_tab, text="功能开关")
        switch_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 安全获取配置值
        encouragement_enabled = getattr(self.config.features, 'encouragement_enabled', True) if hasattr(self.config, 'features') else True
        auto_response_enabled = getattr(self.config.features, 'auto_response_enabled', True) if hasattr(self.config, 'features') else True
        
        self.encouragement_var = tk.BooleanVar(value=encouragement_enabled)
        ttk.Checkbutton(switch_frame, text="启用鼓励语", 
                       variable=self.encouragement_var,
                       command=self.toggle_encouragement).pack(anchor=tk.W, padx=5, pady=2)
        
        self.auto_response_var = tk.BooleanVar(value=auto_response_enabled)
        ttk.Checkbutton(switch_frame, text="启用自动回复", 
                       variable=self.auto_response_var,
                       command=self.toggle_auto_response).pack(anchor=tk.W, padx=5, pady=2)
        
        # 手动输入区域
        manual_frame = ttk.LabelFrame(main_tab, text="手动输入")
        manual_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 聊天模式选择
        chat_mode_frame = ttk.Frame(manual_frame)
        chat_mode_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(chat_mode_frame, text="聊天模式:").pack(side=tk.LEFT, padx=5)
        
        self.chat_mode_var = tk.StringVar(value="enter")
        ttk.Radiobutton(chat_mode_frame, text="Enter键聊天", 
                       variable=self.chat_mode_var, value="enter").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(chat_mode_frame, text="直接输入", 
                       variable=self.chat_mode_var, value="direct").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(chat_mode_frame, text="超快速", 
                       variable=self.chat_mode_var, value="fast").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(manual_frame, text="输入消息:").pack(anchor=tk.W, padx=5, pady=2)
        
        self.message_entry = ttk.Entry(manual_frame, width=50)
        self.message_entry.pack(fill=tk.X, padx=5, pady=2)
        self.message_entry.bind('<Return>', self.send_manual_message)
        
        ttk.Button(manual_frame, text="发送消息", 
                  command=self.send_manual_message).pack(anchor=tk.W, padx=5, pady=5)
        
        # 聊天测试按钮
        test_frame = ttk.Frame(manual_frame)
        test_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 核心测试按钮
        ttk.Button(test_frame, text="测试聊天识别", 
                  command=self.test_chat_recognition).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(test_frame, text="测试击杀检测", 
                  command=self.test_kill_detection).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(test_frame, text="测试OCR对话", 
                  command=self.test_ocr_chat).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(test_frame, text="测试游戏窗口", 
                  command=self.test_game_window).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(test_frame, text="OCR引擎测试", 
                  command=self.test_ocr_engines).pack(side=tk.LEFT, padx=5)
        
    def create_settings_tab(self, parent):
        """创建设置标签页"""
        settings_tab = ttk.Frame(parent)
        parent.add(settings_tab, text="设置")
        
        # API设置
        api_frame = ttk.LabelFrame(settings_tab, text="API设置")
        api_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(api_frame, text="DeepSeek API密钥:").pack(anchor=tk.W, padx=5, pady=2)
        api_key = getattr(self.config.api, 'deepseek_api_key', '') if hasattr(self.config, 'api') else ''
        self.api_key_var = tk.StringVar(value=api_key)
        api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, width=50, show="*")
        api_key_entry.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(api_frame, text="保存API密钥", 
                  command=self.save_api_key).pack(anchor=tk.W, padx=5, pady=5)
        
        ttk.Button(api_frame, text="测试API连接", 
                  command=self.test_api).pack(anchor=tk.W, padx=5, pady=2)
        
        # 区域设置
        area_frame = ttk.LabelFrame(settings_tab, text="检测区域设置")
        area_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(area_frame, text="设置击杀检测区域", 
                  command=lambda: self.select_area('kill')).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(area_frame, text="设置聊天检测区域", 
                  command=lambda: self.select_area('chat')).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(area_frame, text="区域管理器", 
                  command=self.open_area_manager).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 检测功能说明
        info_frame = ttk.LabelFrame(settings_tab, text="检测功能说明")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        info_text = """
检测模式：交替检测模式
1. 检测聊天区域 → 等待3秒 → 检测击杀区域 → 等待3秒 → 循环
2. 击杀检测：必须有字符才认为存在击杀事件
   - 绿色区域+字符 = 我方击杀对方
   - 红色区域+字符 = 我方被击杀
   - 无字符 = 无击杀事件
3. OCR对话：将OCR识别结果直接传递给DeepSeek进行对话
   - 使用独立的OCR对话prompt配置
   - 支持原始文本和中文文本选择
   - 可配置回复长度限制
   - 智能分析游戏内容并回复
4. 高级OCR引擎：支持多种OCR模型
   - Tesseract: 谷歌开源OCR，通用性强
   - EasyOCR: 中文识别效果好，基于PyTorch
   - PaddleOCR: 百度开发，中文识别精度高
5. 建议：先使用配置管理器设置检测区域和OCR引擎，然后启动机器人
        """
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(padx=5, pady=5)
        
    def create_log_tab(self, parent):
        """创建日志标签页"""
        log_tab = ttk.Frame(parent)
        parent.add(log_tab, text="日志")
        
        # 日志显示区域
        self.log_text = scrolledtext.ScrolledText(log_tab, height=20, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 清空日志按钮
        ttk.Button(log_tab, text="清空日志", 
                  command=self.clear_log).pack(padx=5, pady=5)
    
    def create_config_tab(self, parent):
        """创建配置管理标签页"""
        config_tab = ttk.Frame(parent)
        parent.add(config_tab, text="配置管理")
        
        # 配置管理按钮
        ttk.Button(config_tab, text="打开配置管理器", 
                  command=self.open_config_manager).pack(padx=10, pady=10)
        
        # 快速配置区域
        quick_frame = ttk.LabelFrame(config_tab, text="快速配置")
        quick_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # API密钥快速设置
        ttk.Label(quick_frame, text="DeepSeek API密钥:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        api_key = getattr(self.config.api, 'deepseek_api_key', '') if hasattr(self.config, 'api') else ''
        self.quick_api_key_var = tk.StringVar(value=api_key)
        ttk.Entry(quick_frame, textvariable=self.quick_api_key_var, width=50, show="*").grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(quick_frame, text="保存", command=self.save_quick_api_key).grid(row=0, column=2, padx=5, pady=5)
        
        # 功能开关快速设置
        switch_frame = ttk.Frame(quick_frame)
        switch_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)
        
        encouragement_enabled = getattr(self.config.features, 'encouragement_enabled', True) if hasattr(self.config, 'features') else True
        auto_response_enabled = getattr(self.config.features, 'auto_response_enabled', True) if hasattr(self.config, 'features') else True
        
        self.quick_encouragement_var = tk.BooleanVar(value=encouragement_enabled)
        ttk.Checkbutton(switch_frame, text="启用鼓励语", 
                       variable=self.quick_encouragement_var,
                       command=self.toggle_quick_encouragement).pack(side=tk.LEFT, padx=5)
        
        self.quick_auto_response_var = tk.BooleanVar(value=auto_response_enabled)
        ttk.Checkbutton(switch_frame, text="启用自动回复", 
                       variable=self.quick_auto_response_var,
                       command=self.toggle_quick_auto_response).pack(side=tk.LEFT, padx=5)
        
        # 配置信息显示
        info_frame = ttk.LabelFrame(config_tab, text="当前配置信息")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.config_info_text = tk.Text(info_frame, height=15, width=80)
        config_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.config_info_text.yview)
        self.config_info_text.configure(yscrollcommand=config_scrollbar.set)
        
        self.config_info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        config_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 刷新配置信息
        self.refresh_config_info()
        
    def log_message(self, message):
        """记录日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # 限制日志长度
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 1000:
            self.log_text.delete("1.0", "500.0")
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete("1.0", tk.END)
    
    def start_bot(self):
        """启动机器人"""
        # 检查API密钥
        api_key = getattr(self.config.api, 'deepseek_api_key', None) if hasattr(self.config, 'api') else None
        if not api_key:
            messagebox.showerror("错误", "请先设置DeepSeek API密钥")
            return
        
        self.running = True
        self.status_label.config(text="状态: 运行中", foreground="green")
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.log_message("机器人已启动")
    
    def stop_bot(self):
        """停止机器人"""
        self.running = False
        self.status_label.config(text="状态: 已停止", foreground="red")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        self.log_message("机器人已停止")
    
    def start_detection(self):
        """启动检测线程 - 交替检测模式"""
        def detection_loop():
            detection_cycle = 0  # 检测周期计数器：0=聊天区域，1=击杀区域
            
            while True:
                if self.running:
                    try:
                        # 只有在游戏窗口激活时才进行检测
                        if self.is_game_window_active():
                            if detection_cycle == 0:
                                # 检测聊天区域
                                self.log_message("=== 检测聊天区域 ===")
                                chat_event = self.ocr_detector.detect_chat_message()
                                if chat_event:
                                    self.handle_chat_event(chat_event)
                                else:
                                    self.log_message("聊天区域无新消息")
                                
                                # 切换到击杀区域检测
                                detection_cycle = 1
                                self.log_message("等待3秒后检测击杀区域...")
                                time.sleep(3)
                                
                            else:
                                # 检测击杀区域
                                self.log_message("=== 检测击杀区域 ===")
                                kill_event = self.ocr_detector.detect_kill_event()
                                if kill_event:
                                    self.log_message(f"✓ 检测到击杀事件: {kill_event['type']}")
                                    self.handle_kill_event(kill_event)
                                else:
                                    self.log_message("击杀区域无字符，不存在击杀事件")
                                
                                # 切换到聊天区域检测
                                detection_cycle = 0
                                self.log_message("等待3秒后检测聊天区域...")
                                time.sleep(3)
                        else:
                            # 游戏窗口未激活时，减少日志输出
                            pass
                            
                    except Exception as e:
                        self.log_message(f"检测错误: {e}")
                        # 出错时也等待3秒再继续
                        time.sleep(3)
                else:
                    # 机器人未运行时，等待1秒再检查
                    time.sleep(1)
        
        self.detection_thread = threading.Thread(target=detection_loop, daemon=True)
        self.detection_thread.start()
    
    def handle_kill_event(self, event):
        """处理击杀事件 - 发送鼓励语并与队友交流"""
        if event['type'] == 'kill':
            self.log_message(f"检测到击杀: {event['text']}")
            
            if self.encouragement_var.get():
                # 生成鼓励语
                encouragement = self.deepseek_api.generate_encouragement('kill')
                if encouragement:
                    self.send_chat_message(encouragement)
                    self.log_message(f"发送鼓励语: {encouragement}")
                
        
        elif event['type'] == 'death':
            self.log_message(f"检测到死亡: {event['text']}")
            
            if self.encouragement_var.get():
                # 生成安慰语
                encouragement = self.deepseek_api.generate_encouragement('death')
                if encouragement:
                    self.send_chat_message(encouragement)
                    self.log_message(f"发送安慰语: {encouragement}")
                
    
    def handle_chat_event(self, event):
        """处理聊天事件 - 将OCR识别结果直接传递给DeepSeek进行对话"""
        # 显示识别效果提示
        ocr_quality = event.get('ocr_quality', '未知')
        chinese_text = event.get('chinese_text', '')
        has_chinese = event.get('has_chinese', False)
        raw_text = event.get('text', '')
        
        # 详细记录识别到的内容
        self.log_message(f"=== OCR识别结果 ===")
        self.log_message(f"原始识别文本: {raw_text}")
        self.log_message(f"提取的中文内容: {chinese_text if chinese_text else '无'}")
        self.log_message(f"识别质量评估: {ocr_quality}")
        self.log_message(f"包含中文字符: {'是' if has_chinese else '否'}")
        self.log_message(f"文本长度: {len(raw_text)} 字符")
        
        # 将OCR识别结果直接传递给DeepSeek进行对话
        if self.auto_response_var.get():
            # 优先使用中文内容，如果没有中文则使用原始文本
            input_text = chinese_text if chinese_text else raw_text
            
            if input_text and len(input_text.strip()) > 0:
                self.log_message(f"开始OCR对话，输入内容: {input_text}")
                
                # 使用OCR识别结果与DeepSeek API对话
                response = self.ocr_chat_with_ai(input_text)
                if response and not response.startswith("API请求失败"):
                    self.log_message(f"OCR对话回复: {response}")
                    self.send_chat_message(response)
                    self.log_message(f"✓ 已发送OCR对话回复到游戏")
                else:
                    self.log_message(f"✗ OCR对话回复生成失败: {response}")
            else:
                self.log_message("⚠ OCR识别无有效内容，跳过对话")
        else:
            self.log_message("⚠ 自动回复功能已禁用")
        
        # 注意：现在使用交替检测模式，聊天后不再单独检测击杀区域
    
    def ocr_chat_with_ai(self, ocr_text):
        """使用OCR识别结果与DeepSeek进行对话"""
        try:
            # 使用默认的OCR对话prompt
            prompt = "你是一个专业的Dota 2游戏助手。请根据OCR识别到的游戏内容进行智能回复。要求：1. 回复要简洁有力，不超过30字；2. 使用专业游戏术语；3. 保持积极正面的态度；4. 针对识别到的内容给出合适的建议或回应。"
            
            # 构建用户消息
            user_message = f"请根据以下OCR识别内容进行智能回复：\n{ocr_text}"
            
            # 调用DeepSeek API，使用系统prompt
            response = self.deepseek_api._make_api_request(user_message, prompt)
            
            if response and not response.startswith("API请求失败"):
                # 限制回复长度
                max_length = 30
                if len(response) > max_length:
                    response = response[:max_length] + "..."
                return response
            else:
                return f"OCR对话失败: {response}"
                
        except Exception as e:
            self.log_message(f"OCR对话出错: {e}")
            return f"OCR对话出错: {e}"
    
    def is_game_window_active(self):
        """检查游戏窗口是否激活且在前台"""
        try:
            import win32gui
            import win32con
            
            # 获取当前前台窗口
            foreground_window = win32gui.GetForegroundWindow()
            if not foreground_window:
                return False
            
            # 获取前台窗口标题
            window_title = win32gui.GetWindowText(foreground_window)
            
            # 检查是否是Dota 2窗口
            if any(keyword in window_title.lower() for keyword in ['dota', 'dota2']):
                self.log_message(f"检测到游戏窗口激活: {window_title}")
                return True
            
            # 如果前台窗口不是Dota 2，返回False
            self.log_message(f"前台窗口不是Dota 2: {window_title}")
            return False
            
        except ImportError:
            # 如果没有win32gui，使用简单的方法
            self.log_message("未安装win32gui，跳过窗口检测")
            return True
        except Exception as e:
            self.log_message(f"窗口检测失败: {e}")
            return False
    
    def send_chat_message(self, message):
        """发送聊天消息到游戏 - 使用剪切板粘贴方式，带聊天间隔控制"""
        try:
            # 检查聊天间隔
            current_time = time.time()
            min_interval = getattr(self.config.cooldowns, 'min_chat_interval', 2.0)
            if current_time - self.last_chat_time < min_interval:
                remaining_time = min_interval - (current_time - self.last_chat_time)
                self.log_message(f"聊天间隔未到，还需等待 {remaining_time:.1f} 秒")
                return
            
            # 检查游戏窗口是否激活
            if not self.is_game_window_active():
                self.log_message("游戏窗口未激活，跳过发送消息")
                return
            
            # 再次确认游戏窗口激活（双重检查）
            time.sleep(0.1)
            if not self.is_game_window_active():
                self.log_message("游戏窗口检测失败，取消发送消息")
                return
            
            chat_mode = getattr(self, 'chat_mode_var', None)
            if chat_mode:
                chat_mode = chat_mode.get()
            else:
                chat_mode = "enter"  # 默认使用Enter键模式
            
            self.log_message(f"准备发送消息到游戏: {message}")
            
            if chat_mode == "enter":
                # Enter键聊天模式 - 快速流程
                # 1. 将消息复制到剪切板
                self.copy_to_clipboard(message)
                time.sleep(0.05)  # 减少等待时间
                
                # 2. 按Enter键打开聊天框
                pyautogui.press('enter')
                time.sleep(0.2)  # 减少等待时间
                
                # 3. 直接粘贴消息
                pyautogui.hotkey('ctrl', 'v')  # 粘贴
                time.sleep(0.1)  # 减少等待时间
                
                # 4. 按Enter键发送并关闭对话框
                pyautogui.press('enter')
                time.sleep(0.1)  # 减少等待时间
            elif chat_mode == "fast":
                # 超快速模式 - 最小延迟
                # 1. 将消息复制到剪切板
                self.copy_to_clipboard(message)
                
                # 2. 按Enter键打开聊天框
                pyautogui.press('enter')
                time.sleep(0.1)  # 最小等待时间
                
                # 3. 直接粘贴消息
                pyautogui.hotkey('ctrl', 'v')  # 粘贴
                
                # 4. 按Enter键发送并关闭对话框
                pyautogui.press('enter')
            else:
                # 直接输入模式 - 也使用剪切板
                self.copy_to_clipboard(message)
                time.sleep(0.1)
                pyautogui.hotkey('ctrl', 'v')  # 粘贴
                pyautogui.press('enter')
            
            # 更新最后聊天时间
            self.last_chat_time = time.time()
            self.log_message(f"✓ 消息已发送到游戏: {message}")
        except Exception as e:
            self.log_message(f"发送消息失败: {e}")
    
    def copy_to_clipboard(self, text):
        """将文本复制到剪切板 - 优化版本"""
        try:
            # 优先使用pyperclip，更快
            import pyperclip
            pyperclip.copy(text)
            # 不输出日志以减少延迟
        except ImportError:
            # 备用方法：使用tkinter
            try:
                import tkinter as tk
                root = tk.Tk()
                root.withdraw()  # 隐藏窗口
                root.clipboard_clear()
                root.clipboard_append(text)
                root.update()  # 确保剪切板更新
                root.destroy()
            except Exception as e:
                self.log_message(f"复制到剪切板失败: {e}")
        except Exception as e:
            self.log_message(f"pyperclip复制失败: {e}")
            # 最后备用方法：使用tkinter
            try:
                import tkinter as tk
                root = tk.Tk()
                root.withdraw()
                root.clipboard_clear()
                root.clipboard_append(text)
                root.update()
                root.destroy()
            except Exception as e2:
                self.log_message(f"所有剪切板方法都失败: {e2}")
    
    def send_manual_message(self, event=None):
        """发送手动输入的消息"""
        message = self.message_entry.get().strip()
        if message:
            self.send_chat_message(message)
            self.message_entry.delete(0, tk.END)
    
    def test_game_window(self):
        """测试游戏窗口检测"""
        try:
            is_active = self.is_game_window_active()
            if is_active:
                self.log_message("✓ 游戏窗口检测正常，可以发送消息")
            else:
                self.log_message("✗ 游戏窗口未检测到，可能无法发送消息")
        except Exception as e:
            self.log_message(f"游戏窗口检测测试失败: {e}")
    
    def test_chat_recognition(self):
        """测试聊天识别功能"""
        try:
            self.log_message("开始测试聊天识别功能...")
            
            # 检查游戏窗口是否激活
            if not self.is_game_window_active():
                self.log_message("请先打开Dota2游戏窗口并确保窗口在前台")
                return
            
            # 检查聊天检测区域是否设置
            chat_area = getattr(self.config.detection_areas, 'chat_detection_area', {}) if hasattr(self.config, 'detection_areas') else {}
            if not chat_area.get('enabled', False):
                self.log_message("⚠ 聊天检测区域未设置，请先设置聊天检测区域")
                return
            
            self.log_message("正在检测聊天区域中的文字...")
            
            # 检测聊天消息
            chat_event = self.ocr_detector.detect_chat_message()
            if chat_event:
                self.log_message("✓ 检测到聊天内容，开始处理...")
                self.handle_chat_event(chat_event)
            else:
                self.log_message("⚠ 未检测到聊天内容")
                self.log_message("提示：请确保聊天区域中有中文文字，并且聊天检测区域设置正确")
            
            self.log_message("✓ 聊天识别测试完成")
            
        except Exception as e:
            self.log_message(f"聊天识别测试失败: {e}")
    
    def test_kill_detection(self):
        """测试击杀检测功能 - 验证必须有字符才认为有击杀"""
        try:
            self.log_message("开始测试击杀检测功能...")
            self.log_message("检测规则：击杀区域必须有字符才认为存在击杀事件")
            
            # 检查游戏窗口是否激活
            if not self.is_game_window_active():
                self.log_message("请先打开Dota2游戏窗口并确保窗口在前台")
                return
            
            # 检查击杀检测区域是否设置
            kill_area = getattr(self.config.detection_areas, 'kill_detection_area', {}) if hasattr(self.config, 'detection_areas') else {}
            if not kill_area.get('enabled', False):
                self.log_message("⚠ 击杀检测区域未设置，请先设置击杀检测区域")
                return
            
            self.log_message("✓ 击杀检测区域已设置")
            self.log_message("正在检测击杀区域中的字符...")
            
            # 检测击杀事件
            kill_event = self.ocr_detector.detect_kill_event()
            if kill_event:
                self.log_message(f"✓ 检测到击杀事件: {kill_event['type']}")
                self.log_message(f"检测到的文本: '{kill_event['text']}'")
                self.log_message(f"置信度: {kill_event['confidence']}")
                self.log_message(f"颜色检测: {kill_event.get('color_detected', False)}")
                
                # 处理击杀事件
                self.handle_kill_event(kill_event)
            else:
                self.log_message("击杀区域无字符，不存在击杀事件")
                self.log_message("说明：击杀区域必须检测到字符才会认为存在击杀事件")
            
            self.log_message("✓ 击杀检测测试完成")
            self.log_message("提示：如果击杀区域没有显示任何文字，则不会触发击杀事件")
            
        except Exception as e:
            self.log_message(f"击杀检测测试失败: {e}")
    
    def test_ocr_chat(self):
        """测试OCR对话功能 - 使用OCR识别结果直接与DeepSeek对话"""
        try:
            self.log_message("开始测试OCR对话功能...")
            self.log_message("功能：将OCR识别结果直接传递给DeepSeek进行对话")
            
            # 检查游戏窗口是否激活
            if not self.is_game_window_active():
                self.log_message("请先打开Dota2游戏窗口并确保窗口在前台")
                return
            
            # 检查聊天检测区域是否设置
            chat_area = getattr(self.config.detection_areas, 'chat_detection_area', {}) if hasattr(self.config, 'detection_areas') else {}
            if not chat_area.get('enabled', False):
                self.log_message("⚠ 聊天检测区域未设置，请先设置聊天检测区域")
                return
            
            self.log_message("✓ 聊天检测区域已设置")
            self.log_message(f"聊天区域坐标: ({chat_area.get('x', 0)}, {chat_area.get('y', 0)})")
            self.log_message(f"聊天区域大小: {chat_area.get('width', 0)}x{chat_area.get('height', 0)}")
            
            # 检查API密钥
            api_key = getattr(self.config.api, 'deepseek_api_key', '') if hasattr(self.config, 'api') else ''
            if not api_key:
                self.log_message("⚠ DeepSeek API密钥未设置，请先设置API密钥")
                return
            
            self.log_message("✓ DeepSeek API密钥已设置")
            
            # 显示OCR对话配置
            self.log_message(f"OCR对话配置:")
            self.log_message(f"  - 启用状态: 已启用")
            self.log_message(f"  - 文本选择: 优先中文，无中文则使用原始文本")
            self.log_message(f"  - 最大回复长度: 30字")
            self.log_message(f"  - Prompt: 使用默认专业Dota 2助手Prompt")
            
            self.log_message("正在检测聊天区域中的内容...")
            
            # 检测聊天消息
            chat_event = self.ocr_detector.detect_chat_message()
            if chat_event:
                self.log_message("✓ 检测到聊天内容，开始OCR对话...")
                
                # 处理聊天事件（会调用OCR对话）
                self.handle_chat_event(chat_event)
            else:
                self.log_message("⚠ 聊天区域无新内容")
                self.log_message("提示：请确保聊天区域中有文字内容，并且聊天检测区域设置正确")
                
                # 模拟一个聊天事件进行测试
                self.log_message("\n=== 模拟OCR对话测试 ===")
                fake_chat_event = {
                    'type': 'chat',
                    'text': '队友击杀了敌方英雄',
                    'chinese_text': '队友击杀了敌方英雄',
                    'has_chinese': True,
                    'ocr_quality': '良好',
                    'timestamp': time.time()
                }
                
                self.log_message("使用模拟OCR内容测试对话...")
                self.handle_chat_event(fake_chat_event)
            
            self.log_message("✓ OCR对话测试完成")
            self.log_message("说明：OCR识别结果会直接传递给DeepSeek进行智能对话")
            
        except Exception as e:
            self.log_message(f"OCR对话测试失败: {e}")
    
    def test_ocr_engines(self):
        """测试OCR引擎"""
        try:
            from test_ocr_engines import OCREngineTester
            
            self.log_message("启动OCR引擎测试工具...")
            
            # 创建OCR引擎测试窗口
            tester = OCREngineTester()
            tester.run()
            
            self.log_message("OCR引擎测试完成")
            
        except Exception as e:
            self.log_message(f"OCR引擎测试失败: {e}")
    
    def select_area(self, area_type):
        """选择检测区域"""
        picker = AreaPicker(self.root, self.config, area_type)
        picker.start_picking()
    
    def save_api_key(self):
        """保存API密钥"""
        api_key = self.api_key_var.get().strip()
        if api_key:
            if hasattr(self.config, 'api'):
                self.config.api.deepseek_api_key = api_key
            self.config.save_config()
            if hasattr(self.deepseek_api, 'api_key'):
                self.deepseek_api.api_key = api_key
            if hasattr(self.deepseek_api, 'headers'):
                self.deepseek_api.headers["Authorization"] = f"Bearer {api_key}"
            messagebox.showinfo("成功", "API密钥已保存")
        else:
            messagebox.showerror("错误", "请输入API密钥")
    
    def test_api(self):
        """测试API连接"""
        success, message = self.deepseek_api.test_api_connection()
        if success:
            messagebox.showinfo("成功", message)
        else:
            messagebox.showerror("失败", message)
    
    def toggle_encouragement(self):
        """切换鼓励语功能"""
        if hasattr(self.config, 'features'):
            self.config.features.encouragement_enabled = self.encouragement_var.get()
        self.config.save_config()
    
    def toggle_auto_response(self):
        """切换自动回复功能"""
        if hasattr(self.config, 'features'):
            self.config.features.auto_response_enabled = self.auto_response_var.get()
        self.config.save_config()
    
    def open_config_manager(self):
        """打开配置管理器"""
        self.config_manager.show_config_window()
    
    def open_area_manager(self):
        """打开区域管理器"""
        self.area_manager.show_area_manager()
    
    def save_quick_api_key(self):
        """保存快速API密钥设置"""
        api_key = self.quick_api_key_var.get().strip()
        if api_key:
            if hasattr(self.config, 'api'):
                self.config.api.deepseek_api_key = api_key
            self.config.save_config()
            if hasattr(self.deepseek_api, 'api_key'):
                self.deepseek_api.api_key = api_key
            if hasattr(self.deepseek_api, 'headers'):
                self.deepseek_api.headers["Authorization"] = f"Bearer {api_key}"
            messagebox.showinfo("成功", "API密钥已保存")
            self.refresh_config_info()
        else:
            messagebox.showerror("错误", "请输入API密钥")
    
    def toggle_quick_encouragement(self):
        """切换快速鼓励语功能"""
        if hasattr(self.config, 'features'):
            self.config.features.encouragement_enabled = self.quick_encouragement_var.get()
        self.config.save_config()
        self.refresh_config_info()
    
    def toggle_quick_auto_response(self):
        """切换快速自动回复功能"""
        if hasattr(self.config, 'features'):
            self.config.features.auto_response_enabled = self.quick_auto_response_var.get()
        self.config.save_config()
        self.refresh_config_info()
    
    def refresh_config_info(self):
        """刷新配置信息显示"""
        self.config_info_text.delete("1.0", tk.END)
        
        # 安全获取配置信息
        def safe_get(obj, attr, default='未知'):
            if hasattr(obj, attr):
                value = getattr(obj, attr)
                if hasattr(value, '__dict__'):
                    return '对象'
                return str(value)
            return default
        
        # API配置
        api_key = safe_get(self.config.api, 'deepseek_api_key', '') if hasattr(self.config, 'api') else ''
        api_url = safe_get(self.config.api, 'api_base_url', '') if hasattr(self.config, 'api') else ''
        model = safe_get(self.config.api, 'model', '') if hasattr(self.config, 'api') else ''
        temperature = safe_get(self.config.api, 'temperature', '') if hasattr(self.config, 'api') else ''
        max_tokens = safe_get(self.config.api, 'max_tokens', '') if hasattr(self.config, 'api') else ''
        timeout = safe_get(self.config.api, 'timeout', '') if hasattr(self.config, 'api') else ''
        
        # OCR配置
        tesseract_path = safe_get(self.config.ocr, 'tesseract_path', '') if hasattr(self.config, 'ocr') else ''
        tessdata_path = safe_get(self.config.ocr, 'tessdata_path', '') if hasattr(self.config, 'ocr') else ''
        language = safe_get(self.config.ocr, 'language', '') if hasattr(self.config, 'ocr') else ''
        detection_interval = safe_get(self.config.ocr, 'detection_interval', '') if hasattr(self.config, 'ocr') else ''
        
        # 检测区域 - 安全访问ConfigSection对象
        def safe_get_area(area_obj, key, default=None):
            if hasattr(area_obj, key):
                return getattr(area_obj, key)
            elif hasattr(area_obj, '__dict__') and key in area_obj.__dict__:
                return area_obj.__dict__[key]
            else:
                return default
        
        kill_area = getattr(self.config.detection_areas, 'kill_detection_area', {}) if hasattr(self.config, 'detection_areas') else {}
        chat_area = getattr(self.config.detection_areas, 'chat_detection_area', {}) if hasattr(self.config, 'detection_areas') else {}
        
        # 功能开关
        encouragement_enabled = safe_get(self.config.features, 'encouragement_enabled', '') if hasattr(self.config, 'features') else ''
        auto_response_enabled = safe_get(self.config.features, 'auto_response_enabled', '') if hasattr(self.config, 'features') else ''
        kill_detection_enabled = safe_get(self.config.features, 'kill_detection_enabled', '') if hasattr(self.config, 'features') else ''
        chat_detection_enabled = safe_get(self.config.features, 'chat_detection_enabled', '') if hasattr(self.config, 'features') else ''
        debug_mode = safe_get(self.config.features, 'debug_mode', '') if hasattr(self.config, 'features') else ''
        
        # 冷却时间
        kill_cooldown = safe_get(self.config.cooldowns, 'kill_cooldown', '') if hasattr(self.config, 'cooldowns') else ''
        chat_cooldown = safe_get(self.config.cooldowns, 'chat_cooldown', '') if hasattr(self.config, 'cooldowns') else ''
        encouragement_cooldown = safe_get(self.config.cooldowns, 'encouragement_cooldown', '') if hasattr(self.config, 'cooldowns') else ''
        
        info = f"""当前配置信息:

API配置:
  密钥: {'已设置' if api_key else '未设置'}
  URL: {api_url}
  模型: {model}
  温度: {temperature}
  最大令牌: {max_tokens}
  超时: {timeout}秒

OCR配置:
  Tesseract路径: {tesseract_path}
  Tessdata路径: {tessdata_path}
  语言: {language}
  检测间隔: {detection_interval}秒

检测区域:
  击杀检测: {'启用' if safe_get_area(kill_area, 'enabled', False) else '禁用'}
    位置: ({safe_get_area(kill_area, 'x', 0)}, {safe_get_area(kill_area, 'y', 0)})
    大小: {safe_get_area(kill_area, 'width', 0)}x{safe_get_area(kill_area, 'height', 0)}
  
  聊天检测: {'启用' if safe_get_area(chat_area, 'enabled', False) else '禁用'}
    位置: ({safe_get_area(chat_area, 'x', 0)}, {safe_get_area(chat_area, 'y', 0)})
    大小: {safe_get_area(chat_area, 'width', 0)}x{safe_get_area(chat_area, 'height', 0)}

功能开关:
  鼓励语: {'启用' if encouragement_enabled else '禁用'}
  自动回复: {'启用' if auto_response_enabled else '禁用'}
  击杀检测: {'启用' if kill_detection_enabled else '禁用'}
  聊天检测: {'启用' if chat_detection_enabled else '禁用'}
  调试模式: {'启用' if debug_mode else '禁用'}

冷却时间:
  击杀冷却: {kill_cooldown}秒
  聊天冷却: {chat_cooldown}秒
  鼓励语冷却: {encouragement_cooldown}秒

配置验证: {'通过' if self.config.validate_config() else '失败'}
"""
        
        self.config_info_text.insert(tk.END, info)
    
    def run(self):
        """运行主程序"""
        self.root.mainloop()

if __name__ == "__main__":
    app = DotaChatBot()
    app.run()
