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
verify tb_serv_rf_ram_w1 rtl/serv_rf_ram.v tests/external/serv/tb_serv_rf_ram_w1.sv
verify tb_serv_rf_ram_w2 rtl/serv_rf_ram.v tests/external/serv/tb_serv_rf_ram_w2.sv
verify tb_serv_rf_ram_w4 rtl/serv_rf_ram.v tests/external/serv/tb_serv_rf_ram_w4.sv
verify tb_serv_rf_ram_w16 rtl/serv_rf_ram.v tests/external/serv/tb_serv_rf_ram_w16.sv
verify tb_serv_rf_ram_w32 rtl/serv_rf_ram.v tests/external/serv/tb_serv_rf_ram_w32.sv
verify tb_serv_rf_ram_w8_c4 rtl/serv_rf_ram.v tests/external/serv/tb_serv_rf_ram_w8_c4.sv
verify tb_serv_rf_ram_w16_c4 rtl/serv_rf_ram.v tests/external/serv/tb_serv_rf_ram_w16_c4.sv
verify tb_serv_rf_ram_w32_c4 rtl/serv_rf_ram.v tests/external/serv/tb_serv_rf_ram_w32_c4.sv
verify tb_serv_bufreg2 rtl/serv_bufreg2.v tests/external/serv/tb_serv_bufreg2.sv
verify tb_serv_immdec rtl/serv_immdec.v tests/external/serv/tb_serv_immdec.sv
