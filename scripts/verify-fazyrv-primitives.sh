#!/usr/bin/env bash
set -euo pipefail

verify() {
  local top="$1"; shift
  iverilog -g2012 -s "$top" -o "/tmp/$top" "$@"
  vvp "/tmp/$top"
}

verify tb_fazyrv_hadd /source/rtl/fazyrv_hadd.v /workspace/tests/external/fazyrv/tb_fazyrv_hadd.sv
verify tb_fazyrv_fadd /source/rtl/fazyrv_hadd.v /source/rtl/fazyrv_fadd.v /workspace/tests/external/fazyrv/tb_fazyrv_fadd.sv
verify tb_fazyrv_cmp /source/rtl/fazyrv_cmp.v /workspace/tests/external/fazyrv/tb_fazyrv_cmp.sv
verify tb_fazyrv_shftreg -D RISCV_FORMAL /source/rtl/fazyrv_shftreg.sv /workspace/tests/external/fazyrv/tb_fazyrv_shftreg.sv
verify tb_fazyrv_ram_sp -D SIM /source/rtl/fazyrv_ram_sp.sv /workspace/tests/external/fazyrv/tb_fazyrv_ram_sp.sv
verify tb_fazyrv_ram_dp -D SIM /source/rtl/fazyrv_ram_dp.sv /workspace/tests/external/fazyrv/tb_fazyrv_ram_dp.sv
verify tb_fazyrv_align /source/rtl/fazyrv_align.sv /workspace/tests/external/fazyrv/tb_fazyrv_align.sv
verify tb_fazyrv_spm_a /source/rtl/fazyrv_spm_a.sv /workspace/tests/external/fazyrv/tb_fazyrv_spm_a.sv
verify tb_fazyrv_pc /source/rtl/fazyrv_hadd.v /source/rtl/fazyrv_pc.sv /workspace/tests/external/fazyrv/tb_fazyrv_pc.sv
verify tb_fazyrv_rvc /source/rtl/fazyrv_rvc.sv /workspace/tests/external/fazyrv/tb_fazyrv_rvc.sv
