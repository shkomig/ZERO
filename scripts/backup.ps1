# ============================================================================
# Zero Agent - Backup Script
# ============================================================================
#
# This script creates a backup of the Zero Agent project
#
# Usage:
#   .\scripts\backup.ps1

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupName = "zero-agent-backup-$timestamp"
$backupDir = "backups"

Write-Host "💾 Zero Agent - Backup Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Create backup directory
if (!(Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    Write-Host "✅ Created backup directory: $backupDir" -ForegroundColor Green
}

Write-Host "📦 Creating backup: $backupName" -ForegroundColor Yellow
Write-Host ""

# Files and directories to backup
$itemsToBackup = @(
    "*.py",
    "*.html",
    "*.md",
    "*.txt",
    "*.yaml",
    "*.yml",
    ".env.example",
    ".gitignore",
    ".github",
    "memory",
    "zero_agent",
    "docs",
    "scripts",
    "tests",
    "workspace/memory",
    "data/vectors"
)

# Create temporary directory
$tempDir = "$backupDir\temp_$timestamp"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

# Copy files
Write-Host "📋 Copying files..." -ForegroundColor Yellow
foreach ($item in $itemsToBackup) {
    if (Test-Path $item) {
        $destination = Join-Path $tempDir (Split-Path $item -Leaf)
        Copy-Item -Path $item -Destination $tempDir -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ $item" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "🗜️  Compressing backup..." -ForegroundColor Yellow

# Create ZIP archive
$zipPath = "$backupDir\$backupName.zip"
Compress-Archive -Path "$tempDir\*" -DestinationPath $zipPath -Force

# Clean up temp directory
Remove-Item -Path $tempDir -Recurse -Force

# Get file size
$fileSize = (Get-Item $zipPath).Length / 1MB
$fileSizeStr = "{0:N2} MB" -f $fileSize

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ Backup completed successfully!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 Backup location: $zipPath" -ForegroundColor White
Write-Host "📊 Backup size: $fileSizeStr" -ForegroundColor White
Write-Host ""
Write-Host "To restore from backup:" -ForegroundColor Yellow
Write-Host "1. Extract the ZIP file" -ForegroundColor Gray
Write-Host "2. Copy files to the project directory" -ForegroundColor Gray
Write-Host "3. Run setup script: .\scripts\setup.ps1" -ForegroundColor Gray
Write-Host ""

