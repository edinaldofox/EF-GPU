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
    test_command="bash /workspace/scripts/verify-serv-primitives.sh"
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
    test_command="bash /workspace/scripts/verify-fazyrv-primitives.sh"
    ;;
  learn-fpga)
    repository="https://github.com/BrunoLevy/learn-fpga.git"
    commit="5c08c870315c09ccd9ec64ccde20ab3375b3f273"
    license_path="LICENSE"
    license_sha256="dae852f7354066fe13901a60a49ac4f7e45b9ae16fec901e12e24218da0ea999"
    test_command="bash /workspace/scripts/verify-femtorv-tutorial.sh"
    ;;
  fma-rtl)
    repository="https://github.com/Tachyum-Open-Source/fma-rtl.git"
    commit="1e7221349e7b18b1e20f4b301f3b7a34b5ebd490"
    license_path="LICENSE"
    license_sha256="cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
    test_command="bash /workspace/scripts/verify-fma-primitives.sh"
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
