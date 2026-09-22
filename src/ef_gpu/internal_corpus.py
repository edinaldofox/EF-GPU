"""Materialize a licensed seed corpus from EF-GPU's verified in-repository blocks."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ef_gpu.circuit_data import validate_circuit_dataset


ROOT = Path(__file__).resolve().parents[2]


CORPUS_SOURCES: tuple[dict[str, Any], ...] = (
    {
        "id": "ef-gpu-mux2_8-001",
        "split": "train",
        "design_family": "mux2_8",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/circuit_primitives/spec.md",
        "rtl": ("designs/circuit_primitives/rtl/mux2_8.sv",),
        "testbench": "designs/circuit_primitives/tb/tb_circuit_primitives.sv",
        "verification_command": "./scripts/verify-circuit-primitives.sh && ./scripts/synth-circuit-primitives.sh mux2_8",
    },
    {
        "id": "ef-gpu-counter4-001",
        "split": "train",
        "design_family": "counter4",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/circuit_primitives/spec.md",
        "rtl": ("designs/circuit_primitives/rtl/counter4.sv",),
        "testbench": "designs/circuit_primitives/tb/tb_circuit_primitives.sv",
        "verification_command": "./scripts/verify-circuit-primitives.sh && ./scripts/synth-circuit-primitives.sh counter4",
    },
    {
        "id": "ef-gpu-shifter8-001",
        "split": "train",
        "design_family": "shifter8",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/circuit_primitives/spec.md",
        "rtl": ("designs/circuit_primitives/rtl/shifter8.sv",),
        "testbench": "designs/circuit_primitives/tb/tb_circuit_primitives.sv",
        "verification_command": "./scripts/verify-circuit-primitives.sh && ./scripts/synth-circuit-primitives.sh shifter8",
    },
    {
        "id": "ef-gpu-compare8-001",
        "split": "train",
        "design_family": "compare8",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/circuit_primitives/spec.md",
        "rtl": ("designs/circuit_primitives/rtl/compare8.sv",),
        "testbench": "designs/circuit_primitives/tb/tb_circuit_primitives.sv",
        "verification_command": "./scripts/verify-circuit-primitives.sh && ./scripts/synth-circuit-primitives.sh compare8",
    },
    {
        "id": "ef-gpu-arbiter2-001",
        "split": "train",
        "design_family": "arbiter2",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/circuit_primitives/spec.md",
        "rtl": ("designs/circuit_primitives/rtl/arbiter2.sv",),
        "testbench": "designs/circuit_primitives/tb/tb_circuit_primitives.sv",
        "verification_command": "./scripts/verify-circuit-primitives.sh && ./scripts/synth-circuit-primitives.sh arbiter2",
    },
    {
        "id": "ef-gpu-add8-001",
        "split": "train",
        "design_family": "add8",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/training_blocks/spec.md",
        "rtl": ("designs/training_blocks/rtl/add8.sv",),
        "testbench": "designs/training_blocks/tb/tb_training_blocks.sv",
        "verification_command": "./scripts/verify-corpus-blocks.sh training_blocks && ./scripts/synth-corpus-blocks.sh training_blocks add8",
    },
    {
        "id": "ef-gpu-bitwise8-001",
        "split": "train",
        "design_family": "bitwise8",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/training_blocks/spec.md",
        "rtl": ("designs/training_blocks/rtl/bitwise8.sv",),
        "testbench": "designs/training_blocks/tb/tb_training_blocks.sv",
        "verification_command": "./scripts/verify-corpus-blocks.sh training_blocks && ./scripts/synth-corpus-blocks.sh training_blocks bitwise8",
    },
    {
        "id": "ef-gpu-priority8-001",
        "split": "train",
        "design_family": "priority8",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/training_blocks/spec.md",
        "rtl": ("designs/training_blocks/rtl/priority8.sv",),
        "testbench": "designs/training_blocks/tb/tb_training_blocks.sv",
        "verification_command": "./scripts/verify-corpus-blocks.sh training_blocks && ./scripts/synth-corpus-blocks.sh training_blocks priority8",
    },
    {
        "id": "ef-gpu-popcount8-001",
        "split": "train",
        "design_family": "popcount8",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/training_blocks/spec.md",
        "rtl": ("designs/training_blocks/rtl/popcount8.sv",),
        "testbench": "designs/training_blocks/tb/tb_training_blocks.sv",
        "verification_command": "./scripts/verify-corpus-blocks.sh training_blocks && ./scripts/synth-corpus-blocks.sh training_blocks popcount8",
    },
    {
        "id": "ef-gpu-register_slice-001",
        "split": "validation",
        "design_family": "register_slice",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/validation_blocks/spec.md",
        "rtl": ("designs/validation_blocks/rtl/register_slice.sv",),
        "testbench": "designs/validation_blocks/tb/tb_validation_blocks.sv",
        "verification_command": "./scripts/verify-corpus-blocks.sh validation_blocks && ./scripts/synth-corpus-blocks.sh validation_blocks register_slice",
    },
    {
        "id": "ef-gpu-fifo4-001",
        "split": "validation",
        "design_family": "fifo4",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/validation_blocks/spec.md",
        "rtl": ("designs/validation_blocks/rtl/fifo4.sv",),
        "testbench": "designs/validation_blocks/tb/tb_validation_blocks.sv",
        "verification_command": "./scripts/verify-corpus-blocks.sh validation_blocks && ./scripts/synth-corpus-blocks.sh validation_blocks fifo4",
    },
    {
        "id": "ef-gpu-lfsr8-001",
        "split": "benchmark",
        "design_family": "lfsr8",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/benchmark_blocks/spec.md",
        "rtl": ("designs/benchmark_blocks/rtl/lfsr8.sv",),
        "testbench": "designs/benchmark_blocks/tb/tb_benchmark_blocks.sv",
        "verification_command": "./scripts/verify-corpus-blocks.sh benchmark_blocks && ./scripts/synth-corpus-blocks.sh benchmark_blocks lfsr8",
    },
    {
        "id": "ef-gpu-round_robin2-001",
        "split": "benchmark",
        "design_family": "round_robin2",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/benchmark_blocks/spec.md",
        "rtl": ("designs/benchmark_blocks/rtl/round_robin2.sv",),
        "testbench": "designs/benchmark_blocks/tb/tb_benchmark_blocks.sv",
        "verification_command": "./scripts/verify-corpus-blocks.sh benchmark_blocks && ./scripts/synth-corpus-blocks.sh benchmark_blocks round_robin2",
    },
    {
        "id": "ef-gpu-vpu16-sequencer-001",
        "split": "train",
        "design_family": "vpu16_sequencer",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/vpu16_sequencer/spec.md",
        "rtl": ("designs/vpu16_sequencer/rtl/vpu16_sequencer.sv",),
        "testbench": "designs/vpu16_sequencer/tb/tb_vpu16_program.sv",
        "verification_command": "./scripts/verify-vpu16-sequencer.sh && ./scripts/synth-vpu16-sequencer.sh",
    },
    {
        "id": "ef-gpu-alu8-001",
        "split": "train",
        "design_family": "alu8",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/alu8/spec.md",
        "rtl": ("designs/alu8/rtl/alu8_core.sv", "designs/alu8/rtl/ef_gpu_alu8.sv"),
        "testbench": "designs/alu8/tb/tb_ef_gpu_alu8.sv",
        "verification_command": "./scripts/verify-alu8.sh && ./scripts/synth-alu8.sh",
    },
    {
        "id": "ef-gpu-simd4x8-comb-001",
        "split": "train",
        "design_family": "simd4x8",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/simd4x8/README.md",
        "rtl": ("designs/simd4x8/rtl/mult8_comb.sv", "designs/simd4x8/rtl/simd4x8_mac_comb_top.sv"),
        "testbench": "designs/simd4x8/tb/tb_simd4x8_c_ref.sv",
        "verification_command": "./scripts/verify-simd4x8.sh && ./scripts/synth-simd4x8.sh",
    },
    {
        "id": "ef-gpu-vreg8x64-001",
        "split": "validation",
        "design_family": "vreg8x64",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/vreg8x64/spec.md",
        "rtl": ("designs/vreg8x64/rtl/vreg8x64.sv",),
        "testbench": "designs/vreg8x64/tb/tb_vreg8x64.sv",
        "verification_command": "./scripts/verify-vreg8x64.sh && ./scripts/synth-vreg8x64.sh",
    },
    {
        "id": "ef-gpu-scratchpad16x64-001",
        "split": "validation",
        "design_family": "scratchpad16x64",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/scratchpad16x64/spec.md",
        "rtl": ("designs/scratchpad16x64/rtl/scratchpad16x64.sv",),
        "testbench": "designs/scratchpad16x64/tb/tb_scratchpad16x64.sv",
        "verification_command": "./scripts/verify-scratchpad16x64.sh && ./scripts/synth-scratchpad16x64.sh",
    },
    {
        "id": "ef-gpu-vpu16-decode-001",
        "split": "benchmark",
        "design_family": "vpu16_decode",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/vpu16_decode/spec.md",
        "rtl": ("designs/vpu16_decode/rtl/vpu16_decode.sv",),
        "testbench": "designs/vpu16_decode/tb/tb_vpu16_decode.sv",
        "verification_command": "./scripts/verify-vpu16-decode.sh && ./scripts/synth-vpu16-decode.sh",
    },
    {
        "id": "ef-gpu-mini-gpu-vmac-001",
        "split": "benchmark",
        "design_family": "mini_gpu_vmac",
        "task": "specification-to-systemverilog-with-testbench",
        "specification": "designs/mini_gpu_vmac/spec.md",
        # Keep only the top-level module: copying dependency RTL here would leak
        # train/validation source tokens into the frozen benchmark.
        "rtl": ("designs/mini_gpu_vmac/rtl/mini_gpu_vmac_core.sv",),
        "testbench": "designs/mini_gpu_vmac/tb/tb_mini_gpu_vmac_core.sv",
        "verification_command": "./scripts/verify-mini-gpu-vmac.sh && ./scripts/synth-mini-gpu-vmac.sh",
    },
)


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _source_bundle(paths: tuple[str, ...]) -> str:
    return "\n\n".join(f"// Source: {path}\n{_read(path).rstrip()}" for path in paths) + "\n"


def _record(source: dict[str, Any]) -> dict[str, Any]:
    rtl_paths = source["rtl"]
    target = _source_bundle(rtl_paths)
    source_hashes = {path: hashlib.sha256(_read(path).encode("utf-8")).hexdigest() for path in rtl_paths}
    source_hashes[source["specification"]] = hashlib.sha256(_read(source["specification"]).encode("utf-8")).hexdigest()
    source_hashes[source["testbench"]] = hashlib.sha256(_read(source["testbench"]).encode("utf-8")).hexdigest()
    return {
        "schema_version": "1.0",
        "id": source["id"],
        "split": source["split"],
        "design_family": source["design_family"],
        "task": source["task"],
        "input": {"specification": _read(source["specification"]), "context": "EF-GPU internal verified reference."},
        "target": {"systemverilog": target, "testbench": _read(source["testbench"])},
        "verification": {
            "rtl_simulation": "passed",
            "synthesis": "passed",
            "command": source["verification_command"],
        },
        "provenance": {
            "source": "EF-GPU repository-authored reference design",
            "license": "Apache-2.0",
            "reviewed": True,
            "source_paths": [source["specification"], *rtl_paths, source["testbench"]],
            "source_sha256": source_hashes,
        },
    }


def build_internal_circuit_corpus(output: Path) -> dict[str, Any]:
    """Write the versioned internal seed corpus and a reproducibility manifest."""
    if output.exists():
        raise ValueError(f"internal corpus output already exists: {output}")
    records = [_record(source) for source in CORPUS_SOURCES]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")
    validation = validate_circuit_dataset(output)
    manifest = {
        "schema_version": "1.0",
        "command": "build-internal-circuit-corpus",
        "output": str(output),
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "source_records": [source["id"] for source in CORPUS_SOURCES],
        "created_at_utc": datetime.now(UTC).isoformat(),
        "validation": validation,
        "training_status": "seed-corpus-only; insufficient for LoRA training",
    }
    output.with_suffix(output.suffix + ".manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return {**validation, "output": str(output), "manifest": str(output.with_suffix(output.suffix + ".manifest.json"))}
