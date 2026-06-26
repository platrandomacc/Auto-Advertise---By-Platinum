@echo off
REM AutoAds - Quick Start Script for Windows

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║          AutoAds - Advertisement Website               ║
echo ║                  Starting Server...                    ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if errorlevel 1 (
    echo ❌ Node.js is not installed!
    echo.
    echo Please download and install Node.js from:
    echo https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo ✅ Node.js detected
echo.

REM Check if node_modules exists
if not exist "node_modules\" (
    echo 📦 Installing dependencies...
    echo This may take a minute...
    echo.
    call npm install
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo ✅ Dependencies installed
echo.

REM Start the server
echo 🚀 Starting AutoAds Server...
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 🌐 Server is running on: http://localhost:3000
echo.
echo 📝 First time? 
echo    1. Click "Sign up here" to create account
echo    2. Go to "Post Ad" to create your first ad
echo    3. Browse ads from other users
echo.
echo 🛑 Press Ctrl+C to stop the server
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

call npm start
