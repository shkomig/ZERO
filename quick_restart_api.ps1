# Quick restart API Server
Write-Host "Stopping API Server..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowTitle -like "*api_server*"} | Stop-Process -Force
Start-Sleep -Seconds 2

Write-Host "Starting API Server..." -ForegroundColor Green
Start-Process python -ArgumentList "api_server.py" -WindowStyle Normal

Write-Host "Waiting for server to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host "Testing..." -ForegroundColor Green
python test_speed_improvement.py

