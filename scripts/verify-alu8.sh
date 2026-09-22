#!/usr/bin/env bash
# Prove every input combination of the combinational ALU8 core with Yosys SAT.
set -euo pipefail

image="${OPENROAD_IMAGE:-openroad/orfs@sha256:573c1716efa0e286c4f641c26d343e20929d58d27fffbb22be2d0b93f09764f6}"

exec docker run --rm \
  --user "$(id -u):$(id -g)" \
  --volume "${PWD}:/workspace:ro" \
  --workdir /workspace \
  "${image}" yosys -p '
    read_verilog -sv -formal designs/alu8/rtl/alu8_core.sv designs/alu8/formal/alu8_core_formal.sv
    prep -top alu8_core_formal -flatten
    sat -verify -prove fail 0 -show-inputs -show-outputs
  '
