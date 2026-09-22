"""Small, dependency-free entry point for the EF-GPU research workspace."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from ef_gpu.contracts import validate_proposal, validate_request
from ef_gpu.circuit_data import export_circuit_sft, validate_circuit_dataset
from ef_gpu.internal_corpus import build_internal_circuit_corpus
from ef_gpu.campaign import run_simd4x8_campaign
from ef_gpu.evaluation import evaluate_patch_models
from ef_gpu.feedback import collect_patch_feedback
from ef_gpu.iteration import run_autonomous_simd4x8_iteration
from ef_gpu.llm import MODEL_REVISIONS, generate_simd4x8_proposal, generate_simd4x8_testbench_patch
from ef_gpu.pipeline import run_simd4x8_iteration
from ef_gpu.staging import stage_simd4x8_patch
from ef_gpu.templates import TEMPLATE_IDS, emit_simd4x8_template_patch


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
    proposal = subcommands.add_parser("propose-simd4x8", help="create a planning proposal using local Ollama")
    proposal.add_argument("request", type=Path, help="approved design request JSON")
    proposal.add_argument("--output", type=Path, help="proposal JSON path; defaults under runs/")
    proposal.add_argument("--model", default="qwen2.5-coder:1.5b-instruct", help="local Ollama model tag")
    proposal.add_argument("--seed", type=int, default=42, help="deterministic Ollama seed")
    patch = subcommands.add_parser("draft-simd4x8-patch", help="draft a restricted testbench diff with local Ollama")
    patch.add_argument("proposal", type=Path, help="validated SIMD4x8 proposal JSON")
    patch.add_argument("--output", type=Path, help="patch path; defaults under runs/")
    patch.add_argument("--model", default="qwen2.5-coder:1.5b-instruct", help="local Ollama patch model")
    patch.add_argument("--seed", type=int, default=42, help="deterministic Ollama seed")
    template = subcommands.add_parser(
        "emit-simd4x8-template-patch", help="render a reviewed deterministic SIMD4x8 patch template"
    )
    template.add_argument("template_id", choices=sorted(TEMPLATE_IDS), help="reviewed template identifier")
    template.add_argument("--output", type=Path, required=True, help="new patch path under a run directory")
    autonomous = subcommands.add_parser("iterate-simd4x8", help="run the safe autonomous SIMD4x8 candidate loop")
    autonomous.add_argument("request", type=Path, help="approved SIMD4x8 design request JSON")
    autonomous.add_argument("--output", type=Path, help="directory for the complete attempt record")
    autonomous.add_argument("--model", default="qwen2.5-coder:1.5b-instruct", help="local Ollama planning model")
    autonomous.add_argument("--seed", type=int, default=42, help="deterministic Ollama seed")
    autonomous.add_argument(
        "--patch-source", choices=("model", "template"), default="model",
        help="untrusted model diff or deterministic template selected in the proposal",
    )
    campaign = subcommands.add_parser("campaign-simd4x8", help="run bounded safe SIMD4x8 agent attempts")
    campaign.add_argument("request", type=Path, help="approved SIMD4x8 design request JSON")
    campaign.add_argument("--attempts", type=int, default=3, help="number of attempts, from 1 to 20")
    campaign.add_argument("--output", type=Path, help="directory for the campaign record")
    campaign.add_argument("--model", default="qwen2.5-coder:1.5b-instruct", help="local Ollama planning model")
    campaign.add_argument("--seed", type=int, default=42, help="initial deterministic Ollama seed")
    campaign.add_argument(
        "--patch-source", choices=("model", "template"), default="model",
        help="untrusted model diff or deterministic template selected in each proposal",
    )
    feedback = subcommands.add_parser("collect-patch-feedback", help="export reviewed patch attempts to JSONL")
    feedback.add_argument("sources", nargs="+", type=Path, help="run directories or .patch.meta.json files")
    feedback.add_argument("--output", type=Path, required=True, help="new JSONL feedback dataset path")
    circuit_dataset = subcommands.add_parser(
        "check-circuit-dataset", help="validate reviewed SystemVerilog training data without training a model"
    )
    circuit_dataset.add_argument("path", type=Path, help="circuit-examples JSONL path")
    circuit_sft = subcommands.add_parser(
        "export-circuit-sft", help="export reviewed circuit examples to train/validation chat JSONL"
    )
    circuit_sft.add_argument("source", type=Path, help="validated circuit-examples JSONL path")
    circuit_sft.add_argument("--output", type=Path, required=True, help="new SFT JSONL path")
    internal_corpus = subcommands.add_parser(
        "build-internal-circuit-corpus", help="materialize the licensed EF-GPU seed corpus from verified source blocks"
    )
    internal_corpus.add_argument("--output", type=Path, required=True, help="new internal corpus JSONL path")
    evaluation = subcommands.add_parser("evaluate-patch-models", help="run a narrow reproducible patch evaluation")
    evaluation.add_argument("proposal", type=Path, help="validated SIMD4x8 proposal JSON")
    evaluation.add_argument("--models", nargs="+", default=sorted(MODEL_REVISIONS), help="pinned Ollama model tags")
    evaluation.add_argument("--seed", type=int, default=42, help="deterministic Ollama seed")
    evaluation.add_argument("--output", type=Path, required=True, help="new directory for evaluation artifacts")
    stage = subcommands.add_parser("stage-simd4x8", help="validate a testbench patch in a disposable Git worktree")
    stage.add_argument("request", type=Path, help="approved design request JSON")
    stage.add_argument("proposal", type=Path, help="proposal JSON with the base commit")
    stage.add_argument("patch", type=Path, help="unified diff; only the SIMD4x8 testbench is allowed")
    stage.add_argument("--output", type=Path, help="directory for candidate logs and manifest")
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
    if args.command == "propose-simd4x8":
        output = args.output or Path("runs") / f"proposal-simd4x8-{datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
        try:
            proposal_path = generate_simd4x8_proposal(args.request, output, model=args.model, seed=args.seed)
        except (RuntimeError, ValueError) as error:
            print(f"proposal generation failed: {error}")
            return 2
        print(f"proposal written: {proposal_path}")
        return 0
    if args.command == "stage-simd4x8":
        output = args.output or Path("runs") / f"candidate-simd4x8-{datetime.now().strftime('%Y%m%dT%H%M%S')}"
        return stage_simd4x8_patch(args.request, args.proposal, args.patch, output)
    if args.command == "draft-simd4x8-patch":
        output = args.output or Path("runs") / f"draft-simd4x8-{datetime.now().strftime('%Y%m%dT%H%M%S')}.patch"
        try:
            patch_path = generate_simd4x8_testbench_patch(
                args.proposal, output, model=args.model, seed=args.seed
            )
        except (RuntimeError, ValueError, OSError, json.JSONDecodeError) as error:
            print(f"patch generation failed: {error}")
            return 2
        print(f"patch written: {patch_path}")
        return 0
    if args.command == "emit-simd4x8-template-patch":
        try:
            patch_path = emit_simd4x8_template_patch(args.template_id, args.output)
        except (OSError, ValueError, subprocess.CalledProcessError) as error:
            print(f"template patch generation failed: {error}")
            return 2
        print(f"template patch written: {patch_path}")
        return 0
    if args.command == "iterate-simd4x8":
        output = args.output or Path("runs") / f"autonomous-simd4x8-{datetime.now().strftime('%Y%m%dT%H%M%S')}"
        return run_autonomous_simd4x8_iteration(
            args.request, output, model=args.model, seed=args.seed, patch_source=args.patch_source
        )
    if args.command == "campaign-simd4x8":
        output = args.output or Path("runs") / f"campaign-simd4x8-{datetime.now().strftime('%Y%m%dT%H%M%S')}"
        try:
            return run_simd4x8_campaign(
                args.request, output, attempts=args.attempts, model=args.model, seed=args.seed,
                patch_source=args.patch_source,
            )
        except ValueError as error:
            print(f"campaign configuration invalid: {error}")
            return 2
    if args.command == "collect-patch-feedback":
        try:
            summary = collect_patch_feedback(args.sources, args.output)
        except ValueError as error:
            print(f"feedback collection failed: {error}")
            return 2
        print(f"feedback dataset written: {summary['output']} ({summary['records_written']} records)")
        return 0
    if args.command == "check-circuit-dataset":
        try:
            summary = validate_circuit_dataset(args.path)
        except ValueError as error:
            print(f"circuit dataset invalid: {error}")
            return 2
        print(f"circuit dataset valid: {summary['records']} records across {summary['families']} families")
        return 0
    if args.command == "export-circuit-sft":
        try:
            summary = export_circuit_sft(args.source, args.output)
        except ValueError as error:
            print(f"circuit SFT export failed: {error}")
            return 2
        print(f"circuit SFT dataset written: {summary['output']} ({summary['examples_exported']} examples)")
        return 0
    if args.command == "build-internal-circuit-corpus":
        try:
            summary = build_internal_circuit_corpus(args.output)
        except (OSError, ValueError) as error:
            print(f"internal circuit corpus build failed: {error}")
            return 2
        print(f"internal circuit corpus written: {summary['output']} ({summary['records']} records)")
        return 0
    if args.command == "evaluate-patch-models":
        try:
            return evaluate_patch_models(args.proposal, args.output, models=args.models, seed=args.seed)
        except ValueError as error:
            print(f"patch evaluation configuration invalid: {error}")
            return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
