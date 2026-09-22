#!/usr/bin/env bash
# Synthesize the registered ALU8 top and print technology-independent statistics.
set -euo pipefail

image="${OPENROAD_IMAGE:-openroad/orfs@sha256:573c1716efa0e286c4f641c26d343e20929d58d27fffbb22be2d0b93f09764f6}"

exec docker run --rm \
  --user "$(id -u):$(id -g)" \
  --volume "${PWD}:/workspace:ro" \
  --workdir /workspace \
  "${image}" yosys -p '
    read_verilog -sv designs/alu8/rtl/alu8_core.sv designs/alu8/rtl/ef_gpu_alu8.sv
    synth -top ef_gpu_alu8
    stat
  '
