#!/usr/bin/env bash
set -euo pipefail

base="/source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV"
iverilog -g2012 -s tb_femtorv_step1 -o /tmp/femtorv-step1 "$base/step1.v" /workspace/tests/external/femtorv/tb_femtorv_step1.v
vvp /tmp/femtorv-step1
iverilog -g2012 -DBENCH -I "$base" -s tb_femtorv_step2 -o /tmp/femtorv-step2 "$base/step2.v" /workspace/tests/external/femtorv/tb_femtorv_step2.v
vvp /tmp/femtorv-step2
iverilog -g2012 -DBENCH -I "$base" -s tb_femtorv_step3 -o /tmp/femtorv-step3 "$base/step3.v" /workspace/tests/external/femtorv/tb_femtorv_step3.v
vvp /tmp/femtorv-step3
iverilog -g2012 -DBENCH -I "$base" -s tb_femtorv_step4 -o /tmp/femtorv-step4 "$base/step4.v" /workspace/tests/external/femtorv/tb_femtorv_step4.v
vvp /tmp/femtorv-step4
iverilog -g2012 -DBENCH -I "$base" -s tb_femtorv_step5 -o /tmp/femtorv-step5 "$base/step5.v" /workspace/tests/external/femtorv/tb_femtorv_step5.v
vvp /tmp/femtorv-step5
iverilog -g2012 -DBENCH -I "$base" -s tb_femtorv_step6 -o /tmp/femtorv-step6 "$base/step6.v" /workspace/tests/external/femtorv/tb_femtorv_step6.v
vvp /tmp/femtorv-step6
iverilog -g2012 -DBENCH -I "$base" -s tb_femtorv_step7 -o /tmp/femtorv-step7 "$base/step7.v" /workspace/tests/external/femtorv/tb_femtorv_step7.v
vvp /tmp/femtorv-step7
iverilog -g2012 -DBENCH -I "$base" -s tb_femtorv_step8 -o /tmp/femtorv-step8 "$base/step8.v" /workspace/tests/external/femtorv/tb_femtorv_step8.v
vvp /tmp/femtorv-step8
iverilog -g2012 -DBENCH -I "$base" -s tb_femtorv_step9 -o /tmp/femtorv-step9 "$base/step9.v" /workspace/tests/external/femtorv/tb_femtorv_step9.v
vvp /tmp/femtorv-step9
iverilog -g2012 -I "$base" -s tb_femtorv_step10 -o /tmp/femtorv-step10 "$base/step10.v" /workspace/tests/external/femtorv/tb_femtorv_step10.v
vvp /tmp/femtorv-step10
