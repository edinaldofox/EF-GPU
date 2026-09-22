#!/usr/bin/env bash
set -euo pipefail
group="${1:?group required}"; image="${EF_GPU_SIM_IMAGE:-ef-gpu-sim:ubuntu24.04-iverilog12-v1}"; root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
docker run --rm --user "$(id -u):$(id -g)" --volume "${root}:/workspace:ro" --workdir /workspace "${image}" bash -lc "iverilog -g2012 -s tb_${group} -o /tmp/${group} designs/${group}/rtl/*.sv designs/${group}/tb/tb_${group}.sv && vvp /tmp/${group}"
