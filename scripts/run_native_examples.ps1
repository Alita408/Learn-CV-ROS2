param(
    [string]$EnvironmentName = "robotlab"
)

$ErrorActionPreference = "Stop"
$examples = @(
    "p01_camera_geometry",
    "p02_color_detection",
    "p03_astar_grid",
    "p04_rrt_star",
    "p05_dwa_local_planner",
    "p06_ekf_localization",
    "p07_perception_to_planning"
)

foreach ($example in $examples) {
    Write-Host "Running $example"
    conda run -n $EnvironmentName python -m "examples.$example"
    if ($LASTEXITCODE -ne 0) {
        throw "$example failed with exit code $LASTEXITCODE"
    }
}

Write-Host "All core examples completed. Results are in outputs/."
