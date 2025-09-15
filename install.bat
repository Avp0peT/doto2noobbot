@echo off
echo 安装Dota聊天机器人依赖包...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo 检测Python版本...
python -c "import sys; print(f'Python版本: {sys.version}')"

echo.
echo 正在升级pip和构建工具...
python -m pip install --upgrade pip setuptools wheel

echo.
echo 正在安装依赖包（Python 3.13兼容版本）...
echo.

REM 安装预编译包，避免编译问题
echo 安装numpy...
pip install numpy --only-binary=all --upgrade

echo 安装Pillow...
pip install Pillow --only-binary=all --upgrade

echo 安装requests...
pip install requests --upgrade

echo 安装opencv-python...
pip install opencv-python --only-binary=all --upgrade

echo 安装pytesseract...
pip install pytesseract --upgrade

echo 安装pyautogui...
pip install pyautogui --upgrade

echo.
echo 验证安装...
python -c "import numpy, cv2, PIL, pytesseract, pyautogui, requests; print('所有依赖安装成功！')"

if errorlevel 1 (
    echo.
    echo 警告: 某些依赖可能安装失败，尝试替代方案...
    echo.
    echo 尝试安装opencv-python-headless...
    pip install opencv-python-headless --upgrade
    
    echo 尝试安装Pillow的替代版本...
    pip install Pillow==10.4.0 --only-binary=all
)

echo.
echo 依赖包安装完成！
echo.
echo 请确保已安装Tesseract OCR到 D:\Tesseract-OCR\
echo 并下载中文语言包到 D:\Tesseract-OCR\tessdata\
echo.
pause
