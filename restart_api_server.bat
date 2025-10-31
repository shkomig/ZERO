@echo off
echo ==========================================
echo   Restarting API Server with Speed Fix
echo ==========================================
echo.
echo Stopping any existing API server...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq api_server.py*" 2>nul
timeout /t 2 /nobreak >nul
echo.
echo Starting API Server with new router...
start "Zero Agent API" python api_server.py
echo.
echo [OK] API Server starting...
echo.
echo Testing in 10 seconds...
timeout /t 10 /nobreak >nul
echo.
echo Running speed test...
python test_speed_improvement.py
pause

