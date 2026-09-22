#!/usr/bin/env bash
# Verify the first integrated mini-GPU VMAC core against its C reference and RTL testbench.
set -euo pipefail

image="${EF_GPU_SIM_IMAGE:-ef-gpu-sim:ubuntu24.04-iverilog12-v1}"
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! docker image inspect "${image}" >/dev/null 2>&1; then
    docker build --tag "${image}" --file "${project_root}/docker/sim/Dockerfile" "${project_root}/docker/sim"
fi

docker run --rm \
    --user "$(id -u):$(id -g)" \
    --volume "${project_root}:/workspace:ro" \
    --workdir /workspace \
    "${image}" \
    bash -lc '
        set -euo pipefail
        gcc -std=c11 -Wall -Wextra -Werror -pedantic -Idesigns/mini_gpu_vmac/model \
          designs/mini_gpu_vmac/model/mini_gpu_vmac_ref.c designs/mini_gpu_vmac/model/mini_gpu_vmac_ref_test.c \
          -o /tmp/mini_gpu_vmac_ref_test
        /tmp/mini_gpu_vmac_ref_test
        iverilog -g2012 -s tb_mini_gpu_vmac_core -o /tmp/mini_gpu_vmac_tb \
          designs/vreg8x64/rtl/vreg8x64.sv \
          designs/scratchpad16x64/rtl/scratchpad16x64.sv \
          designs/vpu16_decode/rtl/vpu16_decode.sv \
          designs/simd4x8/rtl/mult8_comb.sv \
          designs/simd4x8/rtl/simd4x8_mac_comb_top.sv \
          designs/mini_gpu_vmac/rtl/mini_gpu_vmac_core.sv \
          designs/mini_gpu_vmac/tb/tb_mini_gpu_vmac_core.sv
        vvp /tmp/mini_gpu_vmac_tb
    '
