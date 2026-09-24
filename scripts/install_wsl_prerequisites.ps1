$ErrorActionPreference = "Stop"

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
$isAdministrator = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdministrator) {
    throw "Run this script from an Administrator PowerShell. It enables Windows features and may require a restart."
}

wsl --install --no-distribution
if ($LASTEXITCODE -ne 0) {
    throw "wsl installation failed with exit code $LASTEXITCODE"
}

Write-Host "WSL prerequisites requested. Restart Windows before continuing."
Write-Host "After restart run: wsl --update"
Write-Host "Then run: wsl --install -d Ubuntu-24.04 --location D:\WSL\Ubuntu-24.04"
