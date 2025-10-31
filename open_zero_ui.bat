@echo off
title Zero Agent - Opening UI
echo ======================================================================
echo                    Zero Agent - Opening Interface
echo ======================================================================
echo.
echo Opening Zero Agent Web Interface...
echo.

timeout /t 2 /nobreak >nul
start http://localhost:8080/simple

echo Interface opened in your default browser!
echo.
echo If the interface doesn't open, please check:
echo 1. Zero Agent server is running (run start_zero_agent.bat first)
echo 2. Your browser is set as default
echo.
pause



