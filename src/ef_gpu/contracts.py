"""Small, dependency-free checks for LLM design-agent contracts.

JSON Schema documents remain the normative, interoperable form in ``schemas/``.
These checks intentionally cover the safety-critical minimum for local use.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def _required(document: Mapping[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f"missing required field: {field}" for field in fields if field not in document]


def _object(value: Any, field: str) -> list[str]:
    return [] if isinstance(value, dict) else [f"{field} must be an object"]


def _non_empty_list(value: Any, field: str) -> list[str]:
    return [] if isinstance(value, list) and value else [f"{field} must be a non-empty list"]


def validate_request(document: Any) -> list[str]:
    """Return structural errors for a design request, or an empty list."""
    if not isinstance(document, dict):
        return ["root must be an object"]
    errors = _required(
        document,
        ("schema_version", "design_id", "objective", "interfaces", "constraints", "acceptance"),
    )
    if document.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")
    for field in ("design_id", "objective"):
        if field in document and not isinstance(document[field], str):
            errors.append(f"{field} must be a string")
    errors += _non_empty_list(document.get("interfaces"), "interfaces")
    errors += _object(document.get("constraints"), "constraints")
    errors += _object(document.get("acceptance"), "acceptance")
    if isinstance(document.get("interfaces"), list):
        for index, interface in enumerate(document["interfaces"]):
            label = f"interfaces[{index}]"
            if not isinstance(interface, dict):
                errors.append(f"{label} must be an object")
                continue
            if not isinstance(interface.get("name"), str) or not interface["name"]:
                errors.append(f"{label}.name must be a non-empty string")
            if interface.get("direction") not in {"input", "output", "inout"}:
                errors.append(f"{label}.direction must be input, output, or inout")
            if not isinstance(interface.get("width"), int) or interface["width"] <= 0:
                errors.append(f"{label}.width must be a positive integer")
    if isinstance(document.get("constraints"), dict):
        clock = document["constraints"].get("target_clock_mhz")
        if not isinstance(clock, (int, float)) or clock <= 0:
            errors.append("constraints.target_clock_mhz must be a positive number")
    if isinstance(document.get("acceptance"), dict) and not document["acceptance"].get("testbench"):
        errors.append("acceptance.testbench is required")
    return errors


def validate_proposal(document: Any) -> list[str]:
    """Return structural errors for a design proposal, or an empty list."""
    if not isinstance(document, dict):
        return ["root must be an object"]
    errors = _required(
        document,
        ("schema_version", "proposal_id", "design_id", "base_commit", "model", "artifacts", "changes"),
    )
    if document.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")
    for field in ("proposal_id", "design_id", "base_commit"):
        if field in document and not isinstance(document[field], str):
            errors.append(f"{field} must be a string")
    errors += _object(document.get("model"), "model")
    errors += _object(document.get("artifacts"), "artifacts")
    errors += _non_empty_list(document.get("changes"), "changes")
    if "patch_template" in document and (
        not isinstance(document["patch_template"], str) or not document["patch_template"]
    ):
        errors.append("patch_template must be a non-empty string")
    if isinstance(document.get("model"), dict):
        for field in ("id", "revision", "seed"):
            if field not in document["model"]:
                errors.append(f"model.{field} is required")
    if isinstance(document.get("artifacts"), dict):
        rtl = document["artifacts"].get("rtl")
        if not isinstance(rtl, list) or not rtl or not all(isinstance(path, str) and path for path in rtl):
            errors.append("artifacts.rtl must be a non-empty list of paths")
        for field in ("testbench", "sdc"):
            if not isinstance(document["artifacts"].get(field), str) or not document["artifacts"][field]:
                errors.append(f"artifacts.{field} must be a non-empty path")
    return errors
