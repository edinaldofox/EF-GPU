from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ef_gpu.readiness import sprint3_corpus_readiness


def _record(index: int, split: str) -> dict[str, object]:
    return {
        "id": f"{split}-{index}",
        "split": split,
        "design_family": f"{split}-family-{index}",
        "task": "specification-to-systemverilog",
        "input": {"specification": "Implement a reviewed module."},
        "target": {"systemverilog": f"module {split}_{index}; endmodule"},
        "verification": {"rtl_simulation": "passed", "synthesis": "passed"},
        "provenance": {
            "source": "reviewed fixture",
            "license": "MIT",
            "reviewed": True,
            "source_sha256": {f"{split}-{index}.sv": hashlib.sha256(f"{split}-{index}".encode()).hexdigest()},
        },
    }


def test_sprint3_readiness_requires_exact_frozen_benchmark(tmp_path: Path) -> None:
    records = [*(_record(index, "train") for index in range(100)), *(_record(index, "validation") for index in range(20)), *(_record(index, "benchmark") for index in range(20))]
    corpus = tmp_path / "corpus.jsonl"
    corpus.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")
    benchmark = [record for record in records if record["split"] == "benchmark"]
    digest = hashlib.sha256("".join(json.dumps(record, sort_keys=True) + "\n" for record in benchmark).encode()).hexdigest()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"benchmark_records": [record["id"] for record in benchmark], "frozen_benchmark_sha256": digest}), encoding="utf-8")

    assert sprint3_corpus_readiness(corpus, manifest)["ready_for_training"] is True
    manifest.write_text(json.dumps({"benchmark_records": [], "frozen_benchmark_sha256": digest}), encoding="utf-8")
    assert sprint3_corpus_readiness(corpus, manifest)["benchmark_frozen"] is False
