"""Deterministic, auditable candidate-patch templates.

Templates are intentionally much narrower than model-authored patches.  A model
may eventually select a reviewed template identifier, but this module alone
renders the source change from an immutable local recipe.  It never invokes a
model and never edits the primary worktree.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Final


ROOT = Path(__file__).resolve().parents[2]
TESTBENCH_PATH: Final = "designs/simd4x8/tb/tb_simd4x8_c_ref.sv"

# Each recipe is reviewed source text, not a prompt.  Keep templates small and
# single-purpose so their generated diff remains straightforward to audit.
TEMPLATES: Final = {
    "testbench-pass-message-label": {
        "description": "Labels the existing SIMD4x8 passing-test message as a candidate run.",
        "target_path": TESTBENCH_PATH,
        "old": '        $display("SIMD4x8 C-reference RTL test passed: %0d vectors", vector_count);\n',
        "new": '        $display("SIMD4x8 candidate C-reference RTL test passed: %0d vectors", vector_count);\n',
    }
}
TEMPLATE_IDS: Final = frozenset(TEMPLATES)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def template_description(template_id: str) -> str:
    """Return the reviewed description for one known deterministic template."""
    try:
        return str(TEMPLATES[template_id]["description"])
    except KeyError as error:
        supported = ", ".join(sorted(TEMPLATE_IDS))
        raise ValueError(f"unknown template {template_id!r}; use one of: {supported}") from error


def render_simd4x8_template_patch(template_id: str) -> str:
    """Render a patch from current source without altering it.

    The old text must occur exactly once.  This stops a stale template from
    silently matching a different source location after the testbench changes.
    """
    template_description(template_id)  # validates the ID and gives consistent errors
    recipe = TEMPLATES[template_id]
    target_path = str(recipe["target_path"])
    source_path = ROOT / target_path
    source = source_path.read_text(encoding="utf-8")
    old, new = str(recipe["old"]), str(recipe["new"])
    occurrences = source.count(old)
    if occurrences != 1:
        raise ValueError(
            f"template {template_id!r} expected one occurrence in {target_path}, found {occurrences}"
        )
    candidate = source.replace(old, new, 1)
    diff = difflib.unified_diff(
        source.splitlines(keepends=True),
        candidate.splitlines(keepends=True),
        fromfile=f"a/{target_path}",
        tofile=f"b/{target_path}",
    )
    return f"diff --git a/{target_path} b/{target_path}\n" + "".join(diff)


def emit_simd4x8_template_patch(template_id: str, output_path: Path) -> Path:
    """Write a new generated patch and its provenance record outside the source tree."""
    if output_path.exists():
        raise ValueError(f"refusing to overwrite existing template patch: {output_path}")
    template_description(template_id)
    patch = render_simd4x8_template_patch(template_id)
    target_path = str(TEMPLATES[template_id]["target_path"])
    source = (ROOT / target_path).read_text(encoding="utf-8")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(patch, encoding="utf-8")
    metadata = {
        "schema_version": "1.0",
        "command": "emit-simd4x8-template-patch",
        "source": "deterministic-template",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "git_commit": _git_head(),
        "template": {
            "id": template_id,
            "description": template_description(template_id),
            "target_path": target_path,
        },
        "source_sha256": _sha256_text(source),
        "patch_sha256": _sha256_text(patch),
        "output": str(output_path),
    }
    metadata_path = output_path.with_suffix(output_path.suffix + ".template.meta.json")
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return output_path
