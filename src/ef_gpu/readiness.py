"""Report whether a circuit corpus meets the declared Sprint 2 data floor."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ef_gpu.circuit_data import _read_jsonl, validate_circuit_dataset


DEFAULT_MINIMUMS = {"train": 12, "validation": 4, "benchmark": 4, "families": 20}


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
