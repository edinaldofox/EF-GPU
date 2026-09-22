"""Small, dependency-free entry point for the EF-GPU research workspace."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

from ef_gpu.contracts import validate_proposal, validate_request
from ef_gpu.pipeline import run_simd4x8_iteration


def main() -> int:
    parser = argparse.ArgumentParser(description="EF-GPU development utilities")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("doctor", help="show locally installed EDA executables")
    for command in ("check-request", "check-proposal"):
        contract = subcommands.add_parser(command, help="validate a JSON contract")
        contract.add_argument("path", type=Path, help="JSON contract to validate")
    iteration = subcommands.add_parser("run-simd4x8", help="run one gate-based SIMD4x8 iteration")
    iteration.add_argument("request", type=Path, help="approved design request JSON")
    iteration.add_argument("proposal", type=Path, help="LLM or baseline proposal JSON")
    iteration.add_argument("--output", type=Path, help="directory for logs and manifest")
    iteration.add_argument("--physical", action="store_true", help="run OpenROAD after functional gates pass")
    iteration.add_argument("--allow-dirty", action="store_true", help="record, but allow, an uncommitted worktree")
    args = parser.parse_args()

    if args.command == "doctor":
        for executable in ("openroad", "yosys"):
            location = shutil.which(executable)
            state = location if location else "not found"
            print(f"{executable}: {state}")
        return 0
    if args.command in {"check-request", "check-proposal"}:
        if not args.path:
            parser.error(f"{args.command} requires a JSON file path")
        try:
            document = json.loads(args.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"invalid JSON input: {error}")
            return 2
        errors = (
            validate_request(document)
            if args.command == "check-request"
            else validate_proposal(document)
        )
        if errors:
            print("contract invalid:")
            for error in errors:
                print(f"- {error}")
            return 2
        print("contract valid")
        return 0
    if args.command == "run-simd4x8":
        output = args.output or Path("runs") / f"simd4x8-{datetime.now().strftime('%Y%m%dT%H%M%S')}"
        return run_simd4x8_iteration(
            args.request,
            args.proposal,
            output,
            physical=args.physical,
            allow_dirty=args.allow_dirty,
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
