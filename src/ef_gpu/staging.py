"""Apply a candidate patch in a disposable Git worktree and run quality gates."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ef_gpu.contracts import validate_proposal, validate_request


ROOT = Path(__file__).resolve().parents[2]
ALLOWED_PATCH_PATHS = {"designs/simd4x8/tb/tb_simd4x8_c_ref.sv"}


def _git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def _load(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return document


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _patch_paths(patch: Path) -> set[str]:
    completed = subprocess.run(
        ["git", "apply", "--numstat", "--", str(patch)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode:
        raise ValueError(f"invalid patch: {completed.stderr.strip()}")
    paths = {line.split("\t")[-1] for line in completed.stdout.splitlines() if line}
    if not paths:
        raise ValueError("patch changes no files")
    unknown = paths - ALLOWED_PATCH_PATHS
    if unknown:
        raise ValueError(f"patch changes forbidden path(s): {', '.join(sorted(unknown))}")
    return paths


def _step(name: str, command: list[str], cwd: Path, output: Path) -> dict[str, Any]:
    started = time.monotonic()
    completed = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log = output / f"{name}.log"
    log.write_text(completed.stdout, encoding="utf-8")
    return {"name": name, "command": command, "returncode": completed.returncode,
            "duration_seconds": round(time.monotonic() - started, 3), "log": log.name}


def stage_simd4x8_patch(request_path: Path, proposal_path: Path, patch_path: Path, output: Path) -> int:
    """Never modify ROOT; validate a testbench patch in a detached worktree."""
    output.mkdir(parents=True, exist_ok=False)
    request_path, proposal_path, patch_path = (path.resolve() for path in (request_path, proposal_path, patch_path))
    manifest: dict[str, Any] = {"schema_version": "1.0", "started_at_utc": datetime.now(UTC).isoformat()}
    try:
        request, proposal = _load(request_path), _load(proposal_path)
        errors = validate_request(request) + validate_proposal(proposal)
        if request.get("design_id") != "simd4x8-vmac" or proposal.get("design_id") != "simd4x8-vmac":
            errors.append("request and proposal must target simd4x8-vmac")
        if _git("status", "--porcelain"):
            errors.append("main worktree is dirty; commit before staging a patch")
        changed_paths = _patch_paths(patch_path)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        errors = [str(error)]
        changed_paths = set()
    manifest.update({"request_sha256": _sha256(request_path), "proposal_sha256": _sha256(proposal_path),
                     "patch_sha256": _sha256(patch_path), "changed_paths": sorted(changed_paths), "errors": errors})
    if errors:
        manifest["status"] = "rejected"
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print("candidate rejected: " + "; ".join(errors))
        return 2

    temporary_root = Path(tempfile.mkdtemp(prefix="ef-gpu-candidate-"))
    worktree = temporary_root / "worktree"
    steps: list[dict[str, Any]] = []
    try:
        base_commit = proposal["base_commit"]
        subprocess.run(["git", "worktree", "add", "--detach", str(worktree), base_commit], cwd=ROOT, check=True)
        applied = subprocess.run(["git", "apply", "--check", str(patch_path)], cwd=worktree, text=True, stderr=subprocess.PIPE)
        if applied.returncode:
            raise ValueError(f"patch cannot apply to {base_commit}: {applied.stderr.strip()}")
        subprocess.run(["git", "apply", str(patch_path)], cwd=worktree, check=True)
        steps.append(_step("01-c-reference-and-rtl", ["bash", "scripts/verify-simd4x8.sh"], worktree, output))
        if steps[-1]["returncode"] == 0:
            steps.append(_step("02-yosys-synthesis", ["bash", "scripts/synth-simd4x8.sh"], worktree, output))
        else:
            steps.append({"name": "02-yosys-synthesis", "skipped": True, "reason": "functional verification failed"})
        functional_valid = all(step.get("returncode", 0) == 0 for step in steps if not step.get("skipped"))
        manifest.update({"base_commit": base_commit, "candidate_commit": _git("rev-parse", "HEAD", cwd=worktree),
                         "steps": steps, "functional_valid": functional_valid,
                         "status": "candidate-valid" if functional_valid else "candidate-invalid"})
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        manifest.update({"steps": steps, "functional_valid": False, "status": "candidate-invalid", "errors": [str(error)]})
    finally:
        if worktree.exists():
            subprocess.run(["git", "worktree", "remove", "--force", str(worktree)], cwd=ROOT, check=False)
        shutil.rmtree(temporary_root, ignore_errors=True)
    manifest["finished_at_utc"] = datetime.now(UTC).isoformat()
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"candidate {manifest['status']}: {output / 'manifest.json'}")
    return 0 if manifest["status"] == "candidate-valid" else 1
