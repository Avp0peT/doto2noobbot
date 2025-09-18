# -*- coding: utf-8 -*-
"""
DeepSeek API集成模块
"""
import requests
import json
import time
from config import Config

class DeepSeekAPI:
    def __init__(self, config):
        self.config = config
        
        # 安全获取API配置
        self.api_key = getattr(config.api, 'deepseek_api_key', '') if hasattr(config, 'api') else ''
        self.base_url = getattr(config.api, 'api_base_url', 'https://api.deepseek.com/v1/chat/completions') if hasattr(config, 'api') else 'https://api.deepseek.com/v1/chat/completions'
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 安全获取鼓励语配置
        self.use_ai_generation = getattr(config.encouragement, 'use_ai_generation', True) if hasattr(config, 'encouragement') else True
        self.force_ai_generation = getattr(config.encouragement, 'force_ai_generation', True) if hasattr(config, 'encouragement') else True
        self.ai_prompts = getattr(config.encouragement, 'ai_prompts', {}) if hasattr(config, 'encouragement') else {}
        self.custom_prompt = getattr(config.encouragement, 'custom_prompt', '') if hasattr(config, 'encouragement') else ''
    
    def generate_encouragement(self, event_type, player_name="队友"):
        """生成鼓励语 - 完全使用AI生成，不使用预设信息"""
        encouragement_enabled = getattr(self.config.features, 'encouragement_enabled', True) if hasattr(self.config, 'features') else True
        if not encouragement_enabled:
            return None
        
        # 强制使用AI生成，不使用任何预设信息
        if self.api_key:
            try:
                ai_message = self._generate_ai_encouragement(event_type)
                if ai_message and not ai_message.startswith("API请求失败"):
                    return ai_message
            except Exception as e:
                print(f"AI生成鼓励语失败: {e}")
        
        # 如果AI生成失败，返回简单的默认消息
        return "加油！" if event_type == 'kill' else "别灰心！"
    
    def _generate_ai_encouragement(self, event_type):
        """使用AI生成鼓励语 - 直接调用API，避免重复应用自定义prompt"""
        if not self.api_key:
            return None
        
        # 构建用户消息
        if event_type == 'kill':
            user_message = "请生成一句简短的中文鼓励语，用于队友完成击杀时的鼓励，要求积极正面，不超过20字。"
        elif event_type == 'death':
            user_message = "请生成一句简短的中文鼓励语，用于队友阵亡时的安慰，要求积极正面，不超过20字。"
        else:
            user_message = "请生成一句简短的中文鼓励语，用于游戏中的一般鼓励，要求积极正面，不超过20字。"
        
        try:
            # 构建系统提示词
            if self.custom_prompt:
                system_prompt = f"你是一个Dota 2游戏助手。{self.custom_prompt} 请用中文回复，保持积极正面的态度。"
            else:
                system_prompt = """你是一个Dota 2游戏助手，专门帮助玩家在游戏中提供建议和鼓励。请用中文回复，保持积极正面的态度，给出实用的游戏建议。"""
            
            data = {
                "model": getattr(self.config.api, 'model', 'deepseek-chat'),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": getattr(self.config.api, 'temperature', 0.7),
                "max_tokens": getattr(self.config.api, 'max_tokens', 200)
            }
            
            # 安全获取超时设置，默认30秒
            timeout = getattr(self.config.api, 'timeout', 30) if hasattr(self.config, 'api') else 30
            
            response = requests.post(
                self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=data,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    if content and not content.startswith("API请求失败") and not content.startswith("网络请求失败"):
                        # 清理响应，移除可能的引号或多余字符
                        content = content.strip().strip('"').strip("'")
                        # 移除字符长度限制，允许发送完整消息
                        return content
            else:
                print(f"API请求失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"AI生成鼓励语时出错: {e}")
        
        return None
    
    def _make_api_request(self, user_message, system_prompt=""):
        """直接调用DeepSeek API进行对话"""
        if not self.api_key:
            return "API密钥未设置"
        
        try:
            # 构建请求数据
            data = {
                "model": getattr(self.config.api, 'model', 'deepseek-chat'),
                "messages": []
            }
            
            # 添加系统提示词（如果提供）
            if system_prompt:
                data["messages"].append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # 添加用户消息
            data["messages"].append({
                "role": "user",
                "content": user_message
            })
            
            # 设置其他参数
            data["temperature"] = getattr(self.config.api, 'temperature', 0.7)
            data["max_tokens"] = getattr(self.config.api, 'max_tokens', 200)
            
            # 发送请求
            timeout = getattr(self.config.api, 'timeout', 30)
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=data,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content'].strip()
                else:
                    return "API响应格式错误"
            else:
                return f"API请求失败: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "API请求超时"
        except requests.exceptions.RequestException as e:
            return f"API请求失败: {e}"
        except Exception as e:
            return f"API请求出错: {e}"
    
    def chat_with_ai(self, message, context=""):
        """与AI对话"""
        if not self.api_key:
            return "请先设置DeepSeek API密钥"
        
        try:
            # 构建提示词
            if self.custom_prompt:
                system_prompt = f"你是一个Dota 2游戏助手。{self.custom_prompt} 请用中文回复，保持积极正面的态度。"
            else:
                system_prompt = """你是一个Dota 2游戏助手，专门帮助玩家在游戏中提供建议和鼓励。请用中文回复，保持积极正面的态度，给出实用的游戏建议。"""
            
            if context:
                system_prompt += f"\n当前游戏情况：{context}"
            
            data = {
                "model": getattr(self.config.api, 'model', 'deepseek-chat'),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": getattr(self.config.api, 'temperature', 0.7),
                "max_tokens": getattr(self.config.api, 'max_tokens', 200)
            }
            
            # 安全获取超时设置，默认30秒
            timeout = getattr(self.config.api, 'timeout', 30) if hasattr(self.config, 'api') else 30
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=data,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"API请求失败: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "请求超时，请稍后重试"
        except requests.exceptions.RequestException as e:
            return f"网络请求失败: {e}"
        except Exception as e:
            return f"处理请求时出错: {e}"
    
    def generate_game_advice(self, game_situation):
        """生成游戏建议"""
        advice_prompts = {
            'early_game': "游戏前期，我们应该如何制定策略？",
            'mid_game': "游戏中期，团战应该注意什么？",
            'late_game': "游戏后期，如何确保胜利？",
            'team_fight': "团战时应该注意哪些要点？",
            'item_build': "当前情况下应该出什么装备？",
            'map_control': "如何更好地控制地图？"
        }
        
        if game_situation in advice_prompts:
            return self.chat_with_ai(advice_prompts[game_situation])
        else:
            return self.chat_with_ai(f"在{game_situation}情况下，我们应该如何应对？")
    
    def analyze_team_performance(self, performance_data):
        """分析团队表现"""
        analysis_prompt = f"""
        请分析以下Dota 2团队表现数据，并给出改进建议：
        
        击杀数：{performance_data.get('kills', 0)}
        死亡数：{performance_data.get('deaths', 0)}
        助攻数：{performance_data.get('assists', 0)}
        经济：{performance_data.get('net_worth', 0)}
        经验：{performance_data.get('experience', 0)}
        
        请从团队配合、个人技术、策略选择等方面给出建议。
        """
        
        return self.chat_with_ai(analysis_prompt)
    
    def test_api_connection(self):
        """测试API连接"""
        try:
            response = self.chat_with_ai("你好，请简单回复一下")
            if "API请求失败" in response or "网络请求失败" in response:
                return False, response
            return True, "API连接正常"
        except Exception as e:
            return False, f"API测试失败: {e}"

# 测试入口
if __name__ == "__main__":
    import tkinter as tk
    from tkinter import ttk, messagebox
    
    # 创建测试窗口
    root = tk.Tk()
    root.title("DeepSeek API测试")
    root.geometry("500x400")
    
    # 创建测试配置
    class TestConfig:
        def __init__(self):
            self.api = {
                'deepseek_api_key': 'sk-test-key',
                'api_base_url': 'https://api.deepseek.com/v1/chat/completions',
                'model': 'deepseek-chat',
                'temperature': 0.7,
                'max_tokens': 200,
                'timeout': 10
            }
            self.encouragement = {
                'use_ai_generation': True,
                'ai_prompts': {
                    'kill_prompt': '请为Dota 2游戏中的队友击杀生成一句简短的中文鼓励语',
                    'death_prompt': '请为Dota 2游戏中的队友死亡生成一句简短的中文安慰语',
                    'general_prompt': '请为Dota 2游戏生成一句简短的中文团队鼓励语'
                },
                'fallback_messages': {
                    'kill_messages': ['太棒了！完成了一次精彩的击杀！'],
                    'death_messages': ['没关系！下次一定会更好的！'],
                    'general_messages': ['团队合作最重要！']
                }
            }
            self.features = {
                'encouragement_enabled': True
            }
    
    config = TestConfig()
    api = DeepSeekAPI(config)
    
    # 创建测试界面
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # API密钥输入
    ttk.Label(frame, text="API密钥:").pack(anchor=tk.W)
    api_key_var = tk.StringVar(value="sk-test-key")
    api_key_entry = ttk.Entry(frame, textvariable=api_key_var, width=50)
    api_key_entry.pack(fill=tk.X, pady=5)
    
    # 测试按钮
    def test_api():
        api.api_key = api_key_var.get()
        success, message = api.test_connection()
        messagebox.showinfo("测试结果", f"{'成功' if success else '失败'}: {message}")
    
    ttk.Button(frame, text="测试API连接", command=test_api).pack(pady=10)
    
    def test_chat():
        api.api_key = api_key_var.get()
        response = api.chat_with_ai("你好，请简单介绍一下自己")
        messagebox.showinfo("聊天测试", f"回复: {response}")
    
    ttk.Button(frame, text="测试聊天功能", command=test_chat).pack(pady=5)
    
    def test_encouragement():
        api.api_key = api_key_var.get()
        message = api.generate_encouragement("kill")
        messagebox.showinfo("鼓励语测试", f"鼓励语: {message}")
    
    ttk.Button(frame, text="测试鼓励语生成", command=test_encouragement).pack(pady=5)
    
    # 状态显示
    status_label = ttk.Label(frame, text="输入API密钥后点击按钮测试功能")
    status_label.pack(pady=10)
    
    # 启动主循环
    root.mainloop()
