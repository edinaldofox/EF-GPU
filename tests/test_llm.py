from __future__ import annotations

import json
from pathlib import Path

from ef_gpu.llm import (
    _is_exact_testbench_message_patch,
    build_simd4x8_proposal,
    generate_simd4x8_testbench_patch,
    model_revision,
    validate_simd4x8_plan,
)


ROOT = Path(__file__).resolve().parents[1]
VALID_MESSAGE_PATCH = (
    ROOT / "examples/agent/patches/simd4x8-testbench-message.patch"
).read_text(encoding="utf-8")
UNREQUESTED_PATCH = """diff --git a/designs/simd4x8/tb/tb_simd4x8_c_ref.sv b/designs/simd4x8/tb/tb_simd4x8_c_ref.sv
index 1234567..89abcdef 100644
--- a/designs/simd4x8/tb/tb_simd4x8_c_ref.sv
+++ b/designs/simd4x8/tb/tb_simd4x8_c_ref.sv
@@ -23,7 +23,7 @@ module tb_simd4x8_c_ref;
     logic [63:0] acc = '0;
     logic comb_busy, comb_done, iter_busy, iter_done;
     logic [63:0] comb_result, iter_result;
-    logic [63:0] expected;
+    logic [63:0] expected, candidate_expected;
     integer vector_file;
     integer scan_status;
     integer vector_count;
"""


def test_supported_model_revisions_are_pinned() -> None:
    assert model_revision("qwen2.5-coder:1.5b-instruct").startswith("d7372fd8")
    assert model_revision("qwen2.5-coder:3b-instruct").startswith("4a188102")
    try:
        model_revision("untracked-model")
    except ValueError as error:
        assert "unsupported model" in str(error)
    else:
        raise AssertionError("untracked model was accepted")


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
            "patch_template": "testbench-pass-message-label",
        },
        model="test-model",
        model_digest="test-digest",
        seed=7,
    )
    assert proposal["design_id"] == "simd4x8-vmac"
    assert proposal["model"]["revision"] == "test-digest"
    assert proposal["artifacts"]["rtl"]
    assert proposal["changes"] == [
        "Apply reviewed deterministic template testbench-pass-message-label: "
        "Labels the existing SIMD4x8 passing-test message as a candidate run."
    ]
    assert proposal["assumptions"] == [
        "Only the reviewed deterministic template is compiled; no model-authored RTL is used.",
        "Public interfaces, clock/reset behavior, constraints, and physical configuration are unchanged.",
    ]


def test_interface_changing_plan_is_rejected() -> None:
    errors = validate_simd4x8_plan(
        {
            "changes": ["Add a new input port to the VMAC."],
            "assumptions": [],
            "target_files": ["designs/simd4x8/rtl/simd4x8_mac_comb_top.sv"],
            "preserves_interface": True,
            "validation": "Run the C-reference RTL regression.",
            "patch_template": "testbench-pass-message-label",
        }
    )
    assert "changes imply an interface modification" in errors


def test_plan_with_an_unknown_template_is_rejected() -> None:
    errors = validate_simd4x8_plan(
        {
            "changes": ["Improve the testbench message."],
            "assumptions": [],
            "target_files": ["designs/simd4x8/tb/tb_simd4x8_c_ref.sv"],
            "preserves_interface": True,
            "validation": "Run the C-reference RTL regression.",
            "patch_template": "unreviewed-template",
        }
    )
    assert any(error.startswith("patch_template must be one of:") for error in errors)


def test_exact_testbench_patch_accepts_only_the_requested_replacement() -> None:
    patch = """diff --git a/designs/simd4x8/tb/tb_simd4x8_c_ref.sv b/designs/simd4x8/tb/tb_simd4x8_c_ref.sv
--- a/designs/simd4x8/tb/tb_simd4x8_c_ref.sv
+++ b/designs/simd4x8/tb/tb_simd4x8_c_ref.sv
@@ -65,1 +65,1 @@
-        $display(\"SIMD4x8 C-reference RTL test passed: %0d vectors\", vector_count);
+        $display(\"SIMD4x8 candidate C-reference RTL test passed: %0d vectors\", vector_count);
"""
    assert _is_exact_testbench_message_patch(patch)


def test_exact_testbench_patch_rejects_an_extra_change() -> None:
    patch = """diff --git a/designs/simd4x8/tb/tb_simd4x8_c_ref.sv b/designs/simd4x8/tb/tb_simd4x8_c_ref.sv
--- a/designs/simd4x8/tb/tb_simd4x8_c_ref.sv
+++ b/designs/simd4x8/tb/tb_simd4x8_c_ref.sv
@@ -11,1 +11,1 @@
-    logic [63:0] expected;
+    logic [63:0] expected, candidate_expected;
@@ -65,1 +65,1 @@
-        $display(\"SIMD4x8 C-reference RTL test passed: %0d vectors\", vector_count);
+        $display(\"SIMD4x8 candidate C-reference RTL test passed: %0d vectors\", vector_count);
"""
    assert not _is_exact_testbench_message_patch(patch)


def test_patch_generation_accepts_only_the_exact_patch(monkeypatch, tmp_path) -> None:
    proposal_path = tmp_path / "proposal.json"
    proposal_path.write_text(
        (ROOT / "examples/agent/simd4x8-baseline-proposal.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    requests = []

    def response(_endpoint, payload):
        requests.append(payload)
        return {"message": {"content": json.dumps({"patch": VALID_MESSAGE_PATCH})}}

    monkeypatch.setattr("ef_gpu.llm._post_json", response)
    output = tmp_path / "candidate.patch"
    assert generate_simd4x8_testbench_patch(
        proposal_path, output, model="qwen2.5-coder:3b-instruct"
    ) == output
    assert output.read_text(encoding="utf-8") == VALID_MESSAGE_PATCH
    metadata = json.loads(output.with_suffix(".patch.meta.json").read_text(encoding="utf-8"))
    assert metadata["status"] == "accepted"
    assert metadata["validation"]["exact_requested_replacement"] is True
    assert requests[0]["model"] == "qwen2.5-coder:3b-instruct"
    assert requests[0]["options"]["num_ctx"] == 1536
    assert requests[0]["format"]["required"] == ["patch"]
    assert metadata["model"]["revision"].startswith("4a188102")


def test_patch_generation_rejects_extra_model_changes(monkeypatch, tmp_path) -> None:
    proposal_path = tmp_path / "proposal.json"
    proposal_path.write_text(
        (ROOT / "examples/agent/simd4x8-baseline-proposal.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "ef_gpu.llm._post_json",
        lambda *_args, **_kwargs: {"message": {"content": json.dumps({"patch": UNREQUESTED_PATCH})}},
    )
    output = tmp_path / "candidate.patch"
    try:
        generate_simd4x8_testbench_patch(proposal_path, output)
    except RuntimeError as error:
        assert "exactly the requested display replacement" in str(error)
    else:
        raise AssertionError("patch with an extra model change was accepted")
    assert not output.exists()
    assert output.with_suffix(".patch.rejected.txt").read_text(encoding="utf-8") == UNREQUESTED_PATCH
    metadata = json.loads(output.with_suffix(".patch.meta.json").read_text(encoding="utf-8"))
    assert metadata["status"] == "rejected"
    assert metadata["validation"]["exact_requested_replacement"] is False
