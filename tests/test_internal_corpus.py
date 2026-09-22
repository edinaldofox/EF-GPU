from __future__ import annotations

import json

from ef_gpu.circuit_data import export_circuit_sft
from ef_gpu.internal_corpus import build_internal_circuit_corpus


def test_internal_corpus_has_frozen_benchmarks_and_exports_train_validation(tmp_path) -> None:
    corpus = tmp_path / "internal.jsonl"
    summary = build_internal_circuit_corpus(corpus)
    records = [json.loads(line) for line in corpus.read_text(encoding="utf-8").splitlines()]
    assert summary["records"] == 20
    assert {record["split"] for record in records} == {"train", "validation", "benchmark"}
    assert all(record["provenance"]["license"] == "Apache-2.0" for record in records)
    assert (tmp_path / "internal.jsonl.manifest.json").is_file()
    hashes_by_split = {
        split: {value for record in records if record["split"] == split for value in record["provenance"]["source_sha256"].values()}
        for split in ("train", "validation", "benchmark")
    }
    assert not hashes_by_split["train"] & hashes_by_split["validation"]
    assert not hashes_by_split["train"] & hashes_by_split["benchmark"]
    assert not hashes_by_split["validation"] & hashes_by_split["benchmark"]

    sft = tmp_path / "internal-sft.jsonl"
    sft_summary = export_circuit_sft(corpus, sft)
    assert sft_summary["examples_exported"] == 16
    assert sft_summary["benchmark_examples_excluded"] == 4
