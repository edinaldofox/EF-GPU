# Especialização nativa para circuitos / Native circuit specialization

## Português

Uma LLM torna-se especializada nativamente em circuitos somente quando seus
**pesos são adaptados** com exemplos de hardware. Prompt, RAG e templates
melhoram o uso de um modelo geral, mas não alteram seus pesos. A EF-GPU agora
define a etapa de dados necessária para um futuro adapter LoRA/QLoRA, sem
alegar que o checkpoint já exista.

```text
RTL/testes licenciados e revisados
              ↓
JSONL por família, licença e resultado de verificação
              ↓
check-circuit-dataset ── separa train/validation/benchmark
              ↓
export-circuit-sft ── JSONL de chat, sem benchmark
              ↓
treino LoRA aprovado e reproduzível
              ↓
avaliação congelada → simulação → síntese → agente restrito
```

### Contrato do corpus

Cada linha JSONL contém `id`, `split`, `design_family`, tarefa, especificação,
SystemVerilog alvo, proveniência e evidências. O validador exige:

- `rtl_simulation=passed` e `synthesis=passed`;
- licença declarada e `reviewed=true`;
- IDs únicos;
- uma família de design em apenas um split, evitando vazamento entre treino,
  validação e benchmark;
- benchmark excluído da exportação de treino.

Valide um corpus e produza a entrada de SFT:

```bash
ef-gpu check-circuit-dataset examples/training/circuit-sft-sample.jsonl
ef-gpu export-circuit-sft examples/training/circuit-sft-sample.jsonl \
  --output runs/training/circuit-sft.jsonl
```

O arquivo de exemplo é somente uma demonstração de formato; uma linha não cria
capacidade de projeto. O perfil para o primeiro experimento está em
[`configs/models/circuit-specialization.json`](../configs/models/circuit-specialization.json).
Ele fixa o método proposto (QLoRA), mas não baixa pesos, não inicia treino, não
publica adapter e não substitui a avaliação.

### Critério para chamar o modelo de especializado

O nome `EF-GPU-Circuit-LoRA` só poderá ser usado depois de registrar, no mínimo:

1. revisão e licença do modelo base, corpus e transformações;
2. hiperparâmetros, seed, hardware e hash do adapter;
3. benchmark congelado por famílias ausentes do treino;
4. comparação contra o Qwen base em compilação, simulação e síntese;
5. revisão humana dos resultados e dos limites de uso.

Mesmo então, o adapter é um gerador não confiável: o agente continua limitado
por contratos, worktrees descartáveis e portas EDA.

## English

An LLM becomes natively specialized for circuits only when its **weights are
adapted** on hardware examples. Prompts, RAG, and templates improve the use of
a general model, but do not modify its weights. EF-GPU now defines the data
stage required for a future LoRA/QLoRA adapter without claiming that a
checkpoint already exists.

Each JSONL line records an ID, split, design family, task, specification, target
SystemVerilog, provenance, and verification evidence. The validator requires
passing RTL simulation and synthesis, declared reviewed licensing, unique IDs,
family-separated splits, and keeps frozen benchmark data out of training
exports.

The specialization name may only be used after the base revision, corpus,
transformations, hyperparameters, seed, hardware, adapter hash, frozen
benchmark comparison, and human review have been recorded. The adapter remains
untrusted and is still constrained by contracts, disposable worktrees, and EDA
gates.
