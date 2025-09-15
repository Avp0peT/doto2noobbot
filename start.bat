@echo off
echo 启动Dota聊天机器人...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    echo 请从 https://www.python.org/downloads/ 下载并安装Python
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo 检查依赖包...
pip show opencv-python >nul 2>&1
if errorlevel 1 (
    echo 依赖包未安装，请先运行 install.bat 安装依赖包
    echo 或者手动运行: pip install -r requirements.txt
    pause
    exit /b 1
)

REM 检查Tesseract OCR
if not exist "D:\Tesseract-OCR\tesseract.exe" (
    echo 警告: 未找到Tesseract OCR
    echo 请从 https://github.com/UB-Mannheim/tesseract/wiki 下载并安装
    echo 安装路径应为: D:\Tesseract-OCR\
    echo.
)

REM 启动程序
echo 启动程序...
python main.py

pause
