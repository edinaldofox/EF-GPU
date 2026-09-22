from __future__ import annotations

import json

from ef_gpu.circuit_data import export_circuit_sft, validate_circuit_dataset


def _record(identifier: str, split: str, family: str) -> dict[str, object]:
    return {
        "id": identifier,
        "split": split,
        "design_family": family,
        "task": "spec-to-systemverilog",
        "input": {"specification": "Implement a two-input AND gate."},
        "target": {"systemverilog": "module and2(input logic a, b, output logic y); assign y = a & b; endmodule"},
        "verification": {"rtl_simulation": "passed", "synthesis": "passed"},
        "provenance": {"source": "EF-GPU", "license": "Apache-2.0", "reviewed": True},
    }


def test_export_excludes_frozen_benchmark(tmp_path) -> None:
    source = tmp_path / "circuit.jsonl"
    source.write_text(
        "".join(
            json.dumps(record) + "\n"
            for record in (_record("train-and2", "train", "and2"), _record("bench-xor2", "benchmark", "xor2"))
        ),
        encoding="utf-8",
    )
    output = tmp_path / "sft.jsonl"
    summary = export_circuit_sft(source, output)
    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert summary["examples_exported"] == 1
    assert summary["benchmark_examples_excluded"] == 1
    assert rows[0]["metadata"]["id"] == "train-and2"


def test_validation_rejects_family_leakage(tmp_path) -> None:
    source = tmp_path / "leak.jsonl"
    source.write_text(
        json.dumps(_record("train-and2", "train", "and2"))
        + "\n"
        + json.dumps(_record("validation-and2", "validation", "and2"))
        + "\n",
        encoding="utf-8",
    )
    try:
        validate_circuit_dataset(source)
    except ValueError as error:
        assert "leaks across" in str(error)
    else:
        raise AssertionError("family leakage was accepted")
