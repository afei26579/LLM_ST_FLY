#!/bin/bash

echo "正在运行 AI Chat 流式对话功能测试..."
echo

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 检查是否在正确的目录
if [ ! -f "test.py" ]; then
    echo "错误: 找不到 test.py 文件"
    exit 1
fi

# 运行测试脚本
python test.py

echo
echo "测试完成！"
