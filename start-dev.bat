@echo off
chcp 65001 >nul
echo ========================================
echo    LLM ST FLY 开发环境启动脚本
echo ========================================
echo.

:: 检查是否存在必要的目录
if not exist "backend" (
    echo [错误] 未找到 backend 目录
    pause
    exit /b 1
)

if not exist "frontend" (
    echo [错误] 未找到 frontend 目录
    pause
    exit /b 1
)

if not exist "venv" (
    echo [错误] 未找到虚拟环境 venv 目录
    echo 请先创建虚拟环境: python -m venv venv
    pause
    exit /b 1
)

:: 检查虚拟环境是否存在激活脚本
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境激活脚本不存在
    echo 请检查虚拟环境是否正确安装
    pause
    exit /b 1
)

:: 检查frontend是否安装了依赖
if not exist "frontend\node_modules" (
    echo [警告] 前端依赖未安装，正在安装...
    cd frontend
    echo [信息] 使用 pnpm 安装前端依赖...
    pnpm install
    if errorlevel 1 (
        echo [错误] 前端依赖安装失败
        cd ..
        pause
        exit /b 1
    )
    cd ..
    echo [成功] 前端依赖安装完成
    echo.
)

:: 启动后端服务
echo [信息] 正在启动后端服务...
start "后端服务 - Django" cmd /k "cd /d %~dp0backend && call ..\venv\Scripts\activate.bat && echo [信息] 虚拟环境已激活 && echo [信息] 启动Django开发服务器... && python manage.py runserver"

:: 等待2秒让后端先启动
timeout /t 2 /nobreak >nul

:: 启动前端服务
echo [信息] 正在启动前端服务...
start "前端服务 - Vue" cmd /k "cd /d %~dp0frontend && echo [信息] 启动Vue开发服务器... && pnpm dev"

echo.
echo ========================================
echo [成功] 服务启动完成！
echo.
echo 后端服务: http://localhost:8000
echo 前端服务: http://localhost:5173
echo API文档:  http://localhost:8000/docs/
echo.
echo 按任意键关闭此窗口...
echo ========================================
pause >nul
