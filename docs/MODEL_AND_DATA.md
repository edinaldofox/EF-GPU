# Modelo e dados

## Estratégia de LLM

O modelo será desenvolvido em etapas: primeiro assistência baseada em recuperação de exemplos e regras; depois ajuste supervisionado em pares especificação→RTL/teste; por fim, otimização por feedback de verificadores e métricas físicas válidas.

### Especialização nativa de SystemVerilog

O Qwen local não recebe especialização nativa apenas por prompts. Para alterar
os pesos de modo rastreável, o repositório oferece `check-circuit-dataset` e
`export-circuit-sft`: eles exigem exemplos revisados, licenciados, com simulação
RTL e síntese aprovadas, separam famílias de design entre splits e excluem o
benchmark congelado da saída de treino. Consulte
[Especialização nativa para circuitos](CIRCUIT_SPECIALIZATION.md). A configuração
em `configs/models/circuit-specialization.json` é somente um plano de QLoRA; não
representa adapter treinado nem autoriza download ou publicação de pesos.

O corpus interno v1, em `datasets/circuit/ef-gpu-internal-v1.jsonl`, materializa
seis famílias verificadas com duas em treino, duas em validação e duas em
benchmark. É uma semente de formato e rastreabilidade, não um corpus com volume
suficiente para iniciar LoRA.

### Ponto de partida

O perfil inicial está em
[`configs/models/qwen2.5-coder.json`](../configs/models/qwen2.5-coder.json).
Ele separa dois usos deliberadamente:

- **Smoke/local:** `Qwen/Qwen2.5-Coder-1.5B-Instruct` quantizado em 4 bits,
  contexto curto e sem ajuste fino. É o perfil de experimentação para a GPU de
  4 GB atualmente detectada; o desempenho não deve ser usado como referência de
  qualidade de RTL.
- **Baseline de avaliação:** `Qwen/Qwen2.5-Coder-3B-Instruct`, com os mesmos
  prompts e contratos. Ele é o primeiro candidato local em Q4_K_M, com contexto
  limitado a 1.536 tokens na GPU atual.

A família Qwen2.5-Coder disponibiliza variantes instruct de 1,5 B e 3 B, com
janela de 32k. A licença é específica por peso: o 1,5B instalado é Apache-2.0;
o 3B instalado está sob Qwen Research License e só pode ser usado em pesquisa e
avaliação não comercial. As fontes são o
[repositório do modelo de 3B](https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct)
e a [lista oficial da família](https://github.com/QwenLM/Qwen2.5-Coder).
O projeto não baixa nem executa pesos automaticamente: isso exige escolha do
backend, revisão de licença e orçamento de disco/memória.

### Execução local registrada

Com autorização do mantenedor, o perfil local foi baixado via Ollama em
2026-09-22 como `qwen2.5-coder:1.5b-instruct`, digest
`d7372fd828518a4d38b1eb196c673c31a85f2ed302b3d1e406c4c2d1b64a0668` (Q4_K_M,
986 MB). O primeiro smoke test usou contexto de 1024, temperatura zero, seed 42
e gerou uma proposta estruturalmente válida de melhoria do testbench. Isso
valida a integração Ollama→contrato; não mede capacidade de gerar RTL nem PPA.

O comando `ef-gpu propose-simd4x8` nunca aplica a saída da LLM. Ele registra a
proposta e as métricas da resposta em `runs/`, e rejeita planos que mudem a
interface, criem módulos/arquivos ou não indiquem a regressão C+RTL.

Modelos maiores, como Qwen3-Coder, podem ser comparados depois, mas não são a
baseline inicial: o objetivo desta fase é validar o ciclo EDA, não maximizar a
capacidade do modelo.

### Coleta de feedback

O comando abaixo converte metadados de patch em JSONL deduplicado. Cada registro
contém prompt, resposta, hashes, versão/licença do modelo, portas de validação e
rótulo `accepted` ou `rejected`:

```bash
ef-gpu collect-patch-feedback runs/ --output runs/feedback/patches.jsonl
```

Ele não treina nem publica um modelo. A coleção preserva respostas rejeitadas
porque elas são sinais de preferência/erro; duplicatas de mesma resposta são
removidas. Antes de qualquer LoRA, é obrigatório revisar licenças, remover dados
indevidos, congelar a divisão treino/validação/benchmark e aprovar o uso.

Patches emitidos por templates determinísticos são referência de processo, não
aceitações da LLM. Eles podem registrar uma execução positiva de simulação e
síntese, mas devem manter `source: deterministic-template` e ficar separados de
exemplos de treinamento ou métricas de capacidade do modelo.

### Avaliação de fumaça comparável

Para comparar os perfis instalados na mesma tarefa mínima de patch, execute:

```bash
ef-gpu evaluate-patch-models PROPOSTA.json --output runs/evaluation/patch-smoke
```

O comando usa o mesmo prompt, seed e portas para cada modelo fixado e salva um
manifesto por resultado. Ele não altera o repositório e não é um benchmark de
qualidade de RTL: uma tarefa de testbench não mede capacidade de projetar uma
GPU. O conjunto de benchmark real deve ser congelado e mantido fora de treino.

## Requisitos para dados

- Registrar origem, licença, versão e transformação de cada item.
- Separar treino, validação e benchmark por família de design para evitar vazamento.
- Incluir RTL, testes, resultados de simulação e relatórios EDA quando a licença permitir.
- Remover segredos, PDKs não redistribuíveis e IP proprietário.
- Tratar resultados de ferramenta como evidência contextual, não como verdade universal.

## Avaliação

A avaliação deve medir: taxa de compilação, taxa de testes aprovados, equivalência/formal quando disponível, PPA somente entre candidatos válidos, custo de execução e taxa de intervenção humana. O conjunto de benchmark deve ficar congelado e versionado antes de comparar modelos.

Cada execução também registra: identificador e revisão do modelo, método de
quantização, backend, parâmetros de geração, seed, contexto recuperado, commit,
versões das ferramentas, PDK e orçamento de tentativas. Um benchmark não pode
ser reutilizado no ajuste fino.
