@echo off
echo ========================================
echo WRDS查询系统启动
echo ========================================

echo.
echo 1. 初始化数据库...
cd backend
python db_init.py
cd ..

echo.
echo 2. 启动后端服务...
cd backend
start "Backend Server" cmd /k "python main.py"
cd ..

echo.
echo 3. 启动前端服务...
cd frontend\vite-project
start "Frontend Server" cmd /k "npm run dev"
cd ..\..

echo.
echo ========================================
echo 启动完成！
echo ========================================
echo.
echo 前端地址: http://localhost:5173
echo 后端API:  http://localhost:8002/docs
echo.
echo 请等待几秒钟让服务完全启动...
echo 然后打开浏览器访问前端地址
echo.
pause 