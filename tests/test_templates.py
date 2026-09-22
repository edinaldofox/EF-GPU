from __future__ import annotations

import json
import subprocess
from pathlib import Path

from ef_gpu.templates import (
    ROOT,
    TEMPLATE_IDS,
    emit_simd4x8_template_patch,
    render_simd4x8_template_patch,
)


def test_known_template_renders_an_applicable_single_file_patch(tmp_path) -> None:
    patch = render_simd4x8_template_patch("testbench-pass-message-label")
    path = tmp_path / "candidate.patch"
    path.write_text(patch, encoding="utf-8")
    checked = subprocess.run(
        ["git", "apply", "--check", str(path)], cwd=ROOT, text=True, stderr=subprocess.PIPE, check=False
    )
    assert checked.returncode == 0, checked.stderr
    assert "designs/simd4x8/tb/tb_simd4x8_c_ref.sv" in patch
    assert "candidate C-reference RTL test passed" in patch
    assert TEMPLATE_IDS == {"testbench-pass-message-label"}


def test_emit_records_template_provenance_and_does_not_overwrite(tmp_path) -> None:
    output = tmp_path / "candidate.patch"
    assert emit_simd4x8_template_patch("testbench-pass-message-label", output) == output
    metadata = json.loads(output.with_suffix(".patch.template.meta.json").read_text(encoding="utf-8"))
    assert metadata["source"] == "deterministic-template"
    assert metadata["template"]["id"] == "testbench-pass-message-label"
    try:
        emit_simd4x8_template_patch("testbench-pass-message-label", output)
    except ValueError as error:
        assert "overwrite" in str(error)
    else:
        raise AssertionError("existing generated patch was overwritten")


def test_unknown_template_is_rejected() -> None:
    try:
        render_simd4x8_template_patch("not-reviewed")
    except ValueError as error:
        assert "unknown template" in str(error)
    else:
        raise AssertionError("unknown template was accepted")
