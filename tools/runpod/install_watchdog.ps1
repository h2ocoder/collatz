# Installs the hourly RunPod watchdog as a Windows scheduled task.
#
#   pwsh tools/runpod/install_watchdog.ps1              install / update
#   pwsh tools/runpod/install_watchdog.ps1 -Remove      uninstall
#
# The scripts are COPIED to ~/.runpod/ so the task keeps working if this git worktree is
# deleted. The API key is read at run time from the RUNPOD_API_KEY user environment variable
# or from ~/.runpod/api_key; this installer never sees it.
param([switch]$Remove)

$TaskName = "CollatzRunPodWatchdog"
$Target = Join-Path $HOME ".runpod"

if ($Remove) {
    schtasks /Delete /TN $TaskName /F
    Write-Host "Removed scheduled task $TaskName. Files in $Target were left in place."
    exit 0
}

New-Item -ItemType Directory -Force $Target | Out-Null
Copy-Item (Join-Path $PSScriptRoot "runpod_api.py") $Target -Force
Copy-Item (Join-Path $PSScriptRoot "watchdog.py") $Target -Force

$Python = (Get-Command python -ErrorAction SilentlyContinue | Where-Object { $_.Source -notlike "*WindowsApps*" } | Select-Object -First 1).Source
if (-not $Python) { throw "python.exe not found on PATH" }
$Pythonw = Join-Path (Split-Path $Python) "pythonw.exe"
if (-not (Test-Path $Pythonw)) { $Pythonw = $Python }

# pythonw = no console window flashing up every hour
$Action = "`"$Pythonw`" `"$(Join-Path $Target 'watchdog.py')`""
schtasks /Create /TN $TaskName /TR $Action /SC HOURLY /MO 1 /F | Out-Null
Write-Host "Installed: $TaskName runs hourly -> $Action"
Write-Host "Log: $(Join-Path $Target 'watchdog.log')"
Write-Host "Test it now with:  python `"$(Join-Path $Target 'watchdog.py')`""
