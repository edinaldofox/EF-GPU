"""Bounded, auditable campaigns of safe SIMD4x8 agent iterations."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ef_gpu.iteration import ROOT, run_autonomous_simd4x8_iteration
from ef_gpu.llm import DEFAULT_MODEL


MAX_ATTEMPTS = 20


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_manifest(output: Path, manifest: dict[str, Any]) -> None:
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _response_sha256(attempt_output: Path) -> str | None:
    """Read the model-response fingerprint recorded by the patch gate."""
    metadata_path = attempt_output / "candidate.patch.meta.json"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        response_hash = metadata.get("response", {}).get("sha256")
    except (OSError, json.JSONDecodeError, AttributeError):
        return None
    return response_hash if isinstance(response_hash, str) else None


def run_simd4x8_campaign(
    request_path: Path,
    output: Path,
    *,
    attempts: int,
    model: str = DEFAULT_MODEL,
    seed: int = 42,
) -> int:
    """Run bounded independent attempts and stop at the first valid candidate."""
    if not 1 <= attempts <= MAX_ATTEMPTS:
        raise ValueError(f"attempts must be between 1 and {MAX_ATTEMPTS}")
    output.mkdir(parents=True, exist_ok=False)
    request_path = request_path.resolve()
    manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "command": "campaign-simd4x8",
        "started_at_utc": datetime.now(UTC).isoformat(),
        "request": {"path": str(request_path), "sha256": _sha256(request_path)},
        "model": {"id": model, "initial_seed": seed},
        "attempt_limit": attempts,
        "git": {"commit": _git("rev-parse", "HEAD"), "status": _git("status", "--porcelain")},
        "attempts": [],
    }
    if manifest["git"]["status"]:
        manifest.update(
            {
                "status": "invalid-worktree",
                "error": "main worktree is dirty; commit before a campaign",
                "finished_at_utc": datetime.now(UTC).isoformat(),
            }
        )
        _write_manifest(output, manifest)
        print(f"campaign invalid-worktree: {output / 'manifest.json'}")
        return 2

    seen_response_hashes: dict[str, int] = {}
    for index in range(attempts):
        attempt_seed = seed + index
        attempt_output = output / f"attempt-{index + 1:03d}"
        try:
            returncode = run_autonomous_simd4x8_iteration(
                request_path, attempt_output, model=model, seed=attempt_seed
            )
            attempt_manifest = json.loads((attempt_output / "manifest.json").read_text(encoding="utf-8"))
            status = attempt_manifest.get("status", "missing-status")
            error = attempt_manifest.get("error")
        except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exception:
            returncode = 2
            status = "runner-error"
            error = str(exception)
        response_sha256 = _response_sha256(attempt_output)
        manifest["attempts"].append(
            {
                "index": index + 1,
                "seed": attempt_seed,
                "returncode": returncode,
                "status": status,
                "path": attempt_output.name,
                "error": error,
                "response_sha256": response_sha256,
            }
        )
        if status == "candidate-valid":
            manifest.update(
                {
                    "status": "campaign-valid",
                    "stop_reason": "first valid candidate",
                    "finished_at_utc": datetime.now(UTC).isoformat(),
                }
            )
            _write_manifest(output, manifest)
            print(f"campaign campaign-valid: {output / 'manifest.json'}")
            return 0
        if response_sha256 and response_sha256 in seen_response_hashes:
            manifest.update(
                {
                    "status": "campaign-stopped-duplicate-response",
                    "stop_reason": "duplicate patch response",
                    "duplicate_of_attempt": seen_response_hashes[response_sha256],
                    "finished_at_utc": datetime.now(UTC).isoformat(),
                }
            )
            _write_manifest(output, manifest)
            print(f"campaign stopped on duplicate response: {output / 'manifest.json'}")
            return 1
        if response_sha256:
            seen_response_hashes[response_sha256] = index + 1

    manifest.update(
        {
            "status": "campaign-complete-no-valid-candidate",
            "stop_reason": "attempt limit reached",
            "finished_at_utc": datetime.now(UTC).isoformat(),
        }
    )
    _write_manifest(output, manifest)
    print(f"campaign complete without a valid candidate: {output / 'manifest.json'}")
    return 1
