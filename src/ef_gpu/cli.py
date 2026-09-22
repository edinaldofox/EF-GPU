"""Small, dependency-free entry point for the EF-GPU research workspace."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from ef_gpu.contracts import validate_proposal, validate_request


def main() -> int:
    parser = argparse.ArgumentParser(description="EF-GPU development utilities")
    parser.add_argument("command", choices=("doctor", "check-request", "check-proposal"), help="utility command to run")
    parser.add_argument("path", nargs="?", help="JSON contract to validate")
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
            document = json.loads(Path(args.path).read_text(encoding="utf-8"))
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
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
