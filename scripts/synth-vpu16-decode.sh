#!/usr/bin/env bash
# Synthesize the VPU16 decoder with the pinned OpenROAD image.
set -euo pipefail

image="${OPENROAD_IMAGE:-openroad/orfs@sha256:573c1716efa0e286c4f641c26d343e20929d58d27fffbb22be2d0b93f09764f6}"

docker run --rm --user "$(id -u):$(id -g)" --volume "${PWD}:/workspace:ro" --workdir /workspace "${image}" \
  yosys -p 'read_verilog -sv designs/vpu16_decode/rtl/vpu16_decode.sv; synth -top vpu16_decode; stat'
