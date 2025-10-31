@echo off
echo ========================================
echo   Zero Agent - Service Status Check
echo ========================================
echo.

echo [1/3] Checking Ollama (Port 11434)...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Ollama is RUNNING
) else (
    echo [ERROR] Ollama is NOT RUNNING
    echo Solution: Run 'ollama serve' in a terminal
)
echo.

echo [2/3] Checking API Server (Port 8080)...
curl -s http://localhost:8080/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] API Server is RUNNING
) else (
    echo [ERROR] API Server is NOT RUNNING
    echo Solution: Run 'python api_server.py' in a terminal
)
echo.

echo [3/3] Testing WebSearch...
curl -s -X POST http://localhost:8080/api/chat -H "Content-Type: application/json" -d "{\"message\":\"test search\"}" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] WebSearch endpoint is ACCESSIBLE
) else (
    echo [ERROR] Cannot reach WebSearch endpoint
)
echo.

echo ========================================
echo   WebSearch UI Test
echo ========================================
echo Opening test interface...
start test_websearch_ui.html
echo.
echo Use the web interface to test internet connectivity!
echo.
pause

