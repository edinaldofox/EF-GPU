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
4. Comece por um design pequeno e verificável em `designs/examples/`; não use uma LLM para gerar blocos de GPU complexos antes de estabelecer os testes e as métricas de referência.

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
4. Begin with a small, verifiable design in `designs/examples/`; do not use an LLM to generate complex GPU blocks before baseline tests and metrics exist.

The first reference design is [ALU8](designs/alu8/spec.md). Exhaustively verify its combinational core with `./scripts/verify-alu8.sh`.

### Principles

- **Verification before PPA:** functional correctness is required before comparing power, performance, and area (PPA).
- **Reproducibility:** PDK/tool versions, seeds, and prompts are part of the result.
- **Human in control:** the LLM proposes; a person approves interface, configuration, and tape-out changes.
- **Licensed data:** datasets, PDKs, and IP must record provenance and compatible licensing.

Read [AGENTS.md](AGENTS.md) before automated changes and [the roadmap](docs/ROADMAP.md) for milestones.
