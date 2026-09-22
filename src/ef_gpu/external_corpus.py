"""Materialize a small, reviewed external RTL corpus from pinned checkouts."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ef_gpu.circuit_data import validate_circuit_dataset


ROOT = Path(__file__).resolve().parents[2]

SOURCES: dict[str, dict[str, str]] = {
    "serv": {
        "repository": "https://github.com/olofk/serv.git",
        "commit": "f200eb2ed7b69ac1c6b8eddd47654522aeee5ce8",
        "license": "ISC",
        "license_path": "LICENSE",
        "license_sha256": "d9a1bd691f04280a8369a4aa69b6be20c0e2ee6d164a17ad8a8ef49da8ea0ea9",
    },
    "picorv32": {
        "repository": "https://github.com/YosysHQ/picorv32.git",
        "commit": "ef203c2b0a3fb793280f5114941416c425c5b461",
        "license": "ISC",
        "license_path": "COPYING",
        "license_sha256": "041ebc727233e5bf096dd41260cbb81014d3d29ca007a15f3b1807d4e9ff288e",
    },
    "rtl-riscv32": {
        "repository": "https://github.com/VaradaGovind/rtl-riscv32.git",
        "commit": "c8b8d95d15d8099b02091cf9a6ed53686541e096",
        "license": "MIT",
        "license_path": "LICENSE",
        "license_sha256": "5d77a4df434a9f088476a91acefa0f98c46b39ae60e89e8213c4a460ae7fef4e",
    },
    "fazyrv": {
        "repository": "https://github.com/meiniKi/FazyRV.git",
        "commit": "c8d9c7971b91c0c166aef6c236f1134b2c6ac1a1",
        "license": "MIT",
        "license_path": "rtl/LICENSE.txt",
        "license_sha256": "31beba5b18f79bd120e371525c603f057952effd4d6436a584073f3e50537edc",
    },
}

EXAMPLES: tuple[dict[str, Any], ...] = (
    {
        "id": "serv-alu-001",
        "source_id": "serv",
        "split": "train",
        "design_family": "serv_serial_alu",
        "source_path": "rtl/serv_alu.v",
        "testbench": "tests/external/serv/tb_serv_alu.sv",
        "specification": "Implement the pinned SERV one-bit serial ALU with add, boolean and compare datapaths.",
        "verification_command": "./scripts/verify-external-rtl.sh serv && ./scripts/synth-external-rtl.sh serv serv_alu",
    },
    {
        "id": "serv-aligner-001",
        "source_id": "serv",
        "split": "train",
        "design_family": "serv_instruction_aligner",
        "source_path": "rtl/serv_aligner.v",
        "testbench": "tests/external/serv/tb_serv_aligner.sv",
        "specification": "Implement the pinned SERV instruction-bus aligner, including half-word realignment after a misaligned fetch.",
        "verification_command": "./scripts/verify-external-rtl.sh serv && ./scripts/synth-external-rtl.sh serv serv_aligner",
    },
    {
        "id": "picorv32-pcpi-mul-001",
        "source_id": "picorv32",
        "split": "benchmark",
        "design_family": "picorv32_iterative_pcpi_multiplier",
        "source_path": "picorv32.v",
        "module": "picorv32_pcpi_mul",
        "testbench": "tests/external/picorv32/tb_picorv32_pcpi_mul.sv",
        "specification": "Implement the pinned PicoRV32 iterative PCPI multiplier for the RISC-V M-extension MUL instruction.",
        "verification_command": "./scripts/verify-external-rtl.sh picorv32 && ./scripts/synth-external-rtl.sh picorv32 picorv32_pcpi_mul",
    },
    {
        "id": "rtl-riscv32-pc-001",
        "source_id": "rtl-riscv32",
        "split": "validation",
        "design_family": "rtl_riscv32_program_counter",
        "source_path": "RiscV-32bit/RiscV-32bit.srcs/sources_1/new/pc.v",
        "testbench": "tests/external/rtl_riscv32/tb_pc.v",
        "specification": "Implement the pinned RTL-RISCV32 program counter with asynchronous reset and synchronous next-PC capture.",
        "verification_command": "./scripts/verify-external-rtl.sh rtl-riscv32 && ./scripts/synth-external-rtl.sh rtl-riscv32 pc",
    },
    {
        "id": "fazyrv-hadd-001",
        "source_id": "fazyrv",
        "split": "train",
        "design_family": "fazyrv_half_adder",
        "source_path": "rtl/fazyrv_hadd.v",
        "testbench": "tests/external/fazyrv/tb_fazyrv_hadd.sv",
        "specification": "Implement the pinned FazyRV one-bit half-adder with sum and carry outputs.",
        "verification_command": "./scripts/verify-external-rtl.sh fazyrv && ./scripts/synth-external-rtl.sh fazyrv fazyrv_hadd",
    },
    {
        "id": "fazyrv-fadd-001",
        "source_id": "fazyrv",
        "split": "train",
        "design_family": "fazyrv_full_adder",
        "source_path": "rtl/fazyrv_fadd.v",
        "dependencies": ("rtl/fazyrv_hadd.v",),
        "testbench": "tests/external/fazyrv/tb_fazyrv_fadd.sv",
        "specification": "Implement the pinned FazyRV one-bit full-adder and its half-adder dependency.",
        "verification_command": "./scripts/verify-external-rtl.sh fazyrv && ./scripts/synth-external-rtl.sh fazyrv fazyrv_fadd",
    },
    {
        "id": "fazyrv-cmp-001",
        "source_id": "fazyrv",
        "split": "train",
        "design_family": "fazyrv_chunk_comparator",
        "source_path": "rtl/fazyrv_cmp.v",
        "testbench": "tests/external/fazyrv/tb_fazyrv_cmp.sv",
        "specification": "Implement the pinned FazyRV parameterized chunk comparator, including signed-MSB inversion.",
        "verification_command": "./scripts/verify-external-rtl.sh fazyrv && ./scripts/synth-external-rtl.sh fazyrv fazyrv_cmp",
    },
    {
        "id": "fazyrv-shftreg-001", "source_id": "fazyrv", "split": "train", "design_family": "fazyrv_shift_register",
        "source_path": "rtl/fazyrv_shftreg.sv", "testbench": "tests/external/fazyrv/tb_fazyrv_shftreg.sv",
        "specification": "Implement the pinned FazyRV parameterized serial shift register.",
        "verification_command": "./scripts/verify-external-rtl.sh fazyrv && ./scripts/synth-external-rtl.sh fazyrv fazyrv_shftreg",
    },
    {
        "id": "fazyrv-ram-sp-001", "source_id": "fazyrv", "split": "train", "design_family": "fazyrv_single_port_ram",
        "source_path": "rtl/fazyrv_ram_sp.sv", "testbench": "tests/external/fazyrv/tb_fazyrv_ram_sp.sv",
        "specification": "Implement the pinned FazyRV synchronous single-port register RAM.",
        "verification_command": "./scripts/verify-external-rtl.sh fazyrv && ./scripts/synth-external-rtl.sh fazyrv fazyrv_ram_sp",
    },
    {
        "id": "fazyrv-ram-dp-001", "source_id": "fazyrv", "split": "train", "design_family": "fazyrv_dual_port_ram",
        "source_path": "rtl/fazyrv_ram_dp.sv", "testbench": "tests/external/fazyrv/tb_fazyrv_ram_dp.sv",
        "specification": "Implement the pinned FazyRV synchronous dual-read-port register RAM.",
        "verification_command": "./scripts/verify-external-rtl.sh fazyrv && ./scripts/synth-external-rtl.sh fazyrv fazyrv_ram_dp",
    },
    {
        "id": "fazyrv-align-001", "source_id": "fazyrv", "split": "train", "design_family": "fazyrv_memory_aligner",
        "source_path": "rtl/fazyrv_align.sv", "testbench": "tests/external/fazyrv/tb_fazyrv_align.sv",
        "specification": "Implement the pinned FazyRV memory-bus aligner for aligned and half-word-offset transactions.",
        "verification_command": "./scripts/verify-external-rtl.sh fazyrv && ./scripts/synth-external-rtl.sh fazyrv fazyrv_align",
    },
    {
        "id": "fazyrv-spm-a-001", "source_id": "fazyrv", "split": "train", "design_family": "fazyrv_address_serializer",
        "source_path": "rtl/fazyrv_spm_a.sv", "testbench": "tests/external/fazyrv/tb_fazyrv_spm_a.sv",
        "specification": "Implement the pinned FazyRV serial-to-parallel 32-bit address register.",
        "verification_command": "./scripts/verify-external-rtl.sh fazyrv && ./scripts/synth-external-rtl.sh fazyrv fazyrv_spm_a",
    },
    {
        "id": "fazyrv-pc-001", "source_id": "fazyrv", "split": "train", "design_family": "fazyrv_serial_program_counter",
        "source_path": "rtl/fazyrv_pc.sv", "dependencies": ("rtl/fazyrv_hadd.v",), "testbench": "tests/external/fazyrv/tb_fazyrv_pc.sv",
        "specification": "Implement the pinned FazyRV serial program counter with configurable boot address and half-adder dependency.",
        "verification_command": "./scripts/verify-external-rtl.sh fazyrv && ./scripts/synth-external-rtl.sh fazyrv fazyrv_pc",
    },
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _extract_module(source: str, module: str) -> str:
    """Keep one Verilog module rather than ingesting an unrelated monolithic file."""
    start = re.search(rf"(?m)^module\s+{re.escape(module)}(?:\s|#|\()", source)
    if start is None:
        raise ValueError(f"module not found in reviewed source: {module}")
    end = re.search(r"(?m)^endmodule\b", source[start.start() :])
    if end is None:
        raise ValueError(f"unterminated reviewed module: {module}")
    return source[start.start() : start.start() + end.end()] + "\n"


def _checked_source_root(source_id: str, root: Path) -> dict[str, str]:
    source = SOURCES[source_id]
    if not root.is_dir():
        raise ValueError(f"{source_id} checkout does not exist: {root}")
    head = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    if head != source["commit"]:
        raise ValueError(f"{source_id} checkout commit mismatch: {head}")
    if _sha256(root / source["license_path"]) != source["license_sha256"]:
        raise ValueError(f"{source_id} license checksum mismatch")
    return source


def build_external_circuit_corpus(output: Path, source_roots: dict[str, Path]) -> dict[str, Any]:
    """Write verbatim, license-preserving examples from reviewed temporary checkouts."""
    if output.exists():
        raise ValueError(f"external corpus output already exists: {output}")
    checked = {source_id: _checked_source_root(source_id, source_roots[source_id]) for source_id in SOURCES}
    records: list[dict[str, Any]] = []
    for example in EXAMPLES:
        source = checked[example["source_id"]]
        relative_paths = (*example.get("dependencies", ()), example["source_path"])
        source_paths = [source_roots[example["source_id"]] / relative_path for relative_path in relative_paths]
        testbench_path = ROOT / example["testbench"]
        if not all(path.is_file() for path in source_paths) or not testbench_path.is_file():
            raise ValueError(f"missing reviewed example input for {example['id']}")
        rtl_parts = []
        for relative_path, source_path in zip(relative_paths, source_paths, strict=True):
            source_text = source_path.read_text(encoding="utf-8")
            rtl_parts.append(_extract_module(source_text, example["module"]) if relative_path == example["source_path"] and "module" in example else source_text)
        rtl = "\n".join(rtl_parts)
        license_text = (source_roots[example["source_id"]] / source["license_path"]).read_text(encoding="utf-8")
        rtl = f"/* External source license ({source['license']}):\n{license_text.rstrip()}\n*/\n\n{rtl}"
        testbench = testbench_path.read_text(encoding="utf-8")
        records.append(
            {
                "schema_version": "1.0",
                "id": example["id"],
                "split": example["split"],
                "design_family": example["design_family"],
                "task": "specification-to-systemverilog-with-testbench",
                "input": {"specification": example["specification"], "context": "Pinned external RTL reference; preserve its license notice."},
                "target": {"systemverilog": rtl, "testbench": testbench},
                "verification": {"rtl_simulation": "passed", "synthesis": "passed", "command": example["verification_command"]},
                "provenance": {
                    "source": source["repository"],
                    "license": source["license"],
                    "reviewed": True,
                    "source_commit": source["commit"],
                    "source_paths": [*relative_paths, example["testbench"]],
                    "source_sha256": {**{relative_path: _sha256(source_path) for relative_path, source_path in zip(relative_paths, source_paths, strict=True)}, example["testbench"]: _sha256(testbench_path)},
                    "license_sha256": source["license_sha256"],
                    "dependencies": list(example.get("dependencies", ())),
                    "transformation": (
                        "verbatim selected RTL file preceded by its complete license text; EF-GPU-authored focused smoke testbench appended as separate target field"
                        if "module" not in example
                        else f"verbatim extraction of module {example['module']} from a monolithic reviewed RTL file, preceded by its complete license text; EF-GPU-authored focused smoke testbench appended as separate target field"
                    ),
                },
            }
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")
    validation = validate_circuit_dataset(output)
    benchmark = [record for record in records if record["split"] == "benchmark"]
    benchmark_bytes = "".join(json.dumps(record, sort_keys=True) + "\n" for record in benchmark).encode()
    manifest = {
        "schema_version": "1.0",
        "command": "build-external-circuit-corpus",
        "output": str(output),
        "output_sha256": _sha256(output),
        "benchmark_records": [record["id"] for record in benchmark],
        "frozen_benchmark_sha256": hashlib.sha256(benchmark_bytes).hexdigest(),
        "created_at_utc": datetime.now(UTC).isoformat(),
        "validation": validation,
        "training_status": "candidate-data-only; below Sprint 3 volume floor and no model weights trained",
    }
    output.with_suffix(output.suffix + ".manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
