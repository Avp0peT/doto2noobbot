# -*- coding: utf-8 -*-
"""
OCR击杀检测模块
"""
import cv2
import numpy as np
import pytesseract
import pyautogui
from PIL import Image
import time
import re
from config import Config
from advanced_ocr import AdvancedOCR

class OCRDetector:
    def __init__(self, config):
        self.config = config
        
        # 初始化高级OCR引擎
        self.advanced_ocr = AdvancedOCR(config)
        
        # 设置tesseract路径（向后兼容）
        pytesseract.pytesseract.tesseract_cmd = config.ocr.tesseract_path
        
        # 击杀相关关键词
        self.kill_keywords = [
            "击杀", "killed", "kills", "击杀者", "first blood", "double kill", 
            "triple kill", "rampage", "godlike", "beyond godlike", "ownage",
            "ultra kill", "monster kill", "wicked sick", "unstoppable",
            "dominating", "mega kill", "legendary", "holy shit"
        ]
        
        # 死亡相关关键词
        self.death_keywords = [
            "死亡", "died", "death", "被击杀", "killed by", "was killed",
            "denied", "自杀", "suicide"
        ]
        
        # 颜色检测配置
        self.color_config = {
            # 绿色击杀颜色范围 (BGR格式) - 我方击杀对方
            'kill_colors': {
                'lower': np.array([0, 100, 0]),    # 深绿色
                'upper': np.array([100, 255, 100]) # 亮绿色
            },
            # 红色死亡颜色范围 (BGR格式) - 我方被击杀
            'death_colors': {
                'lower': np.array([0, 0, 150]),    # 深红色
                'upper': np.array([100, 100, 255]) # 亮红色
            }
        }
        
        self.last_kill_time = 0
        self.last_chat_time = 0
        
    def capture_screen_area(self, area):
        """截取指定区域屏幕"""
        # 安全获取区域参数
        if hasattr(area, 'x'):
            x, y, width, height = area.x, area.y, area.width, area.height
        elif isinstance(area, dict):
            x, y, width, height = area['x'], area['y'], area['width'], area['height']
        else:
            x, y, width, height = 0, 0, 100, 100  # 默认值
        
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    def detect_color_regions(self, image, color_type):
        """检测特定颜色的区域"""
        try:
            if color_type == 'kill':
                lower = self.color_config['kill_colors']['lower']
                upper = self.color_config['kill_colors']['upper']
            elif color_type == 'death':
                lower = self.color_config['death_colors']['lower']
                upper = self.color_config['death_colors']['upper']
            else:
                return None
            
            # 创建颜色掩码
            mask = cv2.inRange(image, lower, upper)
            
            # 查找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # 找到最大的轮廓
                largest_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest_contour)
                
                # 如果区域足够大，认为检测到了该颜色
                if area > 50:  # 最小区域阈值
                    return {
                        'detected': True,
                        'area': area,
                        'contour': largest_contour,
                        'mask': mask
                    }
            
            return {'detected': False, 'area': 0, 'contour': None, 'mask': mask}
            
        except Exception as e:
            print(f"颜色检测失败: {e}")
            return None
    
    def preprocess_image(self, image):
        """图像预处理以提高OCR准确率"""
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 应用高斯模糊减少噪声
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # 应用阈值处理
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 形态学操作
        kernel = np.ones((2, 2), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return processed
    
    def extract_text(self, image):
        """从图像中提取文本 - 使用高级OCR引擎"""
        try:
            # 使用高级OCR引擎
            text = self.advanced_ocr.extract_text(image)
            
            if text:
                print(f"[高级OCR] 使用引擎: {self.advanced_ocr.current_engine}, 文本长度: {len(text)}")
                return text
            
            return ""
        except Exception as e:
            print(f"高级OCR提取失败: {e}")
            # 回退到原始Tesseract方法
            return self._extract_text_fallback(image)
    
    def _extract_text_fallback(self, image):
        """回退的OCR提取方法"""
        try:
            # 预处理图像
            processed = self.preprocess_image(image)
            
            # 尝试多种OCR模式
            texts = []
            
            # 模式1：统一文本块
            try:
                text1 = pytesseract.image_to_string(
                    processed, 
                    lang='eng+chi_sim',
                    config='--psm 6'
                ).strip()
                if text1:
                    texts.append(('psm6', text1))
            except:
                pass
            
            # 模式2：单行文本
            try:
                text2 = pytesseract.image_to_string(
                    processed, 
                    lang='eng+chi_sim',
                    config='--psm 7'
                ).strip()
                if text2 and text2 != text1:
                    texts.append(('psm7', text2))
            except:
                pass
            
            # 模式3：单个字符
            try:
                text3 = pytesseract.image_to_string(
                    processed, 
                    lang='eng+chi_sim',
                    config='--psm 8'
                ).strip()
                if text3 and text3 != text1 and text3 != text2:
                    texts.append(('psm8', text3))
            except:
                pass
            
            # 选择最长的有效文本
            if texts:
                # 按文本长度排序，选择最长的
                texts.sort(key=lambda x: len(x[1]), reverse=True)
                best_text = texts[0][1]
                print(f"[OCR回退] 使用模式 {texts[0][0]}, 文本长度: {len(best_text)}")
                
                # 清理文本
                best_text = re.sub(r'\s+', ' ', best_text.strip())
                return best_text
            
            return ""
        except Exception as e:
            print(f"OCR回退提取失败: {e}")
            return ""
    
    def detect_kill_event(self):
        """检测击杀事件 - 结合颜色检测和文本检测"""
        current_time = time.time()
        
        # 检查冷却时间
        kill_cooldown = getattr(self.config.cooldowns, 'kill_cooldown', 5.0) if hasattr(self.config, 'cooldowns') else 5.0
        if current_time - self.last_kill_time < kill_cooldown:
            return None
        
        try:
            # 安全获取击杀检测区域
            kill_area_config = getattr(self.config.detection_areas, 'kill_detection_area', {}) if hasattr(self.config, 'detection_areas') else {}
            kill_area = self.capture_screen_area(kill_area_config)
            
            # 1. 首先进行颜色检测
            kill_color_result = self.detect_color_regions(kill_area, 'kill')
            death_color_result = self.detect_color_regions(kill_area, 'death')
            
            # 2. 提取文本
            text = self.extract_text(kill_area)
            
            # 验证文本有效性
            if text and not self.is_valid_game_text(text):
                return None
            
            # 3. 结合颜色和文本进行判断 - 必须有字符才认为有击杀
            event_type = None
            confidence = 0
            
            # 首先检查是否有文本内容 - 没有字符则不存在击杀
            if not text or len(text.strip()) == 0:
                print(f"[击杀检测] 击杀区域无字符，不存在击杀事件")
                return None
            
            print(f"[击杀检测] 检测到字符: '{text}'")
            
            # 检测绿色击杀 - 我方击杀对方
            if kill_color_result and kill_color_result['detected']:
                text_lower = text.lower()
                for keyword in self.kill_keywords:
                    if keyword.lower() in text_lower:
                        event_type = 'kill'
                        confidence = 0.9  # 颜色+文本匹配，高置信度
                        print(f"[击杀检测] 检测到击杀关键词: '{keyword}'")
                        break
                
                if not event_type:  # 有颜色但文本不匹配关键词
                    event_type = 'kill'
                    confidence = 0.7  # 仅颜色匹配，中等置信度
                    print(f"[击杀检测] 检测到绿色但无关键词，判定为击杀")
            
            # 检测红色死亡 - 我方被击杀
            elif death_color_result and death_color_result['detected']:
                text_lower = text.lower()
                for keyword in self.death_keywords:
                    if keyword.lower() in text_lower:
                        event_type = 'death'
                        confidence = 0.9  # 颜色+文本匹配，高置信度
                        print(f"[击杀检测] 检测到死亡关键词: '{keyword}'")
                        break
                
                if not event_type:  # 有颜色但文本不匹配关键词
                    event_type = 'death'
                    confidence = 0.7  # 仅颜色匹配，中等置信度
                    print(f"[击杀检测] 检测到红色但无关键词，判定为死亡")
            
            # 4. 如果颜色检测失败，回退到纯文本检测（但必须有字符）
            if not event_type and text and len(text.strip()) > 0:
                text_lower = text.lower()
                for keyword in self.kill_keywords:
                    if keyword.lower() in text_lower:
                        event_type = 'kill'
                        confidence = 0.5  # 仅文本匹配，低置信度
                        print(f"[击杀检测] 纯文本检测到击杀关键词: '{keyword}'")
                        break
                
                if not event_type:
                    for keyword in self.death_keywords:
                        if keyword.lower() in text_lower:
                            event_type = 'death'
                            confidence = 0.5  # 仅文本匹配，低置信度
                            print(f"[击杀检测] 纯文本检测到死亡关键词: '{keyword}'")
                            break
            
            # 5. 如果检测到事件且置信度足够高，返回结果
            if event_type and confidence >= 0.5:
                print(f"[击杀检测] 检测到{event_type}事件，置信度: {confidence}")
                self.last_kill_time = current_time
                return {
                    'type': event_type,
                    'text': text,
                    'confidence': confidence,
                    'color_detected': kill_color_result['detected'] if event_type == 'kill' else death_color_result['detected'],
                    'timestamp': current_time
                }
            else:
                print(f"[击杀检测] 未检测到有效击杀事件，事件类型: {event_type}, 置信度: {confidence}")
            
            return None
            
        except Exception as e:
            print(f"击杀检测失败: {e}")
            return None
    
    def detect_chat_message(self):
        """检测聊天消息 - 专门检测中文对话"""
        current_time = time.time()
        
        # 检查冷却时间
        chat_cooldown = getattr(self.config.cooldowns, 'chat_cooldown', 3.0) if hasattr(self.config, 'cooldowns') else 3.0
        if current_time - self.last_chat_time < chat_cooldown:
            return None
        
        try:
            # 安全获取聊天检测区域
            chat_area_config = getattr(self.config.detection_areas, 'chat_detection_area', {}) if hasattr(self.config, 'detection_areas') else {}
            chat_area = self.capture_screen_area(chat_area_config)
            
            # 提取文本
            text = self.extract_text(chat_area)
            
            if not text:
                return None
            
            # 首先验证是否为有效的游戏文本
            if not self.is_valid_game_text(text):
                return None
            
            # 检测中文内容
            chinese_text = self.extract_chinese_text(text)
            
            # 详细记录识别过程
            print(f"[OCR调试] 原始文本: '{text}'")
            print(f"[OCR调试] 提取中文: '{chinese_text}'")
            print(f"[OCR调试] 中文长度: {len(chinese_text)}")
            
            # 检查是否是有效的聊天消息
            if self.is_valid_chat_message(text, chinese_text):
                print(f"[OCR调试] 有效聊天消息，质量: {self.assess_ocr_quality(text)}")
                self.last_chat_time = current_time
                return {
                    'type': 'chat',
                    'text': text,
                    'chinese_text': chinese_text,
                    'has_chinese': len(chinese_text) > 0,
                    'ocr_quality': self.assess_ocr_quality(text),
                    'timestamp': current_time
                }
            else:
                print(f"[OCR调试] 无效聊天消息，跳过")
            
            return None
            
        except Exception as e:
            print(f"聊天检测失败: {e}")
            return None
    
    def extract_chinese_text(self, text):
        """提取文本中的中文内容"""
        return self.advanced_ocr.extract_chinese_text(text)
    
    def assess_ocr_quality(self, text):
        """评估OCR识别质量"""
        return self.advanced_ocr.assess_ocr_quality(text)
    
    def is_valid_game_text(self, text):
        """检查是否为有效的游戏文本"""
        return self.advanced_ocr.is_valid_game_text(text)
    
    def is_valid_chat_message(self, text, chinese_text):
        """判断是否是有效的聊天消息 - 更宽松的检测"""
        # 1. 优先检查是否包含中文（最可靠的指标）
        if len(chinese_text) >= 2:  # 至少2个中文字符
            print(f"[聊天验证] 检测到中文内容: '{chinese_text}'")
            return True
        
        # 2. 检查是否包含聊天标识符
        chat_indicators = [':', '：', '说', 'said', 'says', 'chat', '聊天', '队友', '队友]', '[队友]']
        for indicator in chat_indicators:
            if indicator in text:
                print(f"[聊天验证] 检测到聊天标识符: '{indicator}'")
                return True
        
        # 3. 检查是否包含常见聊天词汇（中英文）
        chat_keywords = [
            '你好', 'hi', 'hello', '谢谢', 'thanks', '再见', 'bye', 'gg', 'wp',
            '加油', 'nice', 'good', 'bad', 'noob', 'pro', 'team', 'push', 'defend',
            'gank', 'farm', 'ward', 'item', 'skill', 'ult', 'ultimate', 'combo',
            'strategy', 'tactics', 'win', 'lose', 'victory', 'defeat'
        ]
        text_lower = text.lower()
        for keyword in chat_keywords:
            if keyword.lower() in text_lower:
                print(f"[聊天验证] 检测到聊天关键词: '{keyword}'")
                return True
        
        # 4. 检查文本长度和字符组成（更宽松）
        if len(text.strip()) >= 3:  # 至少3个字符
            # 检查是否包含字母、数字或中文字符
            has_valid_chars = any(c.isalnum() or '\u4e00' <= c <= '\u9fff' for c in text)
            if has_valid_chars:
                print(f"[聊天验证] 检测到有效字符组合: '{text[:20]}...'")
                return True
        
        print(f"[聊天验证] 无效聊天消息: '{text}'")
        return False
    
    def test_ocr(self, area_name):
        """测试OCR功能"""
        if area_name == 'kill':
            area = getattr(self.config.detection_areas, 'kill_detection_area', {}) if hasattr(self.config, 'detection_areas') else {}
        else:
            area = getattr(self.config.detection_areas, 'chat_detection_area', {}) if hasattr(self.config, 'detection_areas') else {}
        
        try:
            image = self.capture_screen_area(area)
            text = self.extract_text(image)
            return text
        except Exception as e:
            return f"OCR测试失败: {e}"
    
    def test_color_detection(self, area_name):
        """测试颜色检测功能"""
        if area_name == 'kill':
            area = getattr(self.config.detection_areas, 'kill_detection_area', {}) if hasattr(self.config, 'detection_areas') else {}
        else:
            area = getattr(self.config.detection_areas, 'chat_detection_area', {}) if hasattr(self.config, 'detection_areas') else {}
        
        try:
            image = self.capture_screen_area(area)
            
            # 测试击杀颜色检测
            kill_result = self.detect_color_regions(image, 'kill')
            death_result = self.detect_color_regions(image, 'death')
            
            result = f"颜色检测结果:\n"
            result += f"绿色击杀区域: {'检测到' if kill_result and kill_result['detected'] else '未检测到'}\n"
            if kill_result and kill_result['detected']:
                result += f"  区域大小: {kill_result['area']:.2f}\n"
            
            result += f"红褐色死亡区域: {'检测到' if death_result and death_result['detected'] else '未检测到'}\n"
            if death_result and death_result['detected']:
                result += f"  区域大小: {death_result['area']:.2f}\n"
            
            # 同时测试文本检测
            text = self.extract_text(image)
            result += f"\n文本检测结果:\n{text if text else '未检测到文本'}"
            
            return result
        except Exception as e:
            return f"颜色检测测试失败: {e}"
    
    def test_combined_detection(self, area_name):
        """测试综合检测功能"""
        if area_name == 'kill':
            area = getattr(self.config.detection_areas, 'kill_detection_area', {}) if hasattr(self.config, 'detection_areas') else {}
        else:
            area = getattr(self.config.detection_areas, 'chat_detection_area', {}) if hasattr(self.config, 'detection_areas') else {}
        
        try:
            # 使用综合检测方法
            result = self.detect_kill_event()
            
            if result:
                return f"检测到事件:\n类型: {result['type']}\n置信度: {result['confidence']:.2f}\n文本: {result['text']}\n颜色检测: {result['color_detected']}"
            else:
                return "未检测到击杀或死亡事件"
        except Exception as e:
            return f"综合检测测试失败: {e}"
    
    def test_chinese_chat_detection(self, area_name):
        """测试中文聊天检测功能"""
        if area_name == 'kill':
            area = getattr(self.config.detection_areas, 'kill_detection_area', {}) if hasattr(self.config, 'detection_areas') else {}
        else:
            area = getattr(self.config.detection_areas, 'chat_detection_area', {}) if hasattr(self.config, 'detection_areas') else {}
        
        try:
            # 截取区域
            image = self.capture_screen_area(area)
            
            # 提取文本
            text = self.extract_text(image)
            
            # 提取中文
            chinese_text = self.extract_chinese_text(text)
            
            # 检查是否是有效聊天
            is_valid = self.is_valid_chat_message(text, chinese_text)
            
            result = f"中文聊天检测结果:\n"
            result += f"原始文本: {text if text else '无'}\n"
            result += f"中文内容: {chinese_text if chinese_text else '无'}\n"
            result += f"包含中文: {'是' if len(chinese_text) > 0 else '否'}\n"
            result += f"有效聊天: {'是' if is_valid else '否'}\n"
            
            if is_valid:
                result += f"检测到聊天消息，可以进行对话处理"
            else:
                result += f"未检测到有效聊天消息"
            
            return result
        except Exception as e:
            return f"中文聊天检测测试失败: {e}"
    
    def test_chat_detection(self):
        """测试聊天检测功能"""
        try:
            result = self.detect_chat_message()
            
            if result:
                return f"检测到聊天消息:\n文本: {result['text']}\n中文: {result['chinese_text']}\n包含中文: {'是' if result['has_chinese'] else '否'}"
            else:
                return "未检测到聊天消息"
        except Exception as e:
            return f"聊天检测测试失败: {e}"

# 测试入口
if __name__ == "__main__":
    import tkinter as tk
    from tkinter import ttk, messagebox
    
    # 创建测试窗口
    root = tk.Tk()
    root.title("OCR检测器测试")
    root.geometry("600x500")
    
    # 创建测试配置
    class TestConfig:
        def __init__(self):
            self.ocr = {
                'tesseract_path': r"D:\Tesseract-OCR\tesseract.exe",
                'tessdata_path': r"D:\Tesseract-OCR\tessdata",
                'language': "eng+chi_sim",
                'detection_interval': 0.1
            }
            self.detection_areas = {
                'kill_detection_area': {'x': 100, 'y': 100, 'width': 200, 'height': 50, 'enabled': True},
                'chat_detection_area': {'x': 100, 'y': 200, 'width': 300, 'height': 100, 'enabled': True}
            }
            self.cooldowns = {
                'kill_cooldown': 5.0,
                'chat_cooldown': 3.0
            }
    
    config = TestConfig()
    detector = OCRDetector(config)
    
    # 创建测试界面
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 区域选择
    ttk.Label(frame, text="选择检测区域:").pack(anchor=tk.W)
    area_var = tk.StringVar(value="kill")
    area_combo = ttk.Combobox(frame, textvariable=area_var, values=["kill", "chat"])
    area_combo.pack(fill=tk.X, pady=5)
    
    # 测试按钮
    def test_ocr():
        area_type = area_var.get()
        result = detector.test_ocr(area_type)
        messagebox.showinfo("OCR测试结果", f"检测到的文字:\n{result}")
    
    ttk.Button(frame, text="测试OCR识别", command=test_ocr).pack(pady=10)
    
    def test_kill_detection():
        result = detector.detect_kill_event()
        messagebox.showinfo("击杀检测结果", f"检测结果: {result}")
    
    ttk.Button(frame, text="测试击杀检测", command=test_kill_detection).pack(pady=5)
    
    def test_chat_detection():
        result = detector.test_chat_detection()
        messagebox.showinfo("聊天检测结果", f"检测结果: {result}")
    
    ttk.Button(frame, text="测试聊天检测", command=test_chat_detection).pack(pady=5)
    
    def test_chinese_chat():
        area_type = area_var.get()
        result = detector.test_chinese_chat_detection(area_type)
        messagebox.showinfo("中文聊天检测结果", f"检测结果: {result}")
    
    ttk.Button(frame, text="测试中文聊天检测", command=test_chinese_chat).pack(pady=5)
    
    def test_color_detection():
        area_type = area_var.get()
        result = detector.test_color_detection(area_type)
        messagebox.showinfo("颜色检测结果", f"检测结果: {result}")
    
    ttk.Button(frame, text="测试颜色检测", command=test_color_detection).pack(pady=5)
    
    def test_combined():
        area_type = area_var.get()
        result = detector.test_combined_detection(area_type)
        messagebox.showinfo("综合检测结果", f"检测结果: {result}")
    
    ttk.Button(frame, text="测试综合检测", command=test_combined).pack(pady=5)
    
    # 状态显示
    status_label = ttk.Label(frame, text="选择区域类型后点击按钮测试OCR功能")
    status_label.pack(pady=10)
    
    # 启动主循环
    root.mainloop()
