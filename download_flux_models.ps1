# 🎨 FLUX Model Downloader for Zero Agent
# Downloads required FLUX.1-schnell models

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FLUX.1-schnell Model Downloader" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Model URLs (HuggingFace)
$UNET_URL = "https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors"
$CLIP_URL = "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors"
$T5_URL = "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors"
$VAE_URL = "https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors"

# Target directories
$BASE_DIR = "C:\AI-MEDIA-RTX5090\models\flux"
$UNET_DIR = "$BASE_DIR\unet"
$CLIP_DIR = "$BASE_DIR\clip"
$VAE_DIR = "$BASE_DIR\vae"

# Create directories
Write-Host "📁 Creating model directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $UNET_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $CLIP_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $VAE_DIR | Out-Null

# Download function with progress
function Download-Model {
    param(
        [string]$Url,
        [string]$Destination
    )
    
    $fileName = Split-Path $Destination -Leaf
    Write-Host "📥 Downloading $fileName..." -ForegroundColor Yellow
    
    try {
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $Url -OutFile $Destination -UseBasicParsing
        Write-Host "   ✅ Downloaded: $fileName" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "   ❌ Failed: $_" -ForegroundColor Red
        return $false
    }
}

# Download models
Write-Host ""
Write-Host "🚀 Starting downloads..." -ForegroundColor Cyan
Write-Host "This will take a while (models are large ~20GB total)" -ForegroundColor Yellow
Write-Host ""

$success = $true

# UNET (main model) ~10GB
if (-not (Test-Path "$UNET_DIR\flux1-schnell.safetensors")) {
    Write-Host "[1/4] UNET Model (~10GB)" -ForegroundColor Cyan
    $success = $success -and (Download-Model -Url $UNET_URL -Destination "$UNET_DIR\flux1-schnell.safetensors")
} else {
    Write-Host "[1/4] UNET already exists ✓" -ForegroundColor Green
}

# CLIP-L ~250MB
if (-not (Test-Path "$CLIP_DIR\clip_l.safetensors")) {
    Write-Host "[2/4] CLIP-L Model (~250MB)" -ForegroundColor Cyan
    $success = $success -and (Download-Model -Url $CLIP_URL -Destination "$CLIP_DIR\clip_l.safetensors")
} else {
    Write-Host "[2/4] CLIP-L already exists ✓" -ForegroundColor Green
}

# T5 ~9GB
if (-not (Test-Path "$CLIP_DIR\t5xxl_fp16.safetensors")) {
    Write-Host "[3/4] T5 Model (~9GB)" -ForegroundColor Cyan
    $success = $success -and (Download-Model -Url $T5_URL -Destination "$CLIP_DIR\t5xxl_fp16.safetensors")
} else {
    Write-Host "[3/4] T5 already exists ✓" -ForegroundColor Green
}

# VAE ~300MB
if (-not (Test-Path "$VAE_DIR\ae.safetensors")) {
    Write-Host "[4/4] VAE Model (~300MB)" -ForegroundColor Cyan
    $success = $success -and (Download-Model -Url $VAE_URL -Destination "$VAE_DIR\ae.safetensors")
} else {
    Write-Host "[4/4] VAE already exists ✓" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($success) {
    Write-Host "  ✅ All models downloaded!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Restart Docker containers:" -ForegroundColor White
    Write-Host "   cd C:\AI-MEDIA-RTX5090\services" -ForegroundColor Gray
    Write-Host "   .\stop-stack.ps1" -ForegroundColor Gray
    Write-Host "   .\start-stack.ps1" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Test with Zero Agent:" -ForegroundColor White
    Write-Host "   צור תמונה של דג סלמון בנורווגיה" -ForegroundColor Gray
} else {
    Write-Host "  ⚠️  Some downloads failed" -ForegroundColor Red
    Write-Host "  Check your internet connection and try again" -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan

