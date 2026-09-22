#!/usr/bin/env bash
set -euo pipefail

base="/source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV"
iverilog -g2012 -s tb_femtorv_step1 -o /tmp/femtorv-step1 "$base/step1.v" /workspace/tests/external/femtorv/tb_femtorv_step1.v
vvp /tmp/femtorv-step1
iverilog -g2012 -DBENCH -I "$base" -s tb_femtorv_step2 -o /tmp/femtorv-step2 "$base/step2.v" /workspace/tests/external/femtorv/tb_femtorv_step2.v
vvp /tmp/femtorv-step2
