# LLM ST FLY 开发环境启动脚本 (PowerShell版本)
# 设置控制台编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    LLM ST FLY 开发环境启动脚本" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否存在必要的目录
if (-not (Test-Path "backend")) {
    Write-Host "[错误] 未找到 backend 目录" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

if (-not (Test-Path "frontend")) {
    Write-Host "[错误] 未找到 frontend 目录" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

if (-not (Test-Path "venv")) {
    Write-Host "[错误] 未找到虚拟环境 venv 目录" -ForegroundColor Red
    Write-Host "请先创建虚拟环境: python -m venv venv" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit 1
}

# 检查虚拟环境是否存在激活脚本
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "[错误] 虚拟环境PowerShell激活脚本不存在" -ForegroundColor Red
    Write-Host "请检查虚拟环境是否正确安装" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit 1
}

# 检查前端依赖
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "[警告] 前端依赖未安装，正在安装..." -ForegroundColor Yellow
    Set-Location "frontend"
    Write-Host "[信息] 使用 pnpm 安装前端依赖..." -ForegroundColor Green
    
    $pnpmProcess = Start-Process -FilePath "pnpm" -ArgumentList "install" -Wait -PassThru -NoNewWindow
    if ($pnpmProcess.ExitCode -ne 0) {
        Write-Host "[错误] 前端依赖安装失败" -ForegroundColor Red
        Set-Location ".."
        Read-Host "按回车键退出"
        exit 1
    }
    
    Set-Location ".."
    Write-Host "[成功] 前端依赖安装完成" -ForegroundColor Green
    Write-Host ""
}

# 启动后端服务
Write-Host "[信息] 正在启动后端服务..." -ForegroundColor Green
$backendScript = @"
Set-Location '$PWD\backend'
& '..\venv\Scripts\Activate.ps1'
Write-Host '[信息] 虚拟环境已激活' -ForegroundColor Green
Write-Host '[信息] 启动Django开发服务器...' -ForegroundColor Green
python manage.py runserver
"@

Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $backendScript -WindowStyle Normal

# 等待2秒让后端先启动
Start-Sleep -Seconds 2

# 启动前端服务
Write-Host "[信息] 正在启动前端服务..." -ForegroundColor Green
$frontendScript = @"
Set-Location '$PWD\frontend'
Write-Host '[信息] 启动Vue开发服务器...' -ForegroundColor Green
pnpm dev
"@

Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $frontendScript -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[成功] 服务启动完成！" -ForegroundColor Green
Write-Host ""
Write-Host "后端服务: http://localhost:8000" -ForegroundColor White
Write-Host "前端服务: http://localhost:5173" -ForegroundColor White
Write-Host "API文档:  http://localhost:8000/docs/" -ForegroundColor White
Write-Host ""
Write-Host "按任意键关闭此窗口..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

Read-Host
