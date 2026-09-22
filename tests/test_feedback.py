from __future__ import annotations

import json
from pathlib import Path

from ef_gpu.feedback import collect_patch_feedback


def _metadata(artifact: Path, response_hash: str) -> dict[str, object]:
    return {
        "status": "rejected",
        "reason": "invalid diff",
        "git_commit": "test-commit",
        "model": {"id": "qwen2.5-coder:3b-instruct", "revision": "test", "seed": 42},
        "inputs": {"prompt": "generate a patch", "prompt_sha256": "prompt", "target_path": "tb.sv"},
        "response": {"sha256": response_hash},
        "validation": {"git_apply_check_passed": False},
        "artifact_path": str(artifact),
    }


def test_feedback_collection_deduplicates_response_hashes(tmp_path) -> None:
    artifact = tmp_path / "raw.patch"
    artifact.write_text("bad diff\n", encoding="utf-8")
    for name in ("first.patch.meta.json", "second.patch.meta.json"):
        (tmp_path / name).write_text(
            json.dumps(_metadata(artifact, "same-response")) + "\n", encoding="utf-8"
        )
    output = tmp_path / "feedback.jsonl"
    summary = collect_patch_feedback([tmp_path], output)
    records = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert summary["records_written"] == 1
    assert summary["duplicate_responses_skipped"] == 1
    assert records[0]["output"]["patch_text"] == "bad diff\n"
    assert "non-commercial" in records[0]["provenance"]["model_license"]


def test_feedback_collection_refuses_to_overwrite(tmp_path) -> None:
    output = tmp_path / "feedback.jsonl"
    output.write_text("existing\n", encoding="utf-8")
    try:
        collect_patch_feedback([tmp_path], output)
    except ValueError as error:
        assert "already exists" in str(error)
    else:
        raise AssertionError("existing feedback dataset was overwritten")
