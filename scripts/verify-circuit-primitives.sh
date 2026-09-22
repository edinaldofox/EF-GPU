#!/usr/bin/env bash
set -euo pipefail
image="${EF_GPU_SIM_IMAGE:-ef-gpu-sim:ubuntu24.04-iverilog12-v1}"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
docker run --rm --user "$(id -u):$(id -g)" --volume "${root}:/workspace:ro" --workdir /workspace "${image}" bash -lc 'iverilog -g2012 -s tb_circuit_primitives -o /tmp/primitives designs/circuit_primitives/rtl/*.sv designs/circuit_primitives/tb/tb_circuit_primitives.sv && vvp /tmp/primitives'
