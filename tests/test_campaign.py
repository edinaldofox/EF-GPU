from __future__ import annotations

import json
from pathlib import Path

from ef_gpu.campaign import run_simd4x8_campaign


ROOT = Path(__file__).resolve().parents[1]


def _git_clean(*args: str) -> str:
    return "test-commit" if args == ("rev-parse", "HEAD") else ""


def test_campaign_stops_after_the_first_valid_candidate(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("ef_gpu.campaign._git", _git_clean)
    seeds: list[int] = []

    def iterate(_request: Path, output: Path, *, model: str, seed: int) -> int:
        seeds.append(seed)
        output.mkdir()
        status = "patch-rejected" if seed == 10 else "candidate-valid"
        (output / "manifest.json").write_text(json.dumps({"status": status}) + "\n", encoding="utf-8")
        return 0 if status == "candidate-valid" else 2

    monkeypatch.setattr("ef_gpu.campaign.run_autonomous_simd4x8_iteration", iterate)
    output = tmp_path / "campaign"
    result = run_simd4x8_campaign(
        ROOT / "examples/agent/simd4x8-request.json", output, attempts=3, seed=10
    )
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert result == 0
    assert seeds == [10, 11]
    assert manifest["status"] == "campaign-valid"
    assert manifest["stop_reason"] == "first valid candidate"


def test_campaign_blocks_a_dirty_worktree(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        "ef_gpu.campaign._git",
        lambda *args: "test-commit" if args == ("rev-parse", "HEAD") else " M src/ef_gpu/campaign.py",
    )
    output = tmp_path / "campaign"
    result = run_simd4x8_campaign(
        ROOT / "examples/agent/simd4x8-request.json", output, attempts=1
    )
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert result == 2
    assert manifest["status"] == "invalid-worktree"


def test_campaign_rejects_an_unbounded_attempt_count(tmp_path) -> None:
    try:
        run_simd4x8_campaign(
            ROOT / "examples/agent/simd4x8-request.json", tmp_path / "campaign", attempts=21
        )
    except ValueError as error:
        assert "between 1 and 20" in str(error)
    else:
        raise AssertionError("unbounded campaign was accepted")
