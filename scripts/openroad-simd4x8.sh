#!/usr/bin/env bash
# Run an RTL-to-GDSII flow for both VMAC implementations using sky130hd.
set -euo pipefail
image="${OPENROAD_IMAGE:-openroad/orfs@sha256:573c1716efa0e286c4f641c26d343e20929d58d27fffbb22be2d0b93f09764f6}"

for variant in comb iter; do
  docker run --rm --user "$(id -u):$(id -g)" --volume "${PWD}:/work" --workdir /OpenROAD-flow-scripts/flow "${image}" \
    make DESIGN_CONFIG="/work/configs/openroad/simd4x8/${variant}/config.mk" WORK_HOME=/work/.openroad-work
done
