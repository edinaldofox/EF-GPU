#!/usr/bin/env bash
set -euo pipefail
image="${OPENROAD_IMAGE:-openroad/orfs@sha256:573c1716efa0e286c4f641c26d343e20929d58d27fffbb22be2d0b93f09764f6}"
top="${1:?top module required}"
docker run --rm --user "$(id -u):$(id -g)" --volume "${PWD}:/workspace:ro" --workdir /workspace "${image}" yosys -p "read_verilog -sv designs/circuit_primitives/rtl/*.sv; synth -top ${top}; stat"
