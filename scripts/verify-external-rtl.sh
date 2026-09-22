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
    testbench="/workspace/tests/external/serv/tb_serv_external.sv"
    sources="/source/rtl/serv_aligner.v /source/rtl/serv_alu.v"
    top="tb_serv_external"
    ;;
  picorv32)
    repository="https://github.com/YosysHQ/picorv32.git"
    commit="ef203c2b0a3fb793280f5114941416c425c5b461"
    license_path="COPYING"
    license_sha256="041ebc727233e5bf096dd41260cbb81014d3d29ca007a15f3b1807d4e9ff288e"
    testbench="/workspace/tests/external/picorv32/tb_picorv32_pcpi_mul.sv"
    sources="/source/picorv32.v"
    top="tb_picorv32_pcpi_mul"
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
  bash -lc "iverilog -g2012 -s ${top} -o /tmp/external-rtl ${sources} ${testbench} && vvp /tmp/external-rtl"
