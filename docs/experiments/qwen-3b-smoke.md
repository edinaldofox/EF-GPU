# Smoke test local — Qwen2.5-Coder 3B

Date: 2026-09-22. Backend: local Ollama 0.18.2. Model:
`qwen2.5-coder:3b-instruct`, revision
`4a188102020e9c9530b687fd6400f775c45e90a0d7baafe65bd0a36963fbb7ba`, Q4_K_M,
3.1B parameters, and 1.9 GB on disk.

## Scope and license

This is an evaluation of a model-generated **testbench patch only**. The model
is governed by the Qwen Research License Agreement, which permits
non-commercial research/evaluation; it must not be used for commercial work
without a separate license.

## Configuration

- Temperature: `0`
- Seed: `42`
- Context: `1536` tokens
- Output limit: `256` tokens
- Observed hardware: NVIDIA T400, 4 GB VRAM

## Result

The model loaded with approximately 3.27 GB used VRAM, with a reported split
of 77% GPU / 23% CPU. The patch request took 28.5 seconds total (8.8 seconds
of load time). Its output began at a unified-diff hunk (`@@`) without the
required Git diff header, so `git apply --check` rejected it before any
worktree or EDA tool ran.

The run metadata, including prompt, response hash, model revision, and gate
outcome, is stored under `runs/qwen3b-patch-smoke.patch.meta.json` and is not
versioned. This is not a model-quality benchmark: one request is insufficient
to compare models. It confirms that the 3B profile is pinned, executable on the
current hardware, and constrained by the same safety gates as the 1.5B profile.
