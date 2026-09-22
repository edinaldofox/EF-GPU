#!/usr/bin/env bash
set -euo pipefail

verify() {
  local top="$1" source="$2" testbench="$3"
  iverilog -g2012 -s "${top}" -o "/tmp/${top}" "/source/${source}" "/workspace/${testbench}"
  vvp "/tmp/${top}"
}

verify tb_mux2 mux2.v tests/external/fma/tb_mux2.v
verify tb_mux5d mux5d.v tests/external/fma/tb_mux5d.v
verify tb_dff dff.v tests/external/fma/tb_dff.v
verify tb_dffe dffe.v tests/external/fma/tb_dffe.v
verify tb_incrementer incrementer.v tests/external/fma/tb_incrementer.v
verify tb_incrementer_8 incrementer_8.v tests/external/fma/tb_incrementer_8.v
verify tb_incrementer_11 incrementer_11.v tests/external/fma/tb_incrementer_11.v
verify tb_adder10 adder10.v tests/external/fma/tb_adder10.v
verify tb_adder10_no_cin adder10_no_cin.v tests/external/fma/tb_adder10_no_cin.v
verify tb_adder13 adder13.v tests/external/fma/tb_adder13.v
verify tb_adder13_no_cin adder13_no_cin.v tests/external/fma/tb_adder13_no_cin.v
verify tb_adder161_no_cin_no_cout adder161_no_cin_no_cout.v tests/external/fma/tb_adder161_no_cin_no_cout.v
verify tb_adder162_no_cin adder162_no_cin.v tests/external/fma/tb_adder162_no_cin.v
verify tb_left_shifter_28 left_shifter_28.v tests/external/fma/tb_left_shifter_28.v
