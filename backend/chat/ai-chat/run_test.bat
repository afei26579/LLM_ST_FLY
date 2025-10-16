@echo off
echo 正在运行 AI Chat 流式对话功能测试...
echo.

cd /d %~dp0

REM 检查是否在正确的目录
if not exist test.py (
    echo 错误: 找不到 test.py 文件
    pause
    exit /b 1
)

REM 运行测试脚本
python test.py

echo.
echo 测试完成！
pause
