from __future__ import annotations

from ef_gpu.llm import build_simd4x8_proposal, validate_simd4x8_plan


def test_plan_is_wrapped_in_a_complete_proposal(monkeypatch) -> None:
    monkeypatch.setattr("ef_gpu.llm._git_head", lambda: "0123456789abcdef")
    proposal = build_simd4x8_proposal(
        {"design_id": "simd4x8-vmac"},
        {
            "changes": ["Tighten a condition in designs/simd4x8/rtl/mult8_iter.sv."],
            "assumptions": ["Unsigned lanes."],
            "target_files": ["designs/simd4x8/rtl/mult8_iter.sv"],
            "preserves_interface": True,
            "validation": "Run the C-reference RTL regression.",
        },
        model="test-model",
        model_digest="test-digest",
        seed=7,
    )
    assert proposal["design_id"] == "simd4x8-vmac"
    assert proposal["model"]["revision"] == "test-digest"
    assert proposal["artifacts"]["rtl"]


def test_interface_changing_plan_is_rejected() -> None:
    errors = validate_simd4x8_plan(
        {
            "changes": ["Add a new input port to the VMAC."],
            "assumptions": [],
            "target_files": ["designs/simd4x8/rtl/simd4x8_mac_comb_top.sv"],
            "preserves_interface": True,
            "validation": "Run the C-reference RTL regression.",
        }
    )
    assert "changes imply an interface modification" in errors
