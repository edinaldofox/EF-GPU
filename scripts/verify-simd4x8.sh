#!/usr/bin/env bash
# Check both SIMD4x8 VMAC RTL variants against deterministic C reference vectors.
set -euo pipefail

image="${EF_GPU_SIM_IMAGE:-ef-gpu-sim:ubuntu24.04-iverilog12-v1}"
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work_dir="$(mktemp -d)"
trap 'rm -rf "${work_dir}"' EXIT

if ! docker image inspect "${image}" >/dev/null 2>&1; then
    docker build --tag "${image}" --file "${project_root}/docker/sim/Dockerfile" "${project_root}/docker/sim"
fi

docker run --rm \
    --user "$(id -u):$(id -g)" \
    --volume "${project_root}:/workspace:ro" \
    --volume "${work_dir}:/work" \
    --workdir /workspace \
    "${image}" \
    bash -lc '
        set -euo pipefail
        gcc -std=c11 -Wall -Wextra -Werror -pedantic -Idesigns/simd4x8/model \
          designs/simd4x8/model/vmac_ref.c designs/simd4x8/model/vmac_ref_test.c \
          -o /work/vmac_ref_test
        /work/vmac_ref_test
        gcc -std=c11 -Wall -Wextra -Werror -pedantic -Idesigns/simd4x8/model \
          designs/simd4x8/model/vmac_ref.c designs/simd4x8/model/vmac_vector_gen.c \
          -o /work/vmac_vector_gen
        /work/vmac_vector_gen /work/vmac_vectors.txt
        iverilog -g2012 -s tb_simd4x8_c_ref -o /work/simd4x8_tb \
          designs/simd4x8/rtl/mult8_comb.sv \
          designs/simd4x8/rtl/mult8_iter.sv \
          designs/simd4x8/rtl/simd4x8_mult_iter4.sv \
          designs/simd4x8/rtl/simd4x8_mac_comb_top.sv \
          designs/simd4x8/rtl/simd4x8_mac_iter_top.sv \
          designs/simd4x8/tb/tb_simd4x8_c_ref.sv
        vvp /work/simd4x8_tb +vectors=/work/vmac_vectors.txt
    '
