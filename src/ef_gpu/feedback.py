"""Export auditable model patch attempts into a reviewable JSONL dataset."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
MODEL_LICENSES = {
    "qwen2.5-coder:1.5b-instruct": "Apache-2.0",
    "qwen2.5-coder:3b-instruct": "Qwen Research License Agreement (non-commercial research/evaluation only)",
}


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _metadata_paths(sources: Iterable[Path]) -> list[Path]:
    paths: set[Path] = set()
    for source in sources:
        if source.is_file() and source.name.endswith(".patch.meta.json"):
            paths.add(source.resolve())
        elif source.is_dir():
            paths.update(path.resolve() for path in source.rglob("*.patch.meta.json"))
        else:
            raise ValueError(f"feedback source does not exist or is not patch metadata: {source}")
    return sorted(paths)


def _artifact_text(metadata_path: Path, artifact_path: Any) -> str | None:
    if not isinstance(artifact_path, str):
        return None
    candidate = Path(artifact_path)
    options = [candidate] if candidate.is_absolute() else [ROOT / candidate, metadata_path.parent / candidate]
    for option in options:
        try:
            return option.read_text(encoding="utf-8")
        except OSError:
            continue
    return None


def _record(metadata_path: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    model = metadata.get("model") if isinstance(metadata.get("model"), dict) else {}
    inputs = metadata.get("inputs") if isinstance(metadata.get("inputs"), dict) else {}
    response = metadata.get("response") if isinstance(metadata.get("response"), dict) else {}
    validation = metadata.get("validation") if isinstance(metadata.get("validation"), dict) else {}
    artifact_text = _artifact_text(metadata_path, metadata.get("artifact_path"))
    return {
        "schema_version": "1.0",
        "task": "simd4x8-testbench-patch",
        "label": metadata.get("status"),
        "failure_reason": metadata.get("reason"),
        "input": {
            "prompt": inputs.get("prompt"),
            "prompt_sha256": inputs.get("prompt_sha256"),
            "target_path": inputs.get("target_path"),
            "target_sha256": inputs.get("target_sha256"),
            "proposal_sha256": inputs.get("proposal_sha256"),
        },
        "output": {
            "patch_text": artifact_text,
            "sha256": response.get("sha256"),
            "artifact_available": artifact_text is not None,
        },
        "validation": validation,
        "provenance": {
            "metadata_path": str(metadata_path),
            "git_commit": metadata.get("git_commit"),
            "model": model,
            "model_license": MODEL_LICENSES.get(model.get("id"), "unreviewed; do not train or distribute"),
            "exported_at_utc": datetime.now(UTC).isoformat(),
        },
    }


def collect_patch_feedback(sources: list[Path], output: Path) -> dict[str, Any]:
    """Create a deduplicated JSONL feedback set; it does not train a model."""
    if output.exists():
        raise ValueError(f"feedback output already exists: {output}")
    paths = _metadata_paths(sources)
    if not paths:
        raise ValueError("no .patch.meta.json files found")
    records: list[dict[str, Any]] = []
    seen_response_hashes: set[str] = set()
    skipped_duplicates = 0
    for path in paths:
        try:
            metadata = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"invalid patch metadata {path}: {error}") from error
        if not isinstance(metadata, dict):
            raise ValueError(f"patch metadata root must be an object: {path}")
        record = _record(path, metadata)
        response_hash = record["output"]["sha256"]
        if isinstance(response_hash, str) and response_hash in seen_response_hashes:
            skipped_duplicates += 1
            continue
        if isinstance(response_hash, str):
            seen_response_hashes.add(response_hash)
        records.append(record)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8"
    )
    summary = {
        "schema_version": "1.0",
        "command": "collect-patch-feedback",
        "output": str(output),
        "records_written": len(records),
        "duplicate_responses_skipped": skipped_duplicates,
        "source_metadata_files": len(paths),
        "output_sha256": _sha256_text(output.read_text(encoding="utf-8")),
        "created_at_utc": datetime.now(UTC).isoformat(),
        "training_status": "not approved; license and split review required",
    }
    summary_path = output.with_suffix(output.suffix + ".summary.json")
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary
