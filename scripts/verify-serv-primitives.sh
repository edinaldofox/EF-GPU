#!/usr/bin/env bash
set -euo pipefail

verify() {
  local top="$1" source="$2" testbench="$3"
  iverilog -g2012 -s "$top" -o "/tmp/$top" "/source/$source" "/workspace/$testbench"
  vvp "/tmp/$top"
}

verify tb_serv_alu rtl/serv_alu.v tests/external/serv/tb_serv_alu.sv
verify tb_serv_aligner rtl/serv_aligner.v tests/external/serv/tb_serv_aligner.sv
verify tb_serv_rf_ram rtl/serv_rf_ram.v tests/external/serv/tb_serv_rf_ram.sv
