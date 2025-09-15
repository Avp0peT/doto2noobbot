@echo off
echo Python 3.13 专用安装脚本
echo ================================
echo.

REM 检查Python版本
python --version
echo.

echo 正在升级pip和构建工具...
python -m pip install --upgrade pip setuptools wheel

echo.
echo 安装Microsoft Visual C++ Build Tools（如果未安装）...
echo 如果出现错误，请手动安装: https://visualstudio.microsoft.com/visual-cpp-build-tools/
echo.

echo 正在安装依赖包...
echo.

REM 方法1: 尝试安装预编译包
echo [方法1] 尝试安装预编译包...
pip install numpy --only-binary=all --upgrade
pip install Pillow --only-binary=all --upgrade
pip install opencv-python --only-binary=all --upgrade
pip install requests --upgrade
pip install pytesseract --upgrade
pip install pyautogui --upgrade

echo.
echo 验证安装...
python -c "import numpy, cv2, PIL, pytesseract, pyautogui, requests; print('✓ 所有依赖安装成功！')"

if errorlevel 1 (
    echo.
    echo [方法2] 预编译包安装失败，尝试替代方案...
    echo.
    
    REM 方法2: 使用conda（如果可用）
    conda --version >nul 2>&1
    if not errorlevel 1 (
        echo 检测到conda，使用conda安装...
        conda install numpy pillow opencv requests -y
        pip install pytesseract pyautogui
    ) else (
        echo 未检测到conda，尝试其他方法...
        
        REM 方法3: 使用特定版本
        echo 尝试安装特定版本...
        pip install numpy==1.26.4 --only-binary=all
        pip install Pillow==10.4.0 --only-binary=all
        pip install opencv-python-headless==4.8.1.78 --only-binary=all
        pip install requests==2.31.0
        pip install pytesseract==0.3.10
        pip install pyautogui==0.9.54
    )
)

echo.
echo 最终验证...
python -c "import numpy, cv2, PIL, pytesseract, pyautogui, requests; print('✓ 所有依赖安装成功！')"

if errorlevel 1 (
    echo.
    echo ❌ 安装失败！请尝试以下解决方案：
    echo.
    echo 1. 安装Microsoft Visual C++ Build Tools
    echo    https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo.
    echo 2. 使用conda安装Python环境
    echo    conda create -n datdabot python=3.11
    echo    conda activate datdabot
    echo    conda install numpy pillow opencv requests
    echo    pip install pytesseract pyautogui
    echo.
    echo 3. 使用Python 3.11或3.12版本
    echo    从 https://www.python.org/downloads/ 下载
    echo.
) else (
    echo.
    echo ✅ 安装成功！现在可以运行 start.bat 启动程序
)

echo.
pause
