#!/bin/bash

# LLM ST FLY 开发环境启动脚本 (Linux/Mac版本)
# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${YELLOW}    LLM ST FLY 开发环境启动脚本${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# 检查是否存在必要的目录
if [ ! -d "backend" ]; then
    echo -e "${RED}[错误] 未找到 backend 目录${NC}"
    read -p "按回车键退出..."
    exit 1
fi

if [ ! -d "frontend" ]; then
    echo -e "${RED}[错误] 未找到 frontend 目录${NC}"
    read -p "按回车键退出..."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo -e "${RED}[错误] 未找到虚拟环境 venv 目录${NC}"
    echo -e "${YELLOW}请先创建虚拟环境: python -m venv venv${NC}"
    read -p "按回车键退出..."
    exit 1
fi

# 检查虚拟环境是否存在激活脚本
if [ ! -f "venv/bin/activate" ]; then
    echo -e "${RED}[错误] 虚拟环境激活脚本不存在${NC}"
    echo -e "${YELLOW}请检查虚拟环境是否正确安装${NC}"
    read -p "按回车键退出..."
    exit 1
fi

# 检查前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}[警告] 前端依赖未安装，正在安装...${NC}"
    cd frontend
    echo -e "${GREEN}[信息] 使用 pnpm 安装前端依赖...${NC}"
    
    if ! pnpm install; then
        echo -e "${RED}[错误] 前端依赖安装失败${NC}"
        cd ..
        read -p "按回车键退出..."
        exit 1
    fi
    
    cd ..
    echo -e "${GREEN}[成功] 前端依赖安装完成${NC}"
    echo ""
fi

# 检查是否安装了tmux（用于在同一终端中运行多个进程）
if command -v tmux >/dev/null 2>&1; then
    USE_TMUX=true
    echo -e "${GREEN}[信息] 检测到tmux，将使用tmux管理服务${NC}"
else
    USE_TMUX=false
    echo -e "${YELLOW}[信息] 未检测到tmux，将使用后台进程启动服务${NC}"
fi

echo ""

if [ "$USE_TMUX" = true ]; then
    # 使用tmux启动服务
    echo -e "${GREEN}[信息] 使用tmux启动服务...${NC}"
    
    # 创建新的tmux会话
    tmux new-session -d -s llm_st_fly
    
    # 启动后端服务
    tmux send-keys -t llm_st_fly "cd backend && source ../venv/bin/activate && echo '[信息] 虚拟环境已激活' && echo '[信息] 启动Django开发服务器...' && python manage.py runserver" Enter
    
    # 创建新的窗格启动前端服务
    tmux split-window -t llm_st_fly -h
    tmux send-keys -t llm_st_fly "cd frontend && echo '[信息] 启动Vue开发服务器...' && pnpm dev" Enter
    
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${GREEN}[成功] 服务启动完成！${NC}"
    echo ""
    echo -e "${WHITE}后端服务: http://localhost:8000${NC}"
    echo -e "${WHITE}前端服务: http://localhost:5173${NC}"
    echo -e "${WHITE}API文档:  http://localhost:8000/docs/${NC}"
    echo ""
    echo -e "${YELLOW}使用以下命令查看服务:${NC}"
    echo -e "${WHITE}  tmux attach -t llm_st_fly${NC}"
    echo -e "${YELLOW}使用以下命令停止服务:${NC}"
    echo -e "${WHITE}  tmux kill-session -t llm_st_fly${NC}"
    echo -e "${CYAN}========================================${NC}"
    
    # 附加到tmux会话
    tmux attach -t llm_st_fly
    
else
    # 使用后台进程启动服务
    echo -e "${GREEN}[信息] 启动后端服务...${NC}"
    
    # 启动后端服务
    cd backend
    source ../venv/bin/activate
    echo -e "${GREEN}[信息] 虚拟环境已激活${NC}"
    echo -e "${GREEN}[信息] 启动Django开发服务器...${NC}"
    python manage.py runserver > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    # 等待2秒让后端先启动
    sleep 2
    
    # 启动前端服务
    echo -e "${GREEN}[信息] 启动前端服务...${NC}"
    cd frontend
    echo -e "${GREEN}[信息] 启动Vue开发服务器...${NC}"
    pnpm dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${GREEN}[成功] 服务启动完成！${NC}"
    echo ""
    echo -e "${WHITE}后端服务: http://localhost:8000${NC}"
    echo -e "${WHITE}前端服务: http://localhost:5173${NC}"
    echo -e "${WHITE}API文档:  http://localhost:8000/docs/${NC}"
    echo ""
    echo -e "${WHITE}后端PID: $BACKEND_PID${NC}"
    echo -e "${WHITE}前端PID: $FRONTEND_PID${NC}"
    echo ""
    echo -e "${WHITE}日志文件:${NC}"
    echo -e "${WHITE}  后端日志: backend.log${NC}"
    echo -e "${WHITE}  前端日志: frontend.log${NC}"
    echo ""
    echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"
    echo -e "${CYAN}========================================${NC}"
    
    # 等待用户中断
    trap "echo -e '\n${YELLOW}[信息] 正在停止服务...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo -e '${GREEN}[成功] 服务已停止${NC}'; exit 0" INT
    
    # 等待进程结束
    wait
fi
