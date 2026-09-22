"""Small, dependency-free entry point for the EF-GPU research workspace."""

from __future__ import annotations

import argparse
import shutil


def main() -> int:
    parser = argparse.ArgumentParser(description="EF-GPU development utilities")
    parser.add_argument(
        "command", choices=("doctor",), help="utility command to run"
    )
    args = parser.parse_args()

    if args.command == "doctor":
        for executable in ("openroad", "yosys"):
            location = shutil.which(executable)
            state = location if location else "not found"
            print(f"{executable}: {state}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
