#!/usr/bin/env bash
set -euo pipefail

image_name="${1:-learncv/robotics-jazzy:2026-09-24}"
output_dir="${2:-/mnt/d/RobotImages}"
archive_name="robotics-jazzy-20260924.tar.zst"

command -v docker >/dev/null || { echo "docker is required" >&2; exit 1; }
command -v zstd >/dev/null || { echo "zstd is required: sudo apt install zstd" >&2; exit 1; }

mkdir -p "${output_dir}"
docker image inspect "${image_name}" >/dev/null
docker save "${image_name}" | zstd -T0 -10 -o "${output_dir}/${archive_name}"
(cd "${output_dir}" && sha256sum "${archive_name}" > "${archive_name}.sha256")

echo "Exported ${output_dir}/${archive_name}"
