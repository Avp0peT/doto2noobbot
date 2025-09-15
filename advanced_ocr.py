# -*- coding: utf-8 -*-
"""
高级OCR引擎支持
支持多种OCR模型：Tesseract、EasyOCR、PaddleOCR
"""
import cv2
import numpy as np
import re
import time
from typing import List, Dict, Optional, Tuple

class AdvancedOCR:
    """高级OCR引擎，支持多种OCR模型"""
    
    def __init__(self, config):
        self.config = config
        self.engines = {}
        self.current_engine = 'tesseract'  # 默认引擎
        
        # 初始化所有可用的OCR引擎
        self._init_engines()
    
    def _init_engines(self):
        """初始化所有可用的OCR引擎"""
        # 1. Tesseract (默认)
        try:
            import pytesseract
            self.engines['tesseract'] = {
                'name': 'Tesseract',
                'module': pytesseract,
                'available': True,
                'languages': ['eng', 'chi_sim'],
                'description': '谷歌开源OCR，支持多语言'
            }
        except ImportError:
            self.engines['tesseract'] = {'available': False}
        
        # 2. EasyOCR
        try:
            import easyocr
            self.engines['easyocr'] = {
                'name': 'EasyOCR',
                'module': easyocr,
                'available': True,
                'languages': ['en', 'ch_sim'],
                'description': '基于PyTorch，中文识别效果好',
                'reader': None  # 延迟初始化
            }
        except ImportError:
            self.engines['easyocr'] = {'available': False}
        
        # 3. PaddleOCR
        try:
            from paddleocr import PaddleOCR
            self.engines['paddleocr'] = {
                'name': 'PaddleOCR',
                'module': PaddleOCR,
                'available': True,
                'languages': ['ch', 'en'],
                'description': '百度开发，中文识别精度高',
                'reader': None  # 延迟初始化
            }
        except ImportError:
            self.engines['paddleocr'] = {'available': False}
    
    def get_available_engines(self) -> List[str]:
        """获取可用的OCR引擎列表"""
        return [name for name, info in self.engines.items() if info.get('available', False)]
    
    def set_engine(self, engine_name: str) -> bool:
        """设置当前使用的OCR引擎"""
        if engine_name in self.engines and self.engines[engine_name].get('available', False):
            self.current_engine = engine_name
            return True
        return False
    
    def get_engine_info(self, engine_name: str = None) -> Dict:
        """获取OCR引擎信息"""
        if engine_name is None:
            engine_name = self.current_engine
        return self.engines.get(engine_name, {})
    
    def _preprocess_image(self, image):
        """图像预处理以提高OCR准确率"""
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 应用高斯模糊减少噪声
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # 应用阈值处理
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 形态学操作
        kernel = np.ones((2, 2), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return processed
    
    def extract_text_tesseract(self, image) -> str:
        """使用Tesseract提取文本"""
        try:
            processed = self._preprocess_image(image)
            
            # 尝试多种PSM模式
            texts = []
            for psm in [6, 7, 8]:
                try:
                    text = self.engines['tesseract']['module'].image_to_string(
                        processed, 
                        lang='eng+chi_sim',
                        config=f'--psm {psm}'
                    ).strip()
                    if text:
                        texts.append((psm, text))
                except:
                    continue
            
            if texts:
                # 选择最长的文本
                texts.sort(key=lambda x: len(x[1]), reverse=True)
                best_text = texts[0][1]
                return re.sub(r'\s+', ' ', best_text.strip())
            
            return ""
        except Exception as e:
            print(f"Tesseract OCR失败: {e}")
            return ""
    
    def extract_text_easyocr(self, image) -> str:
        """使用EasyOCR提取文本"""
        try:
            # 延迟初始化
            if self.engines['easyocr']['reader'] is None:
                self.engines['easyocr']['reader'] = self.engines['easyocr']['module'].Reader(['ch_sim', 'en'])
            
            # 预处理图像
            processed = self._preprocess_image(image)
            
            # 执行OCR
            results = self.engines['easyocr']['reader'].readtext(processed)
            
            # 提取文本
            texts = []
            for (bbox, text, confidence) in results:
                if confidence > 0.3:  # 置信度阈值
                    texts.append(text)
            
            return ' '.join(texts).strip()
        except Exception as e:
            print(f"EasyOCR失败: {e}")
            return ""
    
    def extract_text_paddleocr(self, image) -> str:
        """使用PaddleOCR提取文本"""
        try:
            # 延迟初始化
            if self.engines['paddleocr']['reader'] is None:
                self.engines['paddleocr']['reader'] = self.engines['paddleocr']['module'](
                    use_angle_cls=True, 
                    lang='ch'
                )
            
            # 执行OCR
            results = self.engines['paddleocr']['reader'].ocr(image, cls=True)
            
            # 提取文本
            texts = []
            if results and results[0]:
                for line in results[0]:
                    if line and len(line) >= 2:
                        text = line[1][0]  # 文本内容
                        confidence = line[1][1]  # 置信度
                        if confidence > 0.3:  # 置信度阈值
                            texts.append(text)
            
            return ' '.join(texts).strip()
        except Exception as e:
            print(f"PaddleOCR失败: {e}")
            return ""
    
    def extract_text(self, image) -> str:
        """使用当前设置的引擎提取文本"""
        if self.current_engine == 'tesseract':
            return self.extract_text_tesseract(image)
        elif self.current_engine == 'easyocr':
            return self.extract_text_easyocr(image)
        elif self.current_engine == 'paddleocr':
            return self.extract_text_paddleocr(image)
        else:
            return ""
    
    def compare_engines(self, image) -> Dict[str, str]:
        """比较所有可用引擎的识别结果"""
        results = {}
        
        for engine_name in self.get_available_engines():
            try:
                if engine_name == 'tesseract':
                    text = self.extract_text_tesseract(image)
                elif engine_name == 'easyocr':
                    text = self.extract_text_easyocr(image)
                elif engine_name == 'paddleocr':
                    text = self.extract_text_paddleocr(image)
                else:
                    text = ""
                
                results[engine_name] = text
            except Exception as e:
                results[engine_name] = f"错误: {e}"
        
        return results
    
    def extract_chinese_text(self, text: str) -> str:
        """从文本中提取中文字符"""
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
        chinese_matches = chinese_pattern.findall(text)
        return ''.join(chinese_matches)
    
    def assess_ocr_quality(self, text: str) -> str:
        """评估OCR识别质量"""
        if not text:
            return "无内容"
        
        # 计算中文字符比例
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(text)
        chinese_ratio = chinese_chars / total_chars if total_chars > 0 else 0
        
        # 计算特殊字符比例
        special_chars = len(re.findall(r'[^\w\s\u4e00-\u9fff]', text))
        special_ratio = special_chars / total_chars if total_chars > 0 else 0
        
        # 评估质量
        if chinese_ratio > 0.3 and special_ratio < 0.2:
            return "优秀"
        elif chinese_ratio > 0.1 and special_ratio < 0.4:
            return "良好"
        elif chinese_ratio > 0.05 or special_ratio < 0.6:
            return "一般"
        else:
            return "较差"
    
    def is_valid_game_text(self, text: str) -> bool:
        """检查是否为有效的游戏文本"""
        if not text or len(text.strip()) < 1:
            return False
        
        # 过滤掉明显的错误信息
        error_patterns = [
            'HTTPConnectionPool', 'Read timed out', 'fail-safe triggered',
            'PyAutoGUI fail-safe', 'DISABLING FAIL-SAFE', 'NOT RECOMMENDED',
            'gayhub', 'AvpOpeT', 'deep seek', 'Readtimed', '呕 吐',
            'HTTPSConnectionPool', 'ReadtimedIRit', 'AvpopeT',
            '聪明', '珀 如 同', '哎 吐', '车 HO', 'BART',
            'HTTP\'S\'Connection\'Pool', 'Connection Pool (host',
            'ReadtimedIRit', 'Readtimed', '呕 吐', '哎 吐'
        ]
        
        text_lower = text.lower()
        for pattern in error_patterns:
            if pattern.lower() in text_lower:
                return False
        
        # 检查是否包含太多特殊字符
        special_char_count = sum(1 for c in text if not c.isalnum() and c not in ' \t\n\r，。！？：；""''（）【】《》')
        if special_char_count > len(text) * 0.7:  # 如果特殊字符超过70%
            return False
        
        return True

if __name__ == "__main__":
    # 测试代码
    import tkinter as tk
    from config import Config
    
    config = Config()
    ocr = AdvancedOCR(config)
    
    print("=== 高级OCR引擎测试 ===")
    print(f"可用引擎: {ocr.get_available_engines()}")
    
    for engine_name in ocr.get_available_engines():
        info = ocr.get_engine_info(engine_name)
        print(f"{engine_name}: {info.get('description', 'N/A')}")

