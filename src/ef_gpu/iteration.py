"""Safe end-to-end orchestration for a narrowly scoped LLM SIMD4x8 attempt."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ef_gpu.contracts import validate_request
from ef_gpu.llm import DEFAULT_MODEL, generate_simd4x8_proposal, generate_simd4x8_testbench_patch
from ef_gpu.staging import stage_simd4x8_patch


ROOT = Path(__file__).resolve().parents[2]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _write_manifest(output: Path, manifest: dict[str, Any]) -> None:
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _finished(manifest: dict[str, Any], status: str, error: str | None = None) -> None:
    manifest["status"] = status
    manifest["finished_at_utc"] = datetime.now(UTC).isoformat()
    if error:
        manifest["error"] = error


def run_autonomous_simd4x8_iteration(
    request_path: Path,
    output: Path,
    *,
    model: str = DEFAULT_MODEL,
    seed: int = 42,
) -> int:
    """Run proposal, restricted patch drafting, and disposable candidate gates.

    The repository worktree is never changed. A rejected model response is a
    normal terminal outcome and remains auditable under ``output``.
    """
    output.mkdir(parents=True, exist_ok=False)
    request_path = request_path.resolve()
    manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "command": "iterate-simd4x8",
        "started_at_utc": datetime.now(UTC).isoformat(),
        "request": {
            "path": str(request_path),
            "sha256": _sha256(request_path) if request_path.is_file() else None,
        },
        "model": {"id": model, "seed": seed},
        "git": {"commit": _git("rev-parse", "HEAD"), "status": _git("status", "--porcelain")},
        "steps": [],
    }
    try:
        request = json.loads(request_path.read_text(encoding="utf-8"))
        errors = validate_request(request) if isinstance(request, dict) else ["request root must be an object"]
        if not isinstance(request, dict) or request.get("design_id") != "simd4x8-vmac":
            errors.append("request.design_id must be simd4x8-vmac")
    except (OSError, json.JSONDecodeError) as error:
        errors = [f"cannot read request: {error}"]
    if manifest["git"]["status"]:
        errors.append("main worktree is dirty; commit before an autonomous iteration")
    if errors:
        _finished(manifest, "invalid-request", "; ".join(errors))
        _write_manifest(output, manifest)
        print(f"autonomous iteration invalid-request: {output / 'manifest.json'}")
        return 2

    proposal_path = output / "proposal.json"
    try:
        generate_simd4x8_proposal(request_path, proposal_path, model=model, seed=seed)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        manifest["steps"].append({"name": "01-proposal", "status": "rejected", "path": proposal_path.name})
        _finished(manifest, "proposal-rejected", str(error))
        _write_manifest(output, manifest)
        print(f"autonomous iteration proposal-rejected: {output / 'manifest.json'}")
        return 2
    manifest["steps"].append(
        {
            "name": "01-proposal",
            "status": "accepted",
            "path": proposal_path.name,
            "sha256": _sha256(proposal_path),
            "metadata": proposal_path.with_suffix(".json.meta.json").name,
        }
    )

    patch_path = output / "candidate.patch"
    try:
        generate_simd4x8_testbench_patch(proposal_path, patch_path, model=model, seed=seed)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        manifest["steps"].append(
            {
                "name": "02-restricted-patch",
                "status": "rejected",
                "metadata": patch_path.with_suffix(".patch.meta.json").name,
                "raw_response": patch_path.with_suffix(".patch.rejected.txt").name,
            }
        )
        _finished(manifest, "patch-rejected", str(error))
        _write_manifest(output, manifest)
        print(f"autonomous iteration patch-rejected: {output / 'manifest.json'}")
        return 2
    manifest["steps"].append(
        {
            "name": "02-restricted-patch",
            "status": "accepted",
            "path": patch_path.name,
            "sha256": _sha256(patch_path),
            "metadata": patch_path.with_suffix(".patch.meta.json").name,
        }
    )

    candidate_output = output / "candidate"
    result = stage_simd4x8_patch(request_path, proposal_path, patch_path, candidate_output)
    candidate_manifest_path = candidate_output / "manifest.json"
    candidate_status = "missing-manifest"
    if candidate_manifest_path.is_file():
        candidate_status = json.loads(candidate_manifest_path.read_text(encoding="utf-8")).get("status", candidate_status)
    manifest["steps"].append(
        {
            "name": "03-disposable-candidate",
            "status": candidate_status,
            "path": str(candidate_manifest_path.relative_to(output)),
        }
    )
    _finished(manifest, candidate_status)
    _write_manifest(output, manifest)
    print(f"autonomous iteration {candidate_status}: {output / 'manifest.json'}")
    return result
