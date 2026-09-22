#!/usr/bin/env bash
# Materialize reviewed external RTL after fetching only registered commits.
set -euo pipefail

output="${1:?new output JSONL path required}"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf -- "${tmp}"' EXIT

fetch_pinned() {
  local repository="$1" commit="$2" destination="$3"
  git init --quiet "${destination}"
  git -C "${destination}" remote add origin "${repository}"
  git -C "${destination}" fetch --quiet --depth 1 origin "${commit}"
  git -C "${destination}" checkout --quiet --detach "${commit}"
}

fetch_pinned https://github.com/olofk/serv.git f200eb2ed7b69ac1c6b8eddd47654522aeee5ce8 "${tmp}/serv"
fetch_pinned https://github.com/YosysHQ/picorv32.git ef203c2b0a3fb793280f5114941416c425c5b461 "${tmp}/picorv32"
fetch_pinned https://github.com/VaradaGovind/rtl-riscv32.git c8b8d95d15d8099b02091cf9a6ed53686541e096 "${tmp}/rtl-riscv32"
PYTHONPATH="${root}/src" python3 -m ef_gpu.cli build-external-circuit-corpus \
  --serv-source "${tmp}/serv" --picorv32-source "${tmp}/picorv32" \
  --rtl-riscv32-source "${tmp}/rtl-riscv32" --output "${output}"
