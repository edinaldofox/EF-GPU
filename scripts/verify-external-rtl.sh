#!/usr/bin/env bash
# Fetch and check only reviewed external RTL in a disposable directory.
set -euo pipefail

source_id="${1:?source id required: serv or picorv32}"
image="${EF_GPU_SIM_IMAGE:-ef-gpu-sim:ubuntu24.04-iverilog12-v1}"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf -- "${tmp}"' EXIT

case "${source_id}" in
  serv)
    repository="https://github.com/olofk/serv.git"
    commit="f200eb2ed7b69ac1c6b8eddd47654522aeee5ce8"
    license_path="LICENSE"
    license_sha256="d9a1bd691f04280a8369a4aa69b6be20c0e2ee6d164a17ad8a8ef49da8ea0ea9"
    test_command="iverilog -g2012 -s tb_serv_alu -o /tmp/serv-alu /source/rtl/serv_alu.v /workspace/tests/external/serv/tb_serv_alu.sv && vvp /tmp/serv-alu && iverilog -g2012 -s tb_serv_aligner -o /tmp/serv-aligner /source/rtl/serv_aligner.v /workspace/tests/external/serv/tb_serv_aligner.sv && vvp /tmp/serv-aligner"
    ;;
  picorv32)
    repository="https://github.com/YosysHQ/picorv32.git"
    commit="ef203c2b0a3fb793280f5114941416c425c5b461"
    license_path="COPYING"
    license_sha256="041ebc727233e5bf096dd41260cbb81014d3d29ca007a15f3b1807d4e9ff288e"
    test_command="iverilog -g2012 -s tb_picorv32_pcpi_mul -o /tmp/picorv32-mul /source/picorv32.v /workspace/tests/external/picorv32/tb_picorv32_pcpi_mul.sv && vvp /tmp/picorv32-mul"
    ;;
  rtl-riscv32)
    repository="https://github.com/VaradaGovind/rtl-riscv32.git"
    commit="c8b8d95d15d8099b02091cf9a6ed53686541e096"
    license_path="LICENSE"
    license_sha256="5d77a4df434a9f088476a91acefa0f98c46b39ae60e89e8213c4a460ae7fef4e"
    test_command="iverilog -g2012 -s tb_alu -o /tmp/rv-alu /source/RiscV-32bit/RiscV-32bit.srcs/sources_1/new/alu.v /workspace/tests/external/rtl_riscv32/tb_alu.v && vvp /tmp/rv-alu && iverilog -g2012 -s tb_pc -o /tmp/rv-pc /source/RiscV-32bit/RiscV-32bit.srcs/sources_1/new/pc.v /workspace/tests/external/rtl_riscv32/tb_pc.v && vvp /tmp/rv-pc && iverilog -g2012 -s tb_instr_decode -o /tmp/rv-decode /source/RiscV-32bit/RiscV-32bit.srcs/sources_1/new/instr_decode.v /workspace/tests/external/rtl_riscv32/tb_instr_decode.v && vvp /tmp/rv-decode"
    ;;
  fazyrv)
    repository="https://github.com/meiniKi/FazyRV.git"
    commit="c8d9c7971b91c0c166aef6c236f1134b2c6ac1a1"
    license_path="rtl/LICENSE.txt"
    license_sha256="31beba5b18f79bd120e371525c603f057952effd4d6436a584073f3e50537edc"
    test_command="iverilog -g2012 -s tb_fazyrv_hadd -o /tmp/fazyrv-hadd /source/rtl/fazyrv_hadd.v /workspace/tests/external/fazyrv/tb_fazyrv_hadd.sv && vvp /tmp/fazyrv-hadd && iverilog -g2012 -s tb_fazyrv_fadd -o /tmp/fazyrv-fadd /source/rtl/fazyrv_hadd.v /source/rtl/fazyrv_fadd.v /workspace/tests/external/fazyrv/tb_fazyrv_fadd.sv && vvp /tmp/fazyrv-fadd && iverilog -g2012 -s tb_fazyrv_cmp -o /tmp/fazyrv-cmp /source/rtl/fazyrv_cmp.v /workspace/tests/external/fazyrv/tb_fazyrv_cmp.sv && vvp /tmp/fazyrv-cmp && iverilog -g2012 -D RISCV_FORMAL -s tb_fazyrv_shftreg -o /tmp/fazyrv-shftreg /source/rtl/fazyrv_shftreg.sv /workspace/tests/external/fazyrv/tb_fazyrv_shftreg.sv && vvp /tmp/fazyrv-shftreg && iverilog -g2012 -D SIM -s tb_fazyrv_ram_sp -o /tmp/fazyrv-ram-sp /source/rtl/fazyrv_ram_sp.sv /workspace/tests/external/fazyrv/tb_fazyrv_ram_sp.sv && vvp /tmp/fazyrv-ram-sp && iverilog -g2012 -D SIM -s tb_fazyrv_ram_dp -o /tmp/fazyrv-ram-dp /source/rtl/fazyrv_ram_dp.sv /workspace/tests/external/fazyrv/tb_fazyrv_ram_dp.sv && vvp /tmp/fazyrv-ram-dp && iverilog -g2012 -s tb_fazyrv_align -o /tmp/fazyrv-align /source/rtl/fazyrv_align.sv /workspace/tests/external/fazyrv/tb_fazyrv_align.sv && vvp /tmp/fazyrv-align && iverilog -g2012 -s tb_fazyrv_spm_a -o /tmp/fazyrv-spm-a /source/rtl/fazyrv_spm_a.sv /workspace/tests/external/fazyrv/tb_fazyrv_spm_a.sv && vvp /tmp/fazyrv-spm-a && iverilog -g2012 -s tb_fazyrv_pc -o /tmp/fazyrv-pc /source/rtl/fazyrv_hadd.v /source/rtl/fazyrv_pc.sv /workspace/tests/external/fazyrv/tb_fazyrv_pc.sv && vvp /tmp/fazyrv-pc"
    ;;
  *)
    echo "unsupported reviewed source: ${source_id}" >&2
    exit 2
    ;;
esac

git clone --quiet "${repository}" "${tmp}/source"
git -C "${tmp}/source" checkout --quiet --detach "${commit}"
test "$(git -C "${tmp}/source" rev-parse HEAD)" = "${commit}"
test "$(sha256sum "${tmp}/source/${license_path}" | awk '{print $1}')" = "${license_sha256}"

docker run --rm --user "$(id -u):$(id -g)" \
  --volume "${root}:/workspace:ro" --volume "${tmp}/source:/source:ro" \
  --workdir /workspace "${image}" \
  bash -lc "${test_command}"
