# -*- coding: utf-8 -*-
"""
安装高级OCR引擎
"""
import subprocess
import sys
import os

def install_package(package):
    """安装Python包"""
    try:
        print(f"正在安装 {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {package} 安装失败: {e}")
        return False

def main():
    """主安装函数"""
    print("=== 安装高级OCR引擎 ===")
    print("这将安装EasyOCR和PaddleOCR以提供更好的文字识别效果")
    print()
    
    # 要安装的包
    packages = [
        "easyocr>=1.7.0",
        "paddlepaddle>=2.5.0", 
        "paddleocr>=2.7.0"
    ]
    
    success_count = 0
    total_count = len(packages)
    
    for package in packages:
        if install_package(package):
            success_count += 1
        print()
    
    print("=== 安装结果 ===")
    print(f"成功安装: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("✓ 所有OCR引擎安装成功！")
        print("\n可用的OCR引擎:")
        print("- Tesseract: 谷歌开源OCR（已安装）")
        print("- EasyOCR: 中文识别效果好")
        print("- PaddleOCR: 百度开发，精度高")
        print("\n请在配置管理器中选择您喜欢的OCR引擎")
    else:
        print("⚠ 部分OCR引擎安装失败，但Tesseract仍然可用")
        print("您可以稍后手动安装失败的包")
    
    print("\n按任意键退出...")
    input()

if __name__ == "__main__":
    main()

