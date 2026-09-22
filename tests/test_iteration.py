from __future__ import annotations

import json
from pathlib import Path

from ef_gpu.iteration import run_autonomous_simd4x8_iteration


ROOT = Path(__file__).resolve().parents[1]


def _git_clean(*args: str) -> str:
    return "test-commit" if args == ("rev-parse", "HEAD") else ""


def _write_proposal(_request: Path, output: Path, **_kwargs: object) -> Path:
    output.write_text(
        (ROOT / "examples/agent/simd4x8-baseline-proposal.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    output.with_suffix(".json.meta.json").write_text("{}\n", encoding="utf-8")
    return output


def _write_template_proposal(_request: Path, output: Path, **_kwargs: object) -> Path:
    proposal = json.loads(
        (ROOT / "examples/agent/simd4x8-baseline-proposal.json").read_text(encoding="utf-8")
    )
    proposal["patch_template"] = "testbench-pass-message-label"
    output.write_text(json.dumps(proposal) + "\n", encoding="utf-8")
    output.with_suffix(".json.meta.json").write_text("{}\n", encoding="utf-8")
    return output


def test_autonomous_iteration_records_a_rejected_patch(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("ef_gpu.iteration._git", _git_clean)
    monkeypatch.setattr("ef_gpu.iteration.generate_simd4x8_proposal", _write_proposal)

    def reject_patch(_proposal: Path, output: Path, **_kwargs: object) -> Path:
        output.with_suffix(".patch.meta.json").write_text("{}\n", encoding="utf-8")
        output.with_suffix(".patch.rejected.txt").write_text("bad diff\n", encoding="utf-8")
        raise RuntimeError("unsafe patch")

    monkeypatch.setattr("ef_gpu.iteration.generate_simd4x8_testbench_patch", reject_patch)
    output = tmp_path / "iteration"
    result = run_autonomous_simd4x8_iteration(
        ROOT / "examples/agent/simd4x8-request.json", output
    )
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert result == 2
    assert manifest["status"] == "patch-rejected"
    assert manifest["steps"][-1]["raw_response"] == "candidate.patch.rejected.txt"


def test_autonomous_iteration_records_a_valid_disposable_candidate(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("ef_gpu.iteration._git", _git_clean)
    monkeypatch.setattr("ef_gpu.iteration.generate_simd4x8_proposal", _write_proposal)

    def accept_patch(_proposal: Path, output: Path, **_kwargs: object) -> Path:
        output.write_text("valid diff\n", encoding="utf-8")
        output.with_suffix(".patch.meta.json").write_text("{}\n", encoding="utf-8")
        return output

    def stage_candidate(_request: Path, _proposal: Path, _patch: Path, output: Path) -> int:
        output.mkdir()
        (output / "manifest.json").write_text('{"status":"candidate-valid"}\n', encoding="utf-8")
        return 0

    monkeypatch.setattr("ef_gpu.iteration.generate_simd4x8_testbench_patch", accept_patch)
    monkeypatch.setattr("ef_gpu.iteration.stage_simd4x8_patch", stage_candidate)
    output = tmp_path / "iteration"
    result = run_autonomous_simd4x8_iteration(
        ROOT / "examples/agent/simd4x8-request.json", output
    )
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert result == 0
    assert manifest["status"] == "candidate-valid"
    assert manifest["steps"][-1]["path"] == "candidate/manifest.json"


def test_autonomous_iteration_can_compile_a_reviewed_template(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("ef_gpu.iteration._git", _git_clean)
    monkeypatch.setattr("ef_gpu.iteration.generate_simd4x8_proposal", _write_template_proposal)

    def emit_template(template_id: str, output: Path) -> Path:
        assert template_id == "testbench-pass-message-label"
        output.write_text("valid diff\n", encoding="utf-8")
        output.with_suffix(".patch.template.meta.json").write_text("{}\n", encoding="utf-8")
        return output

    def stage_candidate(_request: Path, _proposal: Path, _patch: Path, output: Path) -> int:
        output.mkdir()
        (output / "manifest.json").write_text('{"status":"candidate-valid"}\n', encoding="utf-8")
        return 0

    monkeypatch.setattr("ef_gpu.iteration.emit_simd4x8_template_patch", emit_template)
    monkeypatch.setattr("ef_gpu.iteration.stage_simd4x8_patch", stage_candidate)
    output = tmp_path / "iteration"
    result = run_autonomous_simd4x8_iteration(
        ROOT / "examples/agent/simd4x8-request.json", output, patch_source="template"
    )
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert result == 0
    assert manifest["patch_source"] == "template"
    assert manifest["steps"][1]["name"] == "02-deterministic-template"


def test_autonomous_iteration_rejects_a_dirty_worktree(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        "ef_gpu.iteration._git",
        lambda *args: "test-commit" if args == ("rev-parse", "HEAD") else " M src/ef_gpu/iteration.py",
    )
    output = tmp_path / "iteration"
    result = run_autonomous_simd4x8_iteration(
        ROOT / "examples/agent/simd4x8-request.json", output
    )
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert result == 2
    assert manifest["status"] == "invalid-request"
    assert "worktree is dirty" in manifest["error"]
