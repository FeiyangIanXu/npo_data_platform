@echo off
chcp 65001 >nul
echo ========================================
echo WRDS Query System Startup
echo ========================================

echo.
echo 1. Initializing database...
cd backend
python db_init.py
cd ..

echo.
echo 2. Starting backend server...
cd backend
start "Backend Server" cmd /k "python main.py"
cd ..

echo.
echo 3. Starting frontend server...
cd frontend\vite-project
start "Frontend Server" cmd /k "npm run dev"
cd ..\..

echo.
echo ========================================
echo Startup Complete!
echo ========================================
echo.
echo Frontend URL: http://localhost:5173
echo Backend API:  http://localhost:8000/docs
echo.
echo Please wait a few seconds for services to fully start...
echo Then open your browser and navigate to the frontend URL
echo.
pause 