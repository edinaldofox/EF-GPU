# EF-GPU

[Português](#português) · [English](#english)

## Português

**EF-GPU** é uma plataforma de pesquisa para projetar circuitos e blocos de GPU com uma LLM especializada, mantendo a execução física verificável no fluxo aberto do [OpenROAD](https://theopenroadproject.org/).

O objetivo não é aceitar um layout gerado pela IA sem verificação. A LLM propõe especificações, microarquitetura, RTL e restrições; ferramentas determinísticas então simulam, sintetizam e realizam o fluxo físico. Cada resultado precisa produzir artefatos, métricas e rastreabilidade para revisão humana.

### Visão do fluxo

```text
Requisito → LLM de projeto → RTL + SDC + configuração
                              ↓
                  lint/simulação/verificação formal
                              ↓
                 Yosys → OpenROAD → GDSII/relatórios
                              ↓
                  métricas e feedback para a LLM
```

O fluxo completo, os contratos de entrada/saída e as portas de qualidade estão em
[Agente de projeto](docs/DESIGN_AGENT.md). As especificações e propostas usam
JSON versionado em [`schemas/`](schemas/), para que o agente seja integrado ao
fluxo de desenvolvimento, e não tratado como uma caixa-preta.

O modelo local atual é um ponto de partida de código, ainda **não** um modelo
com pesos especializados em circuitos. A trilha para um adapter LoRA/QLoRA de
SystemVerilog — com corpus licenciado, avaliação congelada e validação de dados
— está em [Especialização nativa para circuitos](docs/CIRCUIT_SPECIALIZATION.md).
A ordem obrigatória para hardware, corpus, treinamento e fluxo físico está em
[Sequência de processos](docs/PROCESS_SEQUENCE.md).
As sprints planejadas para levar o corpus ao treinamento e avaliação estão em
[Sprints de treinamento](docs/TRAINING_SPRINTS.md).

### Estrutura inicial

```text
configs/openroad/     Configurações e presets do fluxo físico
designs/              Designs de referência e entradas de benchmark
docs/                 Arquitetura, dados, OpenROAD e roadmap
src/ef_gpu/           Orquestrador Python (em evolução)
tests/                Testes do orquestrador e das validações
```

### Começar

1. Instale Python 3.11+ e as ferramentas EDA necessárias ao experimento (OpenROAD, Yosys e um simulador).
2. Crie um ambiente local e instale o projeto: `python -m pip install -e '.[dev]'`.
3. Leia [a arquitetura](docs/ARCHITECTURE.md) e [o guia do OpenROAD](docs/OPENROAD.md).
4. Valide os contratos de exemplo com `ef-gpu check-request examples/agent/alu8-request.json` e `ef-gpu check-proposal examples/agent/alu8-proposal.json`.
5. Comece por um design pequeno e verificável em `designs/examples/`; não use uma LLM para gerar blocos de GPU complexos antes de estabelecer os testes e as métricas de referência.

Para executar uma iteração automática da baseline SIMD4x8 e registrar seus logs
em `runs/`, use:

```bash
ef-gpu run-simd4x8 examples/agent/simd4x8-request.json \
  examples/agent/simd4x8-baseline-proposal.json
```

Acrescente `--physical` para solicitar OpenROAD depois das portas funcionais.

O primeiro design de referência é a [ALU8](designs/alu8/spec.md). Verifique exaustivamente o núcleo combinacional com `./scripts/verify-alu8.sh`.

### Princípios

- **Verificação antes de PPA:** corretude funcional é requisito para comparar potência, desempenho e área (PPA).
- **Reprodutibilidade:** versões de PDK, ferramentas, sementes e prompts pertencem aos resultados.
- **Humano no controle:** a LLM sugere; uma pessoa aprova alterações de interface, configuração e tape-out.
- **Dados licenciados:** datasets, PDKs e IP devem registrar procedência e licença compatível.

Consulte [AGENTS.md](AGENTS.md) antes de qualquer alteração automatizada e [o roadmap](docs/ROADMAP.md) para os marcos.

---

## English

**EF-GPU** is a research platform for designing GPU circuits and blocks with a specialised LLM while keeping physical implementation verifiable through the open [OpenROAD](https://theopenroadproject.org/) flow.

The goal is not to accept an AI-generated layout without validation. The LLM proposes specifications, microarchitecture, RTL, and constraints; deterministic tools then simulate, synthesize, and implement the physical flow. Every result must provide artifacts, metrics, and provenance for human review.

### Flow overview

```text
Requirement → Design LLM → RTL + SDC + configuration
                               ↓
                   lint/simulation/formal verification
                               ↓
                  Yosys → OpenROAD → GDSII/reports
                               ↓
                    metrics and feedback to the LLM
```

The full workflow, input/output contracts, and quality gates are described in
[Design agent](docs/DESIGN_AGENT.md). Specifications and proposals use
versioned JSON in [`schemas/`](schemas/), so the agent is part of the
development flow rather than a black box.

The current local model is a code-model starting point, **not yet** a model with
circuit-specialized weights. The path toward a SystemVerilog LoRA/QLoRA adapter
with licensed corpus, frozen evaluation, and data validation is documented in
[Native circuit specialization](docs/CIRCUIT_SPECIALIZATION.md).
The required order for hardware, corpus, training, and physical flow is in
[Process sequence](docs/PROCESS_SEQUENCE.md).
The planned sprints that take the corpus through training and evaluation are in
[Training sprints](docs/TRAINING_SPRINTS.md).

### Initial layout

```text
configs/openroad/     Physical-flow configurations and presets
designs/              Reference designs and benchmark inputs
docs/                 Architecture, data, OpenROAD, and roadmap
src/ef_gpu/           Python orchestrator (under development)
tests/                Orchestrator and validation tests
```

### Getting started

1. Install Python 3.11+ and the EDA tools needed by your experiment (OpenROAD, Yosys, and a simulator).
2. Create a local environment and install the project: `python -m pip install -e '.[dev]'`.
3. Read the [architecture](docs/ARCHITECTURE.md) and [OpenROAD guide](docs/OPENROAD.md).
4. Validate the example contracts with `ef-gpu check-request examples/agent/alu8-request.json` and `ef-gpu check-proposal examples/agent/alu8-proposal.json`.
5. Begin with a small, verifiable design in `designs/examples/`; do not use an LLM to generate complex GPU blocks before baseline tests and metrics exist.

To run an automated SIMD4x8 baseline iteration and save logs under `runs/`, use:

```bash
ef-gpu run-simd4x8 examples/agent/simd4x8-request.json \
  examples/agent/simd4x8-baseline-proposal.json
```

Add `--physical` to request OpenROAD after the functional gates.

The first reference design is [ALU8](designs/alu8/spec.md). Exhaustively verify its combinational core with `./scripts/verify-alu8.sh`.

### Principles

- **Verification before PPA:** functional correctness is required before comparing power, performance, and area (PPA).
- **Reproducibility:** PDK/tool versions, seeds, and prompts are part of the result.
- **Human in control:** the LLM proposes; a person approves interface, configuration, and tape-out changes.
- **Licensed data:** datasets, PDKs, and IP must record provenance and compatible licensing.

Read [AGENTS.md](AGENTS.md) before automated changes and [the roadmap](docs/ROADMAP.md) for milestones.
