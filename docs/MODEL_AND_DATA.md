# Modelo e dados

## Estratégia de LLM

O modelo será desenvolvido em etapas: primeiro assistência baseada em recuperação de exemplos e regras; depois ajuste supervisionado em pares especificação→RTL/teste; por fim, otimização por feedback de verificadores e métricas físicas válidas.

### Ponto de partida

O perfil inicial está em
[`configs/models/qwen2.5-coder.json`](../configs/models/qwen2.5-coder.json).
Ele separa dois usos deliberadamente:

- **Smoke/local:** `Qwen/Qwen2.5-Coder-1.5B-Instruct` quantizado em 4 bits,
  contexto curto e sem ajuste fino. É o perfil de experimentação para a GPU de
  4 GB atualmente detectada; o desempenho não deve ser usado como referência de
  qualidade de RTL.
- **Baseline de avaliação:** `Qwen/Qwen2.5-Coder-3B-Instruct`, com os mesmos
  prompts e contratos. Ele é o primeiro candidato para uma máquina com memória
  suficiente, ou para inferência remota aprovada.

A família Qwen2.5-Coder disponibiliza variantes instruct de 1,5 B e 3 B, com
janela de 32k, e licença Apache-2.0. As fontes são o
[repositório do modelo de 3B](https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct)
e a [lista oficial da família](https://github.com/QwenLM/Qwen2.5-Coder).
O projeto não baixa nem executa pesos automaticamente: isso exige escolha do
backend, revisão de licença e orçamento de disco/memória.

Modelos maiores, como Qwen3-Coder, podem ser comparados depois, mas não são a
baseline inicial: o objetivo desta fase é validar o ciclo EDA, não maximizar a
capacidade do modelo.

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
