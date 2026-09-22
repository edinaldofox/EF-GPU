#!/usr/bin/env bash
# Synthesize a single reviewed external module from its pinned temporary checkout.
set -euo pipefail

source_id="${1:?source id required: serv or picorv32}"
top="${2:?top module required}"
image="${OPENROAD_IMAGE:-openroad/orfs@sha256:573c1716efa0e286c4f641c26d343e20929d58d27fffbb22be2d0b93f09764f6}"
tmp="$(mktemp -d)"
trap 'rm -rf -- "${tmp}"' EXIT

case "${source_id}:${top}" in
  serv:serv_alu|serv:serv_aligner|serv:serv_bufreg|serv:serv_bufreg2|serv:serv_decode|serv:serv_immdec|serv:serv_mem_if|serv:serv_state)
    repository="https://github.com/olofk/serv.git"
    commit="f200eb2ed7b69ac1c6b8eddd47654522aeee5ce8"
    source_glob="/source/rtl/${top}.v"
    ;;
  serv:serv_rf_ram_w1|serv:serv_rf_ram_w2|serv:serv_rf_ram_w4|serv:serv_rf_ram|serv:serv_rf_ram_w16|serv:serv_rf_ram_w32|serv:serv_rf_ram_w8_c4|serv:serv_rf_ram_w16_c4|serv:serv_rf_ram_w32_c4)
    repository="https://github.com/olofk/serv.git"
    commit="f200eb2ed7b69ac1c6b8eddd47654522aeee5ce8"
    source_glob="/source/rtl/serv_rf_ram.v"
    read_options="-defer"
    case "${top}" in
      serv_rf_ram_w1) parameterize="chparam -set width 1 -set csr_regs 0 -set depth 1024 serv_rf_ram; " ;;
      serv_rf_ram_w2) parameterize="chparam -set width 2 -set csr_regs 0 -set depth 512 serv_rf_ram; " ;;
      serv_rf_ram_w4) parameterize="chparam -set width 4 -set csr_regs 0 -set depth 256 serv_rf_ram; " ;;
      serv_rf_ram) parameterize="chparam -set width 8 -set csr_regs 0 -set depth 128 serv_rf_ram; " ;;
      serv_rf_ram_w16) parameterize="chparam -set width 16 -set csr_regs 0 -set depth 64 serv_rf_ram; " ;;
      serv_rf_ram_w32) parameterize="chparam -set width 32 -set csr_regs 0 -set depth 32 serv_rf_ram; " ;;
      serv_rf_ram_w8_c4) parameterize="chparam -set width 8 -set csr_regs 4 -set depth 144 serv_rf_ram; " ;;
      serv_rf_ram_w16_c4) parameterize="chparam -set width 16 -set csr_regs 4 -set depth 72 serv_rf_ram; " ;;
      serv_rf_ram_w32_c4) parameterize="chparam -set width 32 -set csr_regs 4 -set depth 36 serv_rf_ram; " ;;
    esac
    top="serv_rf_ram"
    ;;
  picorv32:picorv32_pcpi_mul)
    repository="https://github.com/YosysHQ/picorv32.git"
    commit="ef203c2b0a3fb793280f5114941416c425c5b461"
    source_glob="/source/picorv32.v"
    ;;
  rtl-riscv32:alu|rtl-riscv32:pc|rtl-riscv32:instr_decode)
    repository="https://github.com/VaradaGovind/rtl-riscv32.git"
    commit="c8b8d95d15d8099b02091cf9a6ed53686541e096"
    source_glob="/source/RiscV-32bit/RiscV-32bit.srcs/sources_1/new/${top}.v"
    ;;
  fazyrv:fazyrv_hadd|fazyrv:fazyrv_cmp)
    repository="https://github.com/meiniKi/FazyRV.git"
    commit="c8d9c7971b91c0c166aef6c236f1134b2c6ac1a1"
    source_glob="/source/rtl/${top}.v"
    ;;
  fazyrv:fazyrv_fadd)
    repository="https://github.com/meiniKi/FazyRV.git"
    commit="c8d9c7971b91c0c166aef6c236f1134b2c6ac1a1"
    source_glob="/source/rtl/fazyrv_hadd.v /source/rtl/fazyrv_fadd.v"
    ;;
  fazyrv:fazyrv_shftreg|fazyrv:fazyrv_ram_sp|fazyrv:fazyrv_ram_dp|fazyrv:fazyrv_align)
    repository="https://github.com/meiniKi/FazyRV.git"
    commit="c8d9c7971b91c0c166aef6c236f1134b2c6ac1a1"
    source_glob="/source/rtl/${top}.sv"
    ;;
  fazyrv:fazyrv_spm_a)
    repository="https://github.com/meiniKi/FazyRV.git"
    commit="c8d9c7971b91c0c166aef6c236f1134b2c6ac1a1"
    source_glob="/source/rtl/fazyrv_spm_a.sv"
    ;;
  fazyrv:fazyrv_pc)
    repository="https://github.com/meiniKi/FazyRV.git"
    commit="c8d9c7971b91c0c166aef6c236f1134b2c6ac1a1"
    source_glob="/source/rtl/fazyrv_hadd.v /source/rtl/fazyrv_pc.sv"
    ;;
  fazyrv:fazyrv_rvc)
    repository="https://github.com/meiniKi/FazyRV.git"
    commit="c8d9c7971b91c0c166aef6c236f1134b2c6ac1a1"
    source_glob="/source/rtl/fazyrv_rvc.sv"
    ;;
  learn-fpga:SOC)
    repository="https://github.com/BrunoLevy/learn-fpga.git"
    commit="5c08c870315c09ccd9ec64ccde20ab3375b3f273"
    source_glob="/source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV/step1.v"
    ;;
  learn-fpga:SOC_step2)
    repository="https://github.com/BrunoLevy/learn-fpga.git"
    commit="5c08c870315c09ccd9ec64ccde20ab3375b3f273"
    source_glob="-I/source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV /source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV/step2.v"
    top="SOC"
    ;;
  learn-fpga:SOC_step3)
    repository="https://github.com/BrunoLevy/learn-fpga.git"
    commit="5c08c870315c09ccd9ec64ccde20ab3375b3f273"
    source_glob="-I/source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV /source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV/step3.v"
    top="SOC"
    ;;
  learn-fpga:SOC_step4)
    repository="https://github.com/BrunoLevy/learn-fpga.git"
    commit="5c08c870315c09ccd9ec64ccde20ab3375b3f273"
    source_glob="-I/source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV /source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV/step4.v"
    top="SOC"
    ;;
  learn-fpga:SOC_step5)
    repository="https://github.com/BrunoLevy/learn-fpga.git"
    commit="5c08c870315c09ccd9ec64ccde20ab3375b3f273"
    source_glob="-I/source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV /source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV/step5.v"
    top="SOC"
    ;;
  learn-fpga:SOC_step6)
    repository="https://github.com/BrunoLevy/learn-fpga.git"
    commit="5c08c870315c09ccd9ec64ccde20ab3375b3f273"
    source_glob="-I/source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV /source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV/step6.v"
    top="SOC"
    ;;
  learn-fpga:SOC_step7)
    repository="https://github.com/BrunoLevy/learn-fpga.git"
    commit="5c08c870315c09ccd9ec64ccde20ab3375b3f273"
    source_glob="-I/source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV /source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV/step7.v"
    top="SOC"
    ;;
  learn-fpga:SOC_step8)
    repository="https://github.com/BrunoLevy/learn-fpga.git"
    commit="5c08c870315c09ccd9ec64ccde20ab3375b3f273"
    source_glob="-I/source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV /source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV/step8.v"
    top="SOC"
    ;;
  learn-fpga:SOC_step9)
    repository="https://github.com/BrunoLevy/learn-fpga.git"
    commit="5c08c870315c09ccd9ec64ccde20ab3375b3f273"
    source_glob="-I/source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV /source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV/step9.v"
    top="SOC"
    ;;
  learn-fpga:SOC_step10)
    repository="https://github.com/BrunoLevy/learn-fpga.git"
    commit="5c08c870315c09ccd9ec64ccde20ab3375b3f273"
    source_glob="-I/source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV /source/FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV/step10.v"
    top="SOC"
    ;;
  fma-rtl:mux2|fma-rtl:mux5d|fma-rtl:dff|fma-rtl:dffe|fma-rtl:incrementer|fma-rtl:incrementer_8|fma-rtl:incrementer_11|fma-rtl:adder10|fma-rtl:adder10_no_cin|fma-rtl:adder13|fma-rtl:adder13_no_cin|fma-rtl:adder161_no_cin_no_cout|fma-rtl:adder162_no_cin|fma-rtl:left_shifter_28|fma-rtl:left_shifter_76|fma-rtl:left_shifter_163|fma-rtl:right_shifter_26_with_outside_bits|fma-rtl:right_shifter_74_with_outside_bits|fma-rtl:right_shifter_161_with_outside_bits)
    repository="https://github.com/Tachyum-Open-Source/fma-rtl.git"
    commit="1e7221349e7b18b1e20f4b301f3b7a34b5ebd490"
    source_glob="/source/${top}.v"
    ;;
  *)
    echo "unreviewed source/top pair: ${source_id}:${top}" >&2
    exit 2
    ;;
esac

git clone --quiet "${repository}" "${tmp}/source"
git -C "${tmp}/source" checkout --quiet --detach "${commit}"
test "$(git -C "${tmp}/source" rev-parse HEAD)" = "${commit}"
docker run --rm --user "$(id -u):$(id -g)" --volume "${tmp}/source:/source:ro" \
  "${image}" yosys -p "read_verilog ${read_options:-} -sv ${source_glob}; ${parameterize:-}synth -top ${top}; stat"
