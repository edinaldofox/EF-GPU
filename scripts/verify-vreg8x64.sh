#!/usr/bin/env bash
# Verify the vector-register architectural model and RTL with the pinned simulator image.
set -euo pipefail

image="${EF_GPU_SIM_IMAGE:-ef-gpu-sim:ubuntu24.04-iverilog12-v1}"
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! docker image inspect "${image}" >/dev/null 2>&1; then
    docker build --tag "${image}" --file "${project_root}/docker/sim/Dockerfile" "${project_root}/docker/sim"
fi

docker run --rm \
    --user "$(id -u):$(id -g)" \
    --volume "${project_root}:/workspace:ro" \
    --workdir /workspace \
    "${image}" \
    bash -lc '
        set -euo pipefail
        gcc -std=c11 -Wall -Wextra -Werror -pedantic -Idesigns/vreg8x64/model \
          designs/vreg8x64/model/vreg_ref.c designs/vreg8x64/model/vreg_ref_test.c \
          -o /tmp/vreg_ref_test
        /tmp/vreg_ref_test
        iverilog -g2012 -s tb_vreg8x64 -o /tmp/vreg8x64_tb \
          designs/vreg8x64/rtl/vreg8x64.sv designs/vreg8x64/tb/tb_vreg8x64.sv
        vvp /tmp/vreg8x64_tb
    '
