from __future__ import annotations

from pathlib import Path

from ef_gpu.staging import _patch_paths


ROOT = Path(__file__).resolve().parents[1]


def test_example_candidate_patch_has_only_the_allowed_path() -> None:
    patch = ROOT / "examples/agent/patches/simd4x8-testbench-message.patch"
    assert _patch_paths(patch) == {"designs/simd4x8/tb/tb_simd4x8_c_ref.sv"}
