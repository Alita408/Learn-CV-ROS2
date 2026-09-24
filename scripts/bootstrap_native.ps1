param(
    [string]$EnvironmentName = "robotlab"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    throw "conda was not found. Install Miniconda/Anaconda or use: python -m pip install -e ."
}

$environmentExists = conda env list | Select-String -Pattern "^$([regex]::Escape($EnvironmentName))\s"
if ($LASTEXITCODE -ne 0) {
    throw "conda env list failed with exit code $LASTEXITCODE"
}
if (-not $environmentExists) {
    conda create -n $EnvironmentName python=3.11 pip -y
    if ($LASTEXITCODE -ne 0) {
        throw "conda create failed with exit code $LASTEXITCODE"
    }
}

conda run -n $EnvironmentName python -m pip install -e ".[dev]"
if ($LASTEXITCODE -ne 0) {
    throw "dependency installation failed with exit code $LASTEXITCODE"
}
conda run -n $EnvironmentName python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) {
    throw "tests failed with exit code $LASTEXITCODE"
}

Write-Host "Native environment is ready."
Write-Host "Run: conda run -n $EnvironmentName python -m examples.p07_perception_to_planning"
