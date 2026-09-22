# EF-GPU internal circuit corpus v1

This directory contains the materialized, repository-authored seed corpus for
circuit specialization. `ef-gpu-internal-v1.jsonl` has six examples:

| Split | Families |
| --- | --- |
| Train | `alu8`, `simd4x8` |
| Validation | `vreg8x64`, `scratchpad16x64` |
| Frozen benchmark | `vpu16_decode`, `mini_gpu_vmac` |

Every row records Apache-2.0 provenance, source paths and SHA-256 hashes, a
reviewed specification, RTL, testbench, and passing simulation/synthesis
evidence. The generator rejects family or source-content leakage across splits.

Regenerate only into a new path, never over this versioned corpus:

```bash
ef-gpu build-internal-circuit-corpus \
  --output datasets/circuit/ef-gpu-internal-v2.jsonl
```

The v1 seed is intentionally too small for LoRA training. It establishes the
format and frozen benchmark discipline while the project curates more licensed,
verified design families.

`ef-gpu-internal-v2.jsonl` adds `vpu16_sequencer` to the training split while
keeping v1 unchanged. It has seven families: three train, two validation, and
two frozen benchmark families. It remains a seed corpus, not training volume.
