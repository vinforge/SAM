@echo off
REM SAM Docker Quick Start Script for Windows
REM This batch file provides Windows-native startup for SAM Docker

echo 🐳 SAM Docker Quick Start (Windows)
echo ====================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    echo    Visit: https://docs.docker.com/desktop/windows/
    echo.
    echo    After installation:
    echo    1. Restart your computer
    echo    2. Start Docker Desktop
    echo    3. Run this script again
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not available.
    echo    Docker Desktop should include Docker Compose.
    echo    Please ensure Docker Desktop is running and try again.
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose found

REM Check if Docker Desktop is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Desktop is not running.
    echo    Please start Docker Desktop and try again.
    echo.
    echo    Steps:
    echo    1. Open Docker Desktop from Start Menu
    echo    2. Wait for it to start completely
    echo    3. Run this script again
    pause
    exit /b 1
)

echo 📥 Pulling SAM Docker images...
docker-compose pull
if %errorlevel% neq 0 (
    echo ❌ Failed to pull Docker images.
    echo    Please check your internet connection and try again.
    pause
    exit /b 1
)

echo 🚀 Starting SAM services...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ Failed to start SAM services.
    echo    Checking logs...
    docker-compose logs
    pause
    exit /b 1
)

echo ⏳ Waiting for services to start...
timeout /t 15 /nobreak >nul

REM Check if services are running
docker-compose ps | findstr "Up" >nul
if %errorlevel% equ 0 (
    echo.
    echo ✅ SAM is now running!
    echo.
    echo 🌟 Access SAM at:
    echo    Main Interface:     http://localhost:8502
    echo    Memory Center:      http://localhost:8501
    echo    Setup Page:         http://localhost:8503
    echo.
    echo 📚 For more information, see DOCKER_DEPLOYMENT_GUIDE.md
    echo 🛠️  For management commands, use: manage_sam.sh
    echo.
    echo 💡 Tip: You can also use PowerShell or WSL for Linux-style commands
    echo.
    
    REM Ask if user wants to open SAM in browser
    set /p openBrowser="Would you like to open SAM in your browser now? (y/n): "
    if /i "%openBrowser%"=="y" (
        start http://localhost:8502
    )
    
) else (
    echo ❌ Failed to start SAM services
    echo 📋 Checking logs...
    docker-compose logs
    echo.
    echo 🔧 Troubleshooting tips:
    echo    1. Ensure ports 8502, 8501, 8503, 6379, 8000 are not in use
    echo    2. Check if you have enough free disk space (10GB+)
    echo    3. Restart Docker Desktop and try again
    echo    4. Check the logs above for specific error messages
)

echo.
echo Press any key to exit...
pause >nul
