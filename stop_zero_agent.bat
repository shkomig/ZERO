@echo off
title Zero Agent - Stopping System
echo ======================================================================
echo                    Zero Agent - Stopping System
echo ======================================================================
echo.
echo Stopping Zero Agent processes...

echo Stopping Python processes...
taskkill /F /IM python.exe 2>nul

echo Stopping any remaining Zero Agent processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080') do (
    taskkill /F /PID %%a 2>nul
)

echo.
echo Zero Agent system stopped.
echo.
pause



