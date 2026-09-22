from __future__ import annotations

import json
from pathlib import Path

from ef_gpu.contracts import validate_proposal, validate_request


ROOT = Path(__file__).resolve().parents[1]


def test_example_request_is_valid() -> None:
    request = json.loads((ROOT / "examples/agent/alu8-request.json").read_text())
    assert validate_request(request) == []


def test_example_proposal_is_valid() -> None:
    proposal = json.loads((ROOT / "examples/agent/alu8-proposal.json").read_text())
    assert validate_proposal(proposal) == []


def test_request_requires_positive_clock_and_testbench() -> None:
    errors = validate_request(
        {
            "schema_version": "1.0",
            "design_id": "bad",
            "objective": "bad input",
            "interfaces": [{"name": "a"}],
            "constraints": {"target_clock_mhz": 0},
            "acceptance": {},
        }
    )
    assert "constraints.target_clock_mhz must be a positive number" in errors
    assert "interfaces[0].direction must be input, output, or inout" in errors
    assert "interfaces[0].width must be a positive integer" in errors
    assert "acceptance.testbench is required" in errors
