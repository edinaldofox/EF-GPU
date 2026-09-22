from __future__ import annotations

import json
from pathlib import Path

from ef_gpu.contracts import validate_proposal, validate_request


ROOT = Path(__file__).resolve().parents[1]


def test_simd4x8_pipeline_contracts_are_valid() -> None:
    request = json.loads((ROOT / "examples/agent/simd4x8-request.json").read_text())
    proposal = json.loads((ROOT / "examples/agent/simd4x8-baseline-proposal.json").read_text())

    assert validate_request(request) == []
    assert validate_proposal(proposal) == []
    assert request["design_id"] == proposal["design_id"] == "simd4x8-vmac"
