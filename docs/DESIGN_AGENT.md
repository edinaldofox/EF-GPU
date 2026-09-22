# Agente de projeto de chips / Chip design agent

## Português

### Propósito

O agente transforma uma solicitação de circuito em uma **proposta** rastreável;
ele não é uma autoridade de projeto. A proposta somente é aceita após evidência
gerada por ferramentas determinísticas. O primeiro escopo são blocos pequenos e
independentes — por exemplo ALU, registrador, FIFO, multiplicador ou uma lane
SIMD — e não uma GPU completa.

### Ciclo de execução

```text
Especificação em linguagem natural
              ↓ normalização e aprovação humana
Solicitação JSON (design request)
              ↓ RAG com fontes licenciadas
LLM de RTL/arquitetura
              ↓
RTL + testbench + SDC + proposta JSON
              ↓ portas obrigatórias
lint → simulação → formal (quando disponível)
              ↓ somente se aprovado
Yosys → OpenROAD
              ↓
área, timing, potência estimada, DRC e manifesto
              ↓
feedback estruturado → próxima proposta sob orçamento
```

Não existe seta que leve diretamente da LLM ao GDSII aceito. Falha de contrato,
compilação, teste ou formal torna a tentativa inválida; métricas de PPA dessa
tentativa não entram na comparação.

### Contratos e uso

1. Crie e revise uma solicitação conforme
   [`schemas/design-request.schema.json`](../schemas/design-request.schema.json).
2. Verifique-a: `ef-gpu check-request arquivo.json`.
3. Recupere apenas documentos, RTL e relatórios com origem e licença registrados.
4. Peça à LLM uma proposta no formato
   [`schemas/design-proposal.schema.json`](../schemas/design-proposal.schema.json).
5. Valide: `ef-gpu check-proposal proposta.json`; então execute as portas EDA.
6. Salve um manifesto por tentativa contendo commit, modelo/revisão, seed,
   parâmetros, contexto, ferramentas, PDK, comandos e resultados.

Os exemplos em [`examples/agent/`](../examples/agent/) são contratos de formato,
não resultados de benchmark.

### Execução automatizada atual

O primeiro pipeline implementado é o da VMAC SIMD4x8:

```bash
ef-gpu run-simd4x8 examples/agent/simd4x8-request.json \
  examples/agent/simd4x8-baseline-proposal.json
```

Ele rejeita contratos inválidos, artefatos ausentes e árvore Git suja por padrão;
depois executa C+RTL e Yosys. `--physical` acrescenta OpenROAD somente após essas
duas portas. Todo resultado é escrito em `runs/<id>/`, ignorado pelo Git, com
`manifest.json` e um log por etapa. O estado `functional-valid` não é uma
aprovação física; `physical-valid` tampouco é sign-off.

Para gerar uma proposta de planejamento local com o Qwen instalado, use:

```bash
ef-gpu propose-simd4x8 examples/agent/simd4x8-request.json
```

Esta primeira integração pede apenas `changes` e `assumptions` em JSON e o
EF-GPU preenche e valida o contrato completo. Ela **não aplica RTL gerado** nem
executa o pipeline automaticamente; uma proposta só pode seguir quando seus
artefatos e alterações estiverem em um candidato versionado.

O candidato atual é aplicado somente em um worktree Git descartável. Para testar
um patch de testbench sem tocar a árvore principal:

```bash
ef-gpu stage-simd4x8 examples/agent/simd4x8-request.json \
  PROPOSTA.json examples/agent/patches/simd4x8-testbench-message.patch
```

Nesta primeira versão, apenas `designs/simd4x8/tb/tb_simd4x8_c_ref.sv` pode ser
alterado. O worktree temporário é removido ao final; logs e manifesto permanecem
em `runs/`.

O Qwen pode gerar esse diff restrito em um arquivo de execução:

```bash
ef-gpu draft-simd4x8-patch PROPOSTA.json
```

O comando aceita somente um patch que passe `git apply --check`, mude o único
arquivo permitido **e contenha exatamente** a substituição de mensagem pedida.
Ele inclui o fonte atual no prompt, mas essa resposta continua não confiável:
qualquer linha extra ou substituição diferente é salva como rejeitada. Para
Para toda resposta do modelo, o arquivo vizinho `.patch.meta.json` registra
prompt, hashes das entradas e resposta, versão/seed do modelo e o resultado das
portas do patch. Em seguida, use `stage-simd4x8` para a verificação isolada.

### Portas de qualidade e segurança

| Etapa | Condição para avançar | Saída de feedback |
| --- | --- | --- |
| Solicitação | Interface, clock e critérios de aceitação aprovados | erros de contrato |
| Proposta | Artefatos declarados, commit e modelo rastreáveis | campos ausentes/hipóteses |
| Funcional | lint e simulação aprovados; formal quando exigido | falhas reproduzíveis |
| Física | somente candidato funcional; configuração OpenROAD versionada | área, timing, DRC, potência estimada |
| Aceitação | revisão humana e comparação justa com baseline | decisão e justificativa |

O agente não pode baixar PDK/IP, publicar GDS, alterar interfaces, elevar
restrições ou substituir a baseline sem aprovação humana explícita. Um relatório
de potência é estimativa até existir um fluxo de sign-off apropriado.

### Dados e aprendizagem

Começamos por RAG e contratos, não por treinamento do zero. Colete somente RTL,
testes, documentação e resultados cuja licença permita o uso pretendido. Separe
por famílias de designs antes de treino/validação/benchmark, para evitar
vazamento. Depois de acumular propostas com verificações aprovadas e reprovadas,
um LoRA pode ser avaliado em tarefas estreitas: produzir testbenches, explicar
relatórios ou sugerir variantes de um bloco já especificado.

### Modelo inicial

Use o perfil `local_smoke` de
[`configs/models/qwen2.5-coder.json`](../configs/models/qwen2.5-coder.json) para
desenvolver prompts e a integração local. A máquina atual tem GPU de 4 GB, por
isso ele limita contexto e usa um modelo de 1,5 B quantizado; não é uma medida
de capacidade para criar RTL. O perfil `evaluation_baseline` usa 3 B e serve
para comparações reproduzíveis quando houver memória suficiente ou um serviço
aprovado. Antes da primeira execução, fixe a revisão do peso e registre-a no
manifesto; pesos não são parte deste repositório.

## English

### Purpose

The agent turns a circuit request into a traceable **proposal**; it is not a
design authority. A proposal is accepted only after evidence from deterministic
tools. The initial scope is small independent blocks — e.g. an ALU, register,
FIFO, multiplier, or SIMD lane — rather than a complete GPU.

### Execution loop

```text
Natural-language specification
              ↓ normalization and human approval
JSON design request
              ↓ RAG over licensed sources
RTL/architecture LLM
              ↓
RTL + testbench + SDC + JSON proposal
              ↓ required gates
lint → simulation → formal (when available)
              ↓ only when passing
Yosys → OpenROAD
              ↓
area, timing, estimated power, DRC, and manifest
              ↓
structured feedback → next proposal within budget
```

There is no direct path from the LLM to an accepted GDSII. A contract,
compilation, test, or formal failure invalidates the attempt, and its PPA metrics
are excluded from comparisons.

### Contracts and use

1. Create and review a request using
   [`schemas/design-request.schema.json`](../schemas/design-request.schema.json).
2. Check it with `ef-gpu check-request file.json`.
3. Retrieve only documentation, RTL, and reports with recorded provenance and
   license.
4. Ask the LLM for a proposal using
   [`schemas/design-proposal.schema.json`](../schemas/design-proposal.schema.json).
5. Run `ef-gpu check-proposal proposal.json`, then the EDA gates.
6. Save one manifest per attempt with commit, model/revision, seed, generation
   parameters, context, tools, PDK, commands, and results.

The examples in [`examples/agent/`](../examples/agent/) define formats, not
benchmark results.

### Current automated execution

The first implemented pipeline is the SIMD4x8 VMAC:

```bash
ef-gpu run-simd4x8 examples/agent/simd4x8-request.json \
  examples/agent/simd4x8-baseline-proposal.json
```

It rejects invalid contracts, missing artifacts, and a dirty Git tree by default,
then runs C+RTL and Yosys. `--physical` adds OpenROAD only after both gates. Each
result is written to a Git-ignored `runs/<id>/` directory with `manifest.json`
and one log per stage. `functional-valid` is not physical approval;
`physical-valid` is not sign-off.

To generate a local planning proposal with the installed Qwen model, run:

```bash
ef-gpu propose-simd4x8 examples/agent/simd4x8-request.json
```

This first integration asks only for JSON `changes` and `assumptions`, then
EF-GPU fills and validates the complete contract. It **does not apply generated
RTL** or run the pipeline automatically; a proposal advances only after its
artifacts and changes exist in a versioned candidate.

The current candidate is applied only in a disposable Git worktree. To test a
testbench patch without touching the main worktree:

```bash
ef-gpu stage-simd4x8 examples/agent/simd4x8-request.json \
  PROPOSAL.json examples/agent/patches/simd4x8-testbench-message.patch
```

In this first version, only `designs/simd4x8/tb/tb_simd4x8_c_ref.sv` may change.
The temporary worktree is removed afterwards; logs and the manifest remain under
`runs/`.

The Qwen can draft this restricted diff into a run file:

```bash
ef-gpu draft-simd4x8-patch PROPOSAL.json
```

The command accepts only a patch that passes `git apply --check`, changes the
one allowed file, **and contains exactly** the requested message replacement.
It supplies the current source in the prompt, but the response remains
untrusted: any extra line or different replacement is saved as rejected. For
every model response, the neighboring `.patch.meta.json` records the prompt,
input and response hashes, model version/seed, and patch-gate outcome. Then use
`stage-simd4x8` for isolated verification.

### Quality gates and safety

| Stage | Condition to advance | Feedback output |
| --- | --- | --- |
| Request | Approved interface, clock, and acceptance criteria | contract errors |
| Proposal | Declared artifacts, traceable commit and model | missing fields/assumptions |
| Functional | Passing lint and simulation; formal when required | reproducible failures |
| Physical | Functional candidate only; versioned OpenROAD config | area, timing, DRC, estimated power |
| Acceptance | Human review and fair baseline comparison | decision and rationale |

The agent may not download PDK/IP, publish GDS, change interfaces, relax
constraints, or replace a baseline without explicit human approval. A power
report remains an estimate until an appropriate sign-off flow exists.

### Data and learning

Start with RAG and contracts, not training from scratch. Collect only RTL,
tests, documentation, and results whose licenses allow the intended use. Split
design families before training/validation/benchmarking to prevent leakage. Once
the project has accumulated verified passing and failing proposals, a LoRA can
be evaluated for narrow tasks: producing testbenches, explaining reports, or
suggesting variants of an already specified block.

### Initial model

Use the `local_smoke` profile in
[`configs/models/qwen2.5-coder.json`](../configs/models/qwen2.5-coder.json) to
develop prompts and local integration. The current machine has a 4 GB GPU, so
it limits context and uses a quantized 1.5B model; it is not a measure of RTL
generation capability. `evaluation_baseline` uses 3B and is intended for
reproducible comparisons after sufficient memory or an approved service is
available. Pin the weight revision and record it in the manifest before the
first run; model weights are not stored in this repository.
