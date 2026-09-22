"""Reproducible narrow evaluation for the restricted SIMD4x8 patch task."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ef_gpu.llm import MODEL_REVISIONS, generate_simd4x8_testbench_patch, model_revision


def evaluate_patch_models(
    proposal_path: Path,
    output: Path,
    *,
    models: list[str],
    seed: int,
) -> int:
    """Evaluate pinned models on one narrow patch task without changing ROOT."""
    if not models:
        raise ValueError("at least one model is required")
    if len(set(models)) != len(models):
        raise ValueError("models must be unique")
    for model in models:
        model_revision(model)
    if output.exists():
        raise ValueError(f"evaluation output already exists: {output}")
    output.mkdir(parents=True)
    proposal_path = proposal_path.resolve()
    results: list[dict[str, Any]] = []
    for index, model in enumerate(models, start=1):
        slug = model.replace(":", "-").replace("/", "-")
        patch_path = output / f"{index:02d}-{slug}.patch"
        try:
            generate_simd4x8_testbench_patch(proposal_path, patch_path, model=model, seed=seed)
            returncode = 0
        except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
            returncode = 2
            error_text = str(error)
        else:
            error_text = None
        metadata_path = patch_path.with_suffix(".patch.meta.json")
        metadata: dict[str, Any] = {}
        if metadata_path.is_file():
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        results.append(
            {
                "model": model,
                "revision": MODEL_REVISIONS[model],
                "seed": seed,
                "returncode": returncode,
                "status": metadata.get("status", "generation-error"),
                "reason": metadata.get("reason", error_text),
                "metadata": metadata_path.name if metadata_path.is_file() else None,
                "response_sha256": metadata.get("response", {}).get("sha256"),
                "validation": metadata.get("validation"),
            }
        )
    accepted = sum(result["status"] == "accepted" for result in results)
    manifest = {
        "schema_version": "1.0",
        "command": "evaluate-patch-models",
        "task": "simd4x8-testbench-patch-single-task",
        "proposal_path": str(proposal_path),
        "seed": seed,
        "started_and_finished_at_utc": datetime.now(UTC).isoformat(),
        "results": results,
        "accepted_count": accepted,
        "evaluated_count": len(results),
        "interpretation": "narrow smoke evaluation only; not an RTL-quality benchmark",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"patch evaluation complete: {output / 'manifest.json'}")
    return 0 if accepted else 1
