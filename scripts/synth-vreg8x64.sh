#!/usr/bin/env bash
# Synthesize the vector-register block with the pinned OpenROAD image.
set -euo pipefail

image="${OPENROAD_IMAGE:-openroad/orfs@sha256:573c1716efa0e286c4f641c26d343e20929d58d27fffbb22be2d0b93f09764f6}"

docker run --rm --user "$(id -u):$(id -g)" --volume "${PWD}:/workspace:ro" --workdir /workspace "${image}" \
  yosys -p 'read_verilog -sv designs/vreg8x64/rtl/vreg8x64.sv; synth -top vreg8x64; stat'
