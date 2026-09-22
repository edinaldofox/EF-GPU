#!/usr/bin/env bash
# Synthesize the scratchpad block with the pinned OpenROAD image.
set -euo pipefail

image="${OPENROAD_IMAGE:-openroad/orfs@sha256:573c1716efa0e286c4f641c26d343e20929d58d27fffbb22be2d0b93f09764f6}"

docker run --rm --user "$(id -u):$(id -g)" --volume "${PWD}:/workspace:ro" --workdir /workspace "${image}" \
  yosys -p 'read_verilog -sv designs/scratchpad16x64/rtl/scratchpad16x64.sv; synth -top scratchpad16x64; stat'
