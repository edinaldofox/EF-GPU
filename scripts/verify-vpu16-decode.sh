#!/usr/bin/env bash
# Verify the VPU16 instruction decoder against its C model and RTL testbench.
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
        gcc -std=c11 -Wall -Wextra -Werror -pedantic -Idesigns/vpu16_decode/model \
          designs/vpu16_decode/model/vpu16_decode_ref.c designs/vpu16_decode/model/vpu16_decode_ref_test.c \
          -o /tmp/vpu16_decode_ref_test
        /tmp/vpu16_decode_ref_test
        iverilog -g2012 -s tb_vpu16_decode -o /tmp/vpu16_decode_tb \
          designs/vpu16_decode/rtl/vpu16_decode.sv designs/vpu16_decode/tb/tb_vpu16_decode.sv
        vvp /tmp/vpu16_decode_tb
    '
