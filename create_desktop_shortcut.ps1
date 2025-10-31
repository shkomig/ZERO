# PowerShell script to create desktop shortcut
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Zero Agent.lnk')
$Shortcut.TargetPath = 'C:\AI-ALL-PRO\ZERO\Zero_Agent_Complete.bat'
$Shortcut.WorkingDirectory = 'C:\AI-ALL-PRO\ZERO'
$Shortcut.Description = 'Start Zero Agent AI System'
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully!"
Write-Host "You can now double-click 'Zero Agent' on your desktop to start the system."



