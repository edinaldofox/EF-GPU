#!/usr/bin/env bash
set -euo pipefail
image="${OPENROAD_IMAGE:-openroad/orfs@sha256:573c1716efa0e286c4f641c26d343e20929d58d27fffbb22be2d0b93f09764f6}"
docker run --rm --user "$(id -u):$(id -g)" --volume "${PWD}:/workspace:ro" --workdir /workspace "${image}" \
  yosys -p 'read_verilog -sv designs/vpu16_sequencer/rtl/vpu16_sequencer.sv; synth -top vpu16_sequencer; stat'
