@echo off
title FarmTwin360 Mobile Development
color 0A

echo ============================================================
echo    FarmTwin360 Mobile App Development Environment
echo ============================================================
echo.
echo This will start:
echo   1. Mobile Backend API Server (Port 8000)
echo   2. Expo Metro Bundler
echo.
echo Make sure to keep both windows open while developing!
echo ============================================================
echo.

:: Start Backend API in a new window
echo [1/2] Starting Mobile Backend API Server...
start "FarmTwin360 Backend API" cmd /k "cd /d "%~dp0mobile-backend" && python start_server.py"
timeout /t 3 /nobreak >nul

:: Start Expo Metro Bundler
echo [2/2] Starting Expo Metro Bundler...
cd /d "%~dp0mobile-app"
echo.
echo ============================================================
echo  Backend API: Running in separate window
echo  Metro Bundler: Starting now...
echo ============================================================
echo.
call npx expo start

pause
