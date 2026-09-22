#!/usr/bin/env bash
# Synthesize a single reviewed external module from its pinned temporary checkout.
set -euo pipefail

source_id="${1:?source id required: serv or picorv32}"
top="${2:?top module required}"
image="${OPENROAD_IMAGE:-openroad/orfs@sha256:573c1716efa0e286c4f641c26d343e20929d58d27fffbb22be2d0b93f09764f6}"
tmp="$(mktemp -d)"
trap 'rm -rf -- "${tmp}"' EXIT

case "${source_id}:${top}" in
  serv:serv_alu|serv:serv_aligner|serv:serv_bufreg|serv:serv_decode|serv:serv_immdec|serv:serv_mem_if|serv:serv_state)
    repository="https://github.com/olofk/serv.git"
    commit="f200eb2ed7b69ac1c6b8eddd47654522aeee5ce8"
    source_glob="/source/rtl/${top}.v"
    ;;
  picorv32:picorv32_pcpi_mul)
    repository="https://github.com/YosysHQ/picorv32.git"
    commit="ef203c2b0a3fb793280f5114941416c425c5b461"
    source_glob="/source/picorv32.v"
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
  "${image}" yosys -p "read_verilog -sv ${source_glob}; synth -top ${top}; stat"
