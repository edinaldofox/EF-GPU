"""Report whether a circuit corpus meets the declared Sprint 2 data floor."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Any

from ef_gpu.circuit_data import _read_jsonl, validate_circuit_dataset


DEFAULT_MINIMUMS = {"train": 12, "validation": 4, "benchmark": 4, "families": 20}
SPRINT3_MINIMUMS = {"train": 100, "validation": 20, "benchmark": 20}


def circuit_corpus_readiness(path: Path) -> dict[str, Any]:
    validation = validate_circuit_dataset(path)
    records = _read_jsonl(path)
    tasks: dict[str, int] = {}
    licenses: dict[str, int] = {}
    for record in records:
        tasks[record["task"]] = tasks.get(record["task"], 0) + 1
        license_id = record["provenance"]["license"]
        licenses[license_id] = licenses.get(license_id, 0) + 1
    gaps = {key: max(0, DEFAULT_MINIMUMS[key] - (validation["families"] if key == "families" else validation["splits"][key])) for key in DEFAULT_MINIMUMS}
    return {"schema_version": "1.0", "corpus": str(path), "validation": validation, "tasks": tasks, "licenses": licenses, "minimums": DEFAULT_MINIMUMS, "gaps": gaps, "ready_for_training": not any(gaps.values())}


def write_circuit_corpus_readiness(path: Path, output: Path) -> dict[str, Any]:
    if output.exists():
        raise ValueError(f"readiness output already exists: {output}")
    report = circuit_corpus_readiness(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def sprint3_corpus_readiness(path: Path, manifest_path: Path) -> dict[str, Any]:
    """Check the higher Sprint 3 volume floor and frozen benchmark digest."""
    validation = validate_circuit_dataset(path)
    records = _read_jsonl(path)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid Sprint 3 benchmark manifest: {error}") from error
    benchmark = [record for record in records if record["split"] == "benchmark"]
    expected = manifest.get("frozen_benchmark_sha256")
    actual = hashlib.sha256("".join(json.dumps(record, sort_keys=True) + "\n" for record in benchmark).encode()).hexdigest()
    benchmark_ids = [record["id"] for record in benchmark]
    manifest_ids = manifest.get("benchmark_records")
    benchmark_frozen = isinstance(expected, str) and expected == actual and manifest_ids == benchmark_ids
    gaps = {split: max(0, required - validation["splits"][split]) for split, required in SPRINT3_MINIMUMS.items()}
    return {
        "schema_version": "1.0",
        "corpus": str(path),
        "benchmark_manifest": str(manifest_path),
        "validation": validation,
        "minimums": SPRINT3_MINIMUMS,
        "gaps": gaps,
        "benchmark_frozen": benchmark_frozen,
        "frozen_benchmark_sha256": actual,
        "ready_for_training": benchmark_frozen and not any(gaps.values()),
        "training_status": "readiness-only; separate approval is required before any weight training",
    }


def write_sprint3_corpus_readiness(path: Path, manifest_path: Path, output: Path) -> dict[str, Any]:
    if output.exists():
        raise ValueError(f"Sprint 3 readiness output already exists: {output}")
    report = sprint3_corpus_readiness(path, manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
