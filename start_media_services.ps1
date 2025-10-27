# 🚀 Zero Agent - Media Services Starter
# Starts all AI Media Generation services

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Zero Agent - Media Services" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if services directory exists
$servicesPath = "C:\AI-MEDIA-RTX5090\services"
if (-not (Test-Path $servicesPath)) {
    Write-Host "❌ ERROR: Services directory not found at:" -ForegroundColor Red
    Write-Host "   $servicesPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure AI-MEDIA-RTX5090 is installed correctly." -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "📁 Found services directory" -ForegroundColor Green
Write-Host "🚀 Starting AI Media Stack..." -ForegroundColor Yellow
Write-Host ""

# Navigate to services directory
Push-Location $servicesPath

# Check if start script exists
if (-not (Test-Path ".\start-stack.ps1")) {
    Write-Host "❌ ERROR: start-stack.ps1 not found" -ForegroundColor Red
    Pop-Location
    pause
    exit 1
}

# Start the stack
Write-Host "⚡ Executing start-stack.ps1..." -ForegroundColor Cyan
try {
    & .\start-stack.ps1
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Services Starting..." -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Please wait 30-60 seconds for services to initialize" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Services:" -ForegroundColor Cyan
    Write-Host "  🎨 FLUX (Images):     http://localhost:9188" -ForegroundColor White
    Write-Host "  🎥 CogVideoX (Video): http://localhost:9056/health" -ForegroundColor White
    Write-Host "  🎬 HunyuanVideo:      http://localhost:9055/health" -ForegroundColor White
    Write-Host "  🗣️  Hebrew TTS:        http://localhost:9033/health" -ForegroundColor White
    Write-Host ""
    Write-Host "✅ Done! Services are starting in the background" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now use Zero Agent to:" -ForegroundColor Yellow
    Write-Host "  • צור תמונה של..." -ForegroundColor White
    Write-Host "  • צור סרטון של..." -ForegroundColor White
    Write-Host "  • הקרא בקול..." -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "❌ ERROR: Failed to start services" -ForegroundColor Red
    Write-Host "   $_" -ForegroundColor Red
    Pop-Location
    pause
    exit 1
}

Pop-Location

Write-Host "Press any key to exit..." -ForegroundColor Gray
pause

