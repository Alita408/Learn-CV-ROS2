$ErrorActionPreference = "Stop"

if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "Docker is already available."
    exit 0
}

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    throw "winget was not found. Install Docker Desktop manually from docs.docker.com."
}

winget install --exact --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
if ($LASTEXITCODE -ne 0) {
    throw "Docker Desktop installation failed with exit code $LASTEXITCODE"
}

Write-Host "Docker Desktop installation finished or was queued."
Write-Host "Open Docker Desktop, enable the WSL2 backend, and move its disk image to D: in Settings."
