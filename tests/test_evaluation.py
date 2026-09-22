from __future__ import annotations

import json
from pathlib import Path

from ef_gpu.evaluation import evaluate_patch_models


ROOT = Path(__file__).resolve().parents[1]


def test_evaluation_records_pinned_models_and_rejections(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("ef_gpu.evaluation.model_revision", lambda model: "revision-" + model)
    monkeypatch.setattr("ef_gpu.evaluation.MODEL_REVISIONS", {"model-a": "revision-a", "model-b": "revision-b"})

    def reject(_proposal: Path, output: Path, *, model: str, seed: int) -> Path:
        output.with_suffix(".patch.meta.json").write_text(
            json.dumps({"status": "rejected", "reason": model, "response": {"sha256": model}}) + "\n",
            encoding="utf-8",
        )
        raise RuntimeError("rejected")

    monkeypatch.setattr("ef_gpu.evaluation.generate_simd4x8_testbench_patch", reject)
    output = tmp_path / "evaluation"
    result = evaluate_patch_models(
        ROOT / "examples/agent/simd4x8-baseline-proposal.json",
        output,
        models=["model-a", "model-b"],
        seed=7,
    )
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert result == 1
    assert manifest["accepted_count"] == 0
    assert [item["model"] for item in manifest["results"]] == ["model-a", "model-b"]


def test_evaluation_rejects_duplicate_model_names(tmp_path) -> None:
    try:
        evaluate_patch_models(
            ROOT / "examples/agent/simd4x8-baseline-proposal.json",
            tmp_path / "evaluation",
            models=["qwen2.5-coder:1.5b-instruct", "qwen2.5-coder:1.5b-instruct"],
            seed=42,
        )
    except ValueError as error:
        assert "unique" in str(error)
    else:
        raise AssertionError("duplicate model names were accepted")
