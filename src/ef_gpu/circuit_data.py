"""Validate reviewed circuit examples and export a narrow SFT dataset.

This module deliberately prepares data only. It never downloads, trains, or
publishes model weights.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


SPLITS = {"train", "validation", "benchmark"}
REQUIRED_VERIFICATION = {"rtl_simulation", "synthesis"}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise ValueError(f"circuit dataset does not exist: {path}")
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSONL at line {line_number}: {error}") from error
        if not isinstance(record, dict):
            raise ValueError(f"dataset line {line_number} must be an object")
        records.append(record)
    if not records:
        raise ValueError("circuit dataset contains no records")
    return records


def validate_circuit_dataset(path: Path) -> dict[str, Any]:
    """Return a summary or raise ValueError for unsafe/unusable training data."""
    records = _read_jsonl(path)
    identifiers: set[str] = set()
    family_splits: dict[str, str] = {}
    source_hash_splits: dict[str, str] = {}
    split_counts = {split: 0 for split in SPLITS}

    for index, record in enumerate(records, start=1):
        identifier = record.get("id")
        split = record.get("split")
        family = record.get("design_family")
        task = record.get("task")
        input_data = record.get("input")
        target = record.get("target")
        verification = record.get("verification")
        provenance = record.get("provenance")
        if not isinstance(identifier, str) or not identifier:
            raise ValueError(f"record {index}: id must be a non-empty string")
        if identifier in identifiers:
            raise ValueError(f"record {index}: duplicate id {identifier}")
        identifiers.add(identifier)
        if split not in SPLITS:
            raise ValueError(f"record {index}: split must be one of {sorted(SPLITS)}")
        if not isinstance(family, str) or not family:
            raise ValueError(f"record {index}: design_family must be a non-empty string")
        previous_split = family_splits.setdefault(family, split)
        if previous_split != split:
            raise ValueError(f"record {index}: design family {family} leaks across {previous_split}/{split}")
        if not isinstance(task, str) or not task:
            raise ValueError(f"record {index}: task must be a non-empty string")
        if not isinstance(input_data, dict) or not isinstance(input_data.get("specification"), str) or not input_data["specification"]:
            raise ValueError(f"record {index}: input.specification must be a non-empty string")
        if not isinstance(target, dict) or not isinstance(target.get("systemverilog"), str) or not target["systemverilog"]:
            raise ValueError(f"record {index}: target.systemverilog must be a non-empty string")
        if not isinstance(verification, dict) or any(
            verification.get(gate) != "passed" for gate in REQUIRED_VERIFICATION
        ):
            raise ValueError(f"record {index}: RTL simulation and synthesis must both be passed")
        if not isinstance(provenance, dict) or not isinstance(provenance.get("license"), str) or not provenance["license"]:
            raise ValueError(f"record {index}: provenance.license must be a non-empty string")
        if not isinstance(provenance.get("source"), str) or not provenance["source"]:
            raise ValueError(f"record {index}: provenance.source must be a non-empty string")
        if provenance.get("reviewed") is not True:
            raise ValueError(f"record {index}: provenance.reviewed must be true")
        source_hashes = provenance.get("source_sha256")
        if source_hashes is not None:
            if not isinstance(source_hashes, dict) or not all(isinstance(value, str) and value for value in source_hashes.values()):
                raise ValueError(f"record {index}: provenance.source_sha256 must map paths to non-empty hashes")
            for source_hash in source_hashes.values():
                previous_source_split = source_hash_splits.setdefault(source_hash, split)
                if previous_source_split != split:
                    raise ValueError(f"record {index}: source content leaks across {previous_source_split}/{split}")
        split_counts[split] += 1

    return {
        "schema_version": "1.0",
        "records": len(records),
        "splits": split_counts,
        "families": len(family_splits),
        "training_status": "validated-data-only; no model weights trained",
    }


def export_circuit_sft(source: Path, output: Path) -> dict[str, Any]:
    """Export train/validation examples in chat JSONL; exclude frozen benchmarks."""
    if output.exists():
        raise ValueError(f"SFT output already exists: {output}")
    summary = validate_circuit_dataset(source)
    records = _read_jsonl(source)
    exported: list[dict[str, Any]] = []
    for record in records:
        if record["split"] == "benchmark":
            continue
        context = record["input"].get("context", "")
        user = f"Task: {record['task']}\nSpecification:\n{record['input']['specification']}"
        if context:
            user += f"\nContext:\n{context}"
        assistant = record["target"]["systemverilog"]
        testbench = record["target"].get("testbench")
        if isinstance(testbench, str) and testbench:
            assistant += f"\n\nTestbench:\n{testbench}"
        exported.append(
            {
                "messages": [
                    {"role": "system", "content": "Generate SystemVerilog only when the specification is complete."},
                    {"role": "user", "content": user},
                    {"role": "assistant", "content": assistant},
                ],
                "metadata": {
                    "id": record["id"],
                    "split": record["split"],
                    "design_family": record["design_family"],
                    "license": record["provenance"]["license"],
                },
            }
        )
    if not exported:
        raise ValueError("dataset has no train or validation examples to export")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in exported), encoding="utf-8")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    return {
        **summary,
        "output": str(output),
        "examples_exported": len(exported),
        "benchmark_examples_excluded": summary["splits"]["benchmark"],
        "output_sha256": digest,
        "training_status": "SFT-ready-data-only; LoRA training requires separate approval",
    }
