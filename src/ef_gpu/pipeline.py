"""Reproducible, gate-based execution for the SIMD4x8 design baseline."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ef_gpu.contracts import validate_proposal, validate_request


ROOT = Path(__file__).resolve().parents[2]
SIM_IMAGE = os.environ.get("EF_GPU_SIM_IMAGE", "ef-gpu-sim:ubuntu24.04-iverilog12-v1")
OPENROAD_IMAGE = os.environ.get(
    "OPENROAD_IMAGE",
    "openroad/orfs@sha256:573c1716efa0e286c4f641c26d343e20929d58d27fffbb22be2d0b93f09764f6",
)


@dataclass(frozen=True)
class StepResult:
    name: str
    command: list[str]
    returncode: int | None
    duration_seconds: float
    log: str
    skipped: bool = False


def _load_contract(path: Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read JSON contract {path}: {error}") from error
    if not isinstance(document, dict):
        raise ValueError(f"contract root must be an object: {path}")
    return document


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=ROOT, text=True).strip()


def _docker_image_id(image: str) -> str | None:
    completed = subprocess.run(
        ["docker", "image", "inspect", image, "--format", "{{.Id}}"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def _run_step(name: str, command: list[str], output_dir: Path) -> StepResult:
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log = output_dir / f"{name}.log"
    log.write_text(completed.stdout, encoding="utf-8")
    return StepResult(
        name=name,
        command=command,
        returncode=completed.returncode,
        duration_seconds=round(time.monotonic() - started, 3),
        log=log.name,
    )


def _skipped_step(name: str, reason: str, output_dir: Path) -> StepResult:
    log = output_dir / f"{name}.log"
    log.write_text(f"SKIPPED: {reason}\n", encoding="utf-8")
    return StepResult(name, [], None, 0.0, log.name, skipped=True)


def run_simd4x8_iteration(
    request_path: Path,
    proposal_path: Path,
    output_dir: Path,
    *,
    physical: bool,
    allow_dirty: bool,
) -> int:
    """Run validation gates and write a manifest; return a process-style status."""
    request_path = request_path.resolve()
    proposal_path = proposal_path.resolve()
    output_dir.mkdir(parents=True, exist_ok=False)

    try:
        request = _load_contract(request_path)
        proposal = _load_contract(proposal_path)
    except ValueError as error:
        (output_dir / "manifest.json").write_text(
            json.dumps({"status": "invalid-contract", "error": str(error)}, indent=2) + "\n",
            encoding="utf-8",
        )
        print(error)
        return 2

    errors = [f"request: {error}" for error in validate_request(request)]
    errors += [f"proposal: {error}" for error in validate_proposal(proposal)]
    if request.get("design_id") != "simd4x8-vmac":
        errors.append("request.design_id must be simd4x8-vmac")
    if proposal.get("design_id") != request.get("design_id"):
        errors.append("proposal.design_id must match request.design_id")
    for artifact in proposal.get("artifacts", {}).get("rtl", []):
        if not (ROOT / artifact).is_file():
            errors.append(f"declared RTL artifact does not exist: {artifact}")
    for field in ("testbench", "sdc", "openroad_config"):
        artifact = proposal.get("artifacts", {}).get(field)
        if artifact and not (ROOT / artifact).exists():
            errors.append(f"declared {field} artifact does not exist: {artifact}")

    dirty = _git("status", "--porcelain")
    if dirty and not allow_dirty:
        errors.append("working tree is dirty; commit first or pass --allow-dirty")

    common: dict[str, Any] = {
        "schema_version": "1.0",
        "started_at_utc": datetime.now(UTC).isoformat(),
        "design_id": request.get("design_id"),
        "request": {"path": str(request_path), "sha256": _sha256(request_path)},
        "proposal": {"path": str(proposal_path), "sha256": _sha256(proposal_path)},
        "model": proposal.get("model"),
        "git": {"commit": _git("rev-parse", "HEAD"), "dirty": bool(dirty), "status": dirty},
        "toolchain": {
            "simulation_image": SIM_IMAGE,
            "simulation_image_id": _docker_image_id(SIM_IMAGE),
            "iverilog_package": "12.0-2build2",
            "openroad_image": OPENROAD_IMAGE,
            "openroad_image_id": _docker_image_id(OPENROAD_IMAGE),
            "pdk": request.get("constraints", {}).get("technology"),
        },
        "physical_requested": physical,
    }
    if errors:
        common.update({"status": "invalid-contract", "errors": errors, "steps": []})
        (output_dir / "manifest.json").write_text(json.dumps(common, indent=2) + "\n", encoding="utf-8")
        print("iteration rejected:")
        for error in errors:
            print(f"- {error}")
        return 2

    steps: list[StepResult] = []
    verification = _run_step("01-c-reference-and-rtl", ["bash", "scripts/verify-simd4x8.sh"], output_dir)
    steps.append(verification)
    if verification.returncode == 0:
        synthesis = _run_step("02-yosys-synthesis", ["bash", "scripts/synth-simd4x8.sh"], output_dir)
    else:
        synthesis = _skipped_step("02-yosys-synthesis", "functional verification failed", output_dir)
    steps.append(synthesis)

    if physical and verification.returncode == 0 and synthesis.returncode == 0:
        physical_step = _run_step("03-openroad", ["bash", "scripts/openroad-simd4x8.sh"], output_dir)
    elif physical:
        physical_step = _skipped_step("03-openroad", "a prior quality gate failed", output_dir)
    else:
        physical_step = _skipped_step("03-openroad", "not requested", output_dir)
    steps.append(physical_step)

    functional_valid = verification.returncode == 0 and synthesis.returncode == 0
    physical_valid = physical and functional_valid and physical_step.returncode == 0
    status = "physical-valid" if physical_valid else "functional-valid" if functional_valid else "invalid"
    common.update(
        {
            "finished_at_utc": datetime.now(UTC).isoformat(),
            "status": status,
            "functional_valid": functional_valid,
            "physical_valid": physical_valid,
            "steps": [asdict(step) for step in steps],
        }
    )
    (output_dir / "manifest.json").write_text(json.dumps(common, indent=2) + "\n", encoding="utf-8")
    print(f"iteration {status}: {output_dir / 'manifest.json'}")
    return 0 if functional_valid and (not physical or physical_valid) else 1
