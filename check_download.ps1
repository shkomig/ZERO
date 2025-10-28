# Check DictaLM Download Status
# Run this to see download progress

$modelPath = "C:\AI-ALL-PRO\ZERO\models\dictalm2.0"
$targetSize = 14  # GB

Write-Host "="*60 -ForegroundColor Cyan
Write-Host "DictaLM 2.0 Download Monitor" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan
Write-Host ""

if (Test-Path $modelPath) {
    $files = Get-ChildItem $modelPath -Recurse -File
    $totalSize = ($files | Measure-Object -Property Length -Sum).Sum / 1GB
    $fileCount = $files.Count
    $progress = [math]::Round(($totalSize / $targetSize) * 100, 1)
    
    Write-Host "Status: " -NoNewline
    Write-Host "DOWNLOADING" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Downloaded: " -NoNewline
    Write-Host "$([math]::Round($totalSize, 2)) GB" -ForegroundColor Green -NoNewline
    Write-Host " / $targetSize GB"
    Write-Host "Files: " -NoNewline
    Write-Host "$fileCount" -ForegroundColor Green
    Write-Host "Progress: " -NoNewline
    Write-Host "$progress%" -ForegroundColor $(if($progress -ge 100){"Green"}elseif($progress -ge 50){"Yellow"}else{"Red"})
    Write-Host ""
    
    if ($progress -ge 95) {
        Write-Host "="*60 -ForegroundColor Green
        Write-Host "DOWNLOAD COMPLETE!" -ForegroundColor Green
        Write-Host "="*60 -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "1. Test: python hebrew_llm.py"
        Write-Host "2. Run: python api_server.py"
        Write-Host "3. Chat: http://localhost:8080/simple"
    } else {
        Write-Host "Estimated time remaining: " -NoNewline
        $remaining = $targetSize - $totalSize
        $minutes = [math]::Round($remaining * 2, 0)  # ~2 min per GB
        Write-Host "$minutes minutes (approximate)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Run this script again in 5 minutes to check progress"
    }
    
    Write-Host ""
    Write-Host "Recent files:"
    $files | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | Format-Table Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB, 1)}}, LastWriteTime -AutoSize
    
} else {
    Write-Host "ERROR: " -NoNewline -ForegroundColor Red
    Write-Host "Model directory not found!"
    Write-Host ""
    Write-Host "The download may have failed or not started."
    Write-Host "Try running the download script again:"
    Write-Host ""
    Write-Host "python download_hebrew_models.py" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "="*60 -ForegroundColor Cyan




