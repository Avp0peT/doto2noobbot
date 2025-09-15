# Dota聊天机器人

一个基于DeepSeek API的Dota 2聊天机器人，具备击杀检测和智能鼓励功能。

## 快速开始

### 1. 安装
```bash
# 运行安装脚本
install.bat
```

### 2. 启动
```bash
# 使用启动脚本
start.bat

# 或直接运行
python main.py
```

### 3. 配置
1. 在"设置"标签页中输入DeepSeek API密钥
2. 使用可视化区域选择设置检测区域
3. 调整冷却时间和功能开关

### 4. 测试模块
```bash
# 测试所有模块
python test_modules.py

# 或单独测试各个模块
python area_selector.py    # 测试区域选择器
python config.py           # 测试配置系统
python deepseek_api.py     # 测试DeepSeek API
python ocr_detector.py     # 测试OCR检测器
```

## 功能特性

- 🎯 **击杀检测**: 使用OCR技术检测游戏中的击杀和死亡事件
- 🤖 **AI对话**: 集成DeepSeek API，提供智能聊天回复
- 💬 **自动鼓励**: 根据队友击杀或阵亡自动发送鼓励语
- ⚙️ **灵活配置**: 可自由选择检测区域和设置冷却时间
- 📊 **实时日志**: 显示检测和发送的消息记录
- 🔧 **OCR测试**: 内置OCR测试工具，方便调试
- 🛠️ **配置管理**: 完整的配置管理系统，支持导入导出
- 📝 **AI生成鼓励语**: 使用DeepSeek模型智能生成个性化鼓励语
- 🎯 **可视化区域选择**: 支持手动拖拽选择检测区域

## 项目结构

```
datdabot/
├── main.py              # 主程序入口
├── config.py            # 配置管理和配置界面（整合版）
├── ocr_detector.py      # OCR检测模块
├── deepseek_api.py      # DeepSeek API集成
├── area_selector.py     # 区域选择器和区域管理器（整合版）
├── requirements.txt     # 依赖包列表
├── config_example.json  # 示例配置文件
├── install.bat          # 安装脚本
├── install_python313.bat # Python 3.13专用安装脚本
├── start.bat            # 启动脚本
├── DOCUMENTATION.md     # 完整文档
└── README.md           # 说明文档
```

## 文档

📖 **完整文档**: 查看 [DOCUMENTATION.md](DOCUMENTATION.md) 获取详细的安装指南、使用说明、故障排除和开发文档。

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规和游戏服务条款。
