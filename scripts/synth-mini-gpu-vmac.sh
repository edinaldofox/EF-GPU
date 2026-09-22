#!/usr/bin/env bash
# Synthesize the first integrated mini-GPU VMAC core with the pinned OpenROAD image.
set -euo pipefail

image="${OPENROAD_IMAGE:-openroad/orfs@sha256:573c1716efa0e286c4f641c26d343e20929d58d27fffbb22be2d0b93f09764f6}"

docker run --rm --user "$(id -u):$(id -g)" --volume "${PWD}:/workspace:ro" --workdir /workspace "${image}" \
  yosys -p 'read_verilog -sv designs/vreg8x64/rtl/vreg8x64.sv designs/vpu16_decode/rtl/vpu16_decode.sv designs/simd4x8/rtl/mult8_comb.sv designs/simd4x8/rtl/simd4x8_mac_comb_top.sv designs/mini_gpu_vmac/rtl/mini_gpu_vmac_core.sv; synth -top mini_gpu_vmac_core; stat'
