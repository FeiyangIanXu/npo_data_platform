@echo off
chcp 65001 >nul
title WRDS-Style NPO Data Platform Launcher

:: =================================================================
::  1. 设定项目根目录 (无论从哪里运行此脚本)
:: =================================================================
set "PROJECT_ROOT=%~dp0"
echo [INFO] Project root is: %PROJECT_ROOT%
echo.

:: =================================================================
::  2. 检查端口是否被占用 (核心改进)
:: =================================================================
echo [STEP 1/4] Checking for running services on ports 8000 and 5173...
set "BACKEND_PORT_IN_USE="
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000"') do set "BACKEND_PORT_IN_USE=%%a"

set "FRONTEND_PORT_IN_USE="
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173"') do set "FRONTEND_PORT_IN_USE=%%a"

if defined BACKEND_PORT_IN_USE (
    echo [ERROR] Backend port 8000 is already in use by PID: %BACKEND_PORT_IN_USE%.
    echo Please close the existing backend process before starting.
    pause
    exit /b
)

if defined FRONTEND_PORT_IN_USE (
    echo [ERROR] Frontend port 5173 is already in use by PID: %FRONTEND_PORT_IN_USE%.
    echo Please close the existing frontend process before starting.
    pause
    exit /b
)
echo [OK] Ports are free.
echo.

:: =================================================================
::  3. 初始化数据库
:: =================================================================
echo [STEP 2/4] Initializing database...
cd /d "%PROJECT_ROOT%backend"
REM 使用虚拟环境中的Python来运行，确保环境一致
call .\.venv\Scripts\python.exe db_init.py
cd /d "%PROJECT_ROOT%"
echo [OK] Database check/initialization complete.
echo.

:: =================================================================
::  4. 启动后端服务 (核心改进)
:: =================================================================
echo [STEP 3/4] Starting backend server...
cd /d "%PROJECT_ROOT%backend"
REM 直接指定虚拟环境中的 python.exe，不再依赖系统路径
start "Backend Server (NPO Platform)" cmd /k ".\.venv\Scripts\python.exe main.py"
cd /d "%PROJECT_ROOT%"
echo [OK] Backend server is starting in a new window...
echo Waiting a few seconds for the backend to initialize...
timeout /t 5 >nul
echo.

:: =================================================================
::  5. 启动前端服务
:: =================================================================
echo [STEP 4/4] Starting frontend server...
cd /d "%PROJECT_ROOT%frontend\vite-project"
start "Frontend Server (NPO Platform)" cmd /k "npm run dev"
cd /d "%PROJECT_ROOT%"
echo [OK] Frontend server is starting in a new window...
echo.

:: =================================================================
::  6. 显示最终信息
:: =================================================================
echo ================================================================
echo                    🚀 Startup Complete! 🚀
echo ================================================================
echo.
echo  - Frontend App: http://localhost:5173
echo  - Backend API Docs: http://localhost:8000/docs
echo.
echo Please wait a moment for the servers to finish loading.
echo You can now open your browser to the Frontend URL.
echo.
pause