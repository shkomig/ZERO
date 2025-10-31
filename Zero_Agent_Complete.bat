@echo off
title Zero Agent - Complete System
echo ======================================================================
echo                    Zero Agent - Complete System
echo ======================================================================
echo.
echo This will start Zero Agent and open the web interface
echo.

cd /d "C:\AI-ALL-PRO\ZERO"

echo Step 1: Checking Ollama...
netstat -an | findstr :11434 >nul
if %errorlevel% neq 0 (
    echo ERROR: Ollama is not running!
    echo Please start Ollama first, then run this script again.
    echo.
    pause
    exit /b 1
)
echo Ollama is running ✓

echo.
echo Step 2: Starting Zero Agent API Server...
echo (This will open in a new window)
echo.

start "Zero Agent Server" cmd /k "cd /d C:\AI-ALL-PRO\ZERO && python api_server.py"

echo Waiting for server to start...
timeout /t 10 /nobreak >nul

echo.
echo Step 3: Opening Web Interface...
start http://localhost:8080/simple

echo.
echo ======================================================================
echo                    Zero Agent is Ready!
echo ======================================================================
echo.
echo The server is running in a separate window.
echo The web interface should open in your browser.
echo.
echo To stop the server, close the "Zero Agent Server" window.
echo.
pause



