@echo off
title Zero Agent - Starting...
echo ======================================================================
echo                    Zero Agent - Starting System
echo ======================================================================
echo.
echo Starting Zero Agent API Server...
echo.

cd /d "C:\AI-ALL-PRO\ZERO"

echo Checking if Ollama is running...
netstat -an | findstr :11434 >nul
if %errorlevel% neq 0 (
    echo Ollama is not running! Please start Ollama first.
    echo.
    pause
    exit /b 1
)

echo Ollama is running ✓
echo.

echo Starting Zero Agent API Server...
python api_server.py

echo.
echo Zero Agent has stopped.
pause



