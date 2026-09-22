"""Local, structured proposal generation through Ollama.

This module deliberately creates planning proposals only. It never asks a model
to write into the repository or applies text returned by the model.
"""

from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ef_gpu.contracts import validate_request


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = "qwen2.5-coder:1.5b-instruct"
DEFAULT_MODEL_DIGEST = "d7372fd828518a4d38b1eb196c673c31a85f2ed302b3d1e406c4c2d1b64a0668"
OLLAMA_API = os.environ.get("EF_GPU_OLLAMA_API", "http://localhost:11434/api")
ALLOWED_TARGET_FILES = {
    "designs/simd4x8/rtl/mult8_comb.sv",
    "designs/simd4x8/rtl/mult8_iter.sv",
    "designs/simd4x8/rtl/simd4x8_mult_iter4.sv",
    "designs/simd4x8/rtl/simd4x8_mac_comb_top.sv",
    "designs/simd4x8/rtl/simd4x8_mac_iter_top.sv",
    "designs/simd4x8/tb/tb_simd4x8_c_ref.sv",
}


def _post_json(endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{OLLAMA_API}/{endpoint}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Ollama request failed: {error}") from error
    if not isinstance(data, dict):
        raise RuntimeError("Ollama returned a non-object response")
    return data


def _git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def validate_simd4x8_plan(plan: dict[str, Any]) -> list[str]:
    """Reject plans that declare or imply an interface change before execution."""
    errors: list[str] = []
    changes = plan.get("changes")
    assumptions = plan.get("assumptions")
    target_files = plan.get("target_files")
    validation = plan.get("validation")
    if not isinstance(changes, list) or not changes or not all(isinstance(item, str) for item in changes):
        errors.append("changes must be a non-empty string list")
    if not isinstance(assumptions, list) or not all(isinstance(item, str) for item in assumptions):
        errors.append("assumptions must be a string list")
    if plan.get("preserves_interface") is not True:
        errors.append("preserves_interface must be true")
    if not isinstance(target_files, list) or not target_files or not all(isinstance(item, str) for item in target_files):
        errors.append("target_files must be a non-empty string list")
    elif unknown := set(target_files) - ALLOWED_TARGET_FILES:
        errors.append(f"target_files contain unsupported path(s): {', '.join(sorted(unknown))}")
    if not isinstance(validation, str) or "c-reference" not in validation.lower():
        errors.append("validation must explicitly use the C-reference RTL regression")
    text = " ".join(changes if isinstance(changes, list) else []).lower()
    forbidden = (
        "new input port",
        "new output port",
        "add input port",
        "add output port",
        "change interface",
        "new module",
        "add a module",
    )
    if any(phrase in text for phrase in forbidden):
        errors.append("changes imply an interface modification")
    return errors


def build_simd4x8_proposal(
    request: dict[str, Any],
    plan: dict[str, Any],
    *,
    model: str,
    model_digest: str,
    seed: int,
) -> dict[str, Any]:
    """Wrap a model plan in a complete, non-mutating EF-GPU proposal."""
    errors = validate_simd4x8_plan(plan)
    if errors:
        raise ValueError("invalid model plan: " + "; ".join(errors))
    changes = plan["changes"]
    assumptions = plan["assumptions"]
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return {
        "schema_version": "1.0",
        "proposal_id": f"ollama-{timestamp}",
        "design_id": request["design_id"],
        "base_commit": _git_head(),
        "model": {
            "id": model,
            "revision": model_digest,
            "seed": seed,
            "temperature": 0.0,
            "context_sources": ["examples/agent/simd4x8-request.json", "designs/simd4x8/README.md"],
        },
        "artifacts": {
            "rtl": [
                "designs/simd4x8/rtl/mult8_comb.sv",
                "designs/simd4x8/rtl/mult8_iter.sv",
                "designs/simd4x8/rtl/simd4x8_mult_iter4.sv",
                "designs/simd4x8/rtl/simd4x8_mac_comb_top.sv",
                "designs/simd4x8/rtl/simd4x8_mac_iter_top.sv",
            ],
            "testbench": "designs/simd4x8/tb/tb_simd4x8_c_ref.sv",
            "sdc": "configs/openroad/simd4x8/comb/constraints.sdc",
            "openroad_config": "configs/openroad/simd4x8",
        },
        "changes": changes,
        "assumptions": assumptions,
    }


def generate_simd4x8_proposal(
    request_path: Path,
    output_path: Path,
    *,
    model: str = DEFAULT_MODEL,
    seed: int = 42,
) -> Path:
    """Ask the local model for a plan, validate it, and write a proposal JSON."""
    try:
        request = json.loads(request_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read request JSON: {error}") from error
    errors = validate_request(request)
    if errors:
        raise ValueError("invalid request: " + "; ".join(errors))
    if request.get("design_id") != "simd4x8-vmac":
        raise ValueError("request.design_id must be simd4x8-vmac")

    plan_schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["changes", "assumptions", "target_files", "preserves_interface", "validation"],
        "properties": {
            "changes": {"type": "array", "minItems": 1, "items": {"type": "string"}},
            "assumptions": {"type": "array", "items": {"type": "string"}},
            "target_files": {"type": "array", "minItems": 1, "items": {"type": "string", "enum": sorted(ALLOWED_TARGET_FILES)}},
            "preserves_interface": {"const": True},
            "validation": {"type": "string", "minLength": 1},
        },
    }
    request_summary = {
        "design_id": request["design_id"],
        "objective": request["objective"],
        "target_clock_mhz": request["constraints"]["target_clock_mhz"],
        "acceptance_testbench": request["acceptance"]["testbench"],
        "interface_rule": "Preserve the existing public interface.",
    }
    prompt = (
        "You are planning a small, verified SIMD4x8 VMAC experiment. "
        "Return JSON only. Do not claim to execute tests. Do not output RTL, shell commands, or markdown. "
        "The baseline already has four unsigned 8-bit lanes and combinational plus iterative VMAC variants. "
        "For this first planning task, propose exactly one testbench-only verification improvement in designs/simd4x8/tb/tb_simd4x8_c_ref.sv. "
        "Do not add modules, RTL, ports, or files. preserves_interface must be true and target_files must contain that testbench path. "
        "validation must explicitly say C-reference RTL regression. changes must be a non-empty list; assumptions must be a list. "
        f"Design request summary: {json.dumps(request_summary, separators=(',', ':'))}"
    )
    response = _post_json(
        "chat",
        {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an EF-GPU planning assistant. Correctness and reproducibility come first.",
                },
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "format": plan_schema,
            "options": {"temperature": 0, "seed": seed, "num_ctx": 1024, "num_predict": 256},
            "keep_alive": "1m",
        },
    )
    content = response.get("message", {}).get("content")
    if not isinstance(content, str):
        raise RuntimeError("Ollama response has no message.content string")
    try:
        plan = json.loads(content)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Ollama returned invalid plan JSON: {error}") from error
    if not isinstance(plan, dict):
        raise RuntimeError("Ollama plan must be a JSON object")

    proposal = build_simd4x8_proposal(
        request, plan, model=model, model_digest=DEFAULT_MODEL_DIGEST, seed=seed
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(proposal, indent=2) + "\n", encoding="utf-8")
    metadata_path = output_path.with_suffix(output_path.suffix + ".meta.json")
    metadata = {
        "model": model,
        "model_digest": DEFAULT_MODEL_DIGEST,
        "backend": "ollama-local",
        "options": {"temperature": 0, "seed": seed, "num_ctx": 1024, "num_predict": 256},
        "response_metrics": {key: response.get(key) for key in ("total_duration", "load_duration", "prompt_eval_count", "eval_count")},
        "model_plan": plan,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return output_path
