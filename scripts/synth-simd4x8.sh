#!/usr/bin/env bash
# Synthesize both VMAC implementations with the pinned OpenROAD image.
set -euo pipefail
image="${OPENROAD_IMAGE:-openroad/orfs@sha256:573c1716efa0e286c4f641c26d343e20929d58d27fffbb22be2d0b93f09764f6}"

for top in simd4x8_mac_comb_top simd4x8_mac_iter_top; do
  if [[ "$top" == simd4x8_mac_comb_top ]]; then
    sources='designs/simd4x8/rtl/mult8_comb.sv designs/simd4x8/rtl/simd4x8_mac_comb_top.sv'
  else
    sources='designs/simd4x8/rtl/mult8_iter.sv designs/simd4x8/rtl/simd4x8_mult_iter4.sv designs/simd4x8/rtl/simd4x8_mac_iter_top.sv'
  fi
  docker run --rm --user "$(id -u):$(id -g)" --volume "${PWD}:/workspace:ro" --workdir /workspace "${image}" \
    yosys -p "read_verilog -sv ${sources}; synth -top ${top}; stat"
done
