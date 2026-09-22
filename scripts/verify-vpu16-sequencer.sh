#!/usr/bin/env bash
set -euo pipefail
image="${EF_GPU_SIM_IMAGE:-ef-gpu-sim:ubuntu24.04-iverilog12-v1}"
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
docker run --rm --user "$(id -u):$(id -g)" --volume "${project_root}:/workspace:ro" --workdir /workspace "${image}" bash -lc '
  set -euo pipefail
  iverilog -g2012 -s tb_vpu16_program -o /tmp/vpu16_program_tb \
    designs/vreg8x64/rtl/vreg8x64.sv designs/scratchpad16x64/rtl/scratchpad16x64.sv \
    designs/vpu16_decode/rtl/vpu16_decode.sv designs/simd4x8/rtl/mult8_comb.sv \
    designs/simd4x8/rtl/simd4x8_mac_comb_top.sv designs/mini_gpu_vmac/rtl/mini_gpu_vmac_core.sv \
    designs/vpu16_sequencer/rtl/vpu16_sequencer.sv designs/vpu16_sequencer/tb/tb_vpu16_program.sv
  vvp /tmp/vpu16_program_tb
'
