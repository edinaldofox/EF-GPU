# Sprints de treinamento da LLM

## Estado atual

O corpus v2 tem 7 exemplos: 3 treino, 2 validação e 2 benchmark. A revisão do
Qwen 1.5B ainda não está fixada para treino e não existe adapter. Portanto, o
projeto não está pronto nem autorizado para LoRA.

## Sprint 2 — qualidade e escala interna

**Objetivo:** ampliar somente com hardware EF-GPU, sem downloads nem pesos.

- Criar taxonomia: especificação→RTL, RTL→testbench, correção e relatórios.
- Implementar relatório de prontidão por exemplos, famílias, split, licença e
  evidência de verificação.
- Adicionar 12 famílias verificadas (FIFO, contador, mux, arbiter, shifter,
  comparador, decoder, controlador e similares).
- Gerar corpus v3 com no mínimo 20 famílias: 12 treino, 4 validação e 4
  benchmark; exportar SFT sem benchmark.

**Porta de saída:** `check-circuit-dataset` aprovado, hashes sem vazamento e
simulação/síntese para todas as famílias. Ainda não autoriza treino.

## Sprint 3 — fontes externas licenciadas

**Pré-requisito:** Sprint 2 concluída e autorização explícita para download.

- Criar registro de fontes com URL, commit fixado, licença, responsável e data
  de revisão.
- Revisar licença e conteúdo antes de baixar; usar apenas área temporária.
- Registrar hash, transformação e dependências de cada exemplo admitido.
- Congelar benchmark com famílias que nunca aparecem em treino.

**Porta de saída:** 100 exemplos de treino, 20 de validação, 20 de benchmark,
proveniência revisada e benchmark com checksum. Não autoriza pesos ainda.

## Sprint 4 — piloto QLoRA reproduzível

**Pré-requisito:** Sprints 2–3 e autorização explícita para modelo, GPU, disco
e criação de pesos.

- Fixar modelo base Apache-2.0, revisão, checksum e tokenizer.
- Fixar framework, CUDA, dataset, seed, hardware e hiperparâmetros em manifesto.
- Executar smoke de VRAM/disco e um único piloto com limite de passos.
- Guardar checkpoints apenas em diretório ignorado pelo Git; registrar perda,
  custo, hashes e falhas; não publicar o adapter.

**Porta de saída:** adapter reproduzível por manifesto, sem vazamento de
benchmark nem artefato de peso no Git. Perda de treino não é prova de RTL.

## Sprint 5 — avaliação base × adapter

**Pré-requisito:** adapter da Sprint 4 e ambiente EDA fixado.

- Executar prompts e orçamento idênticos para Qwen base e adapter.
- Medir JSON válido, compilação, simulação, síntese, custo e falhas de segurança.
- Auditar interfaces inventadas, resets/clocks inconsistentes e patches fora do
  escopo permitido.
- Publicar relatório por família com decisão explícita de promover ou rejeitar.

**Porta de saída:** adapter iguala ou supera o base nas portas funcionais sem
piorar segurança; revisão humana obrigatória.

## Sprint 6 — canário do agente especializado

**Pré-requisito:** Sprint 5 aprovada por revisão humana.

- Fixar adapter, backend, prompt, seed, contexto e orçamento de tentativas.
- Aceitar somente propostas JSON e templates/arquivos permitidos.
- Usar worktrees descartáveis e C+RTL+Yosys para toda tentativa.
- Definir rollback para regressão, custo excedido, licença inválida ou patch fora
  do escopo.

**Porta de saída:** canário rastreável e seguro; o adapter ainda não tem
autoridade para alterar interfaces, baixar PDK/IP ou publicar GDS.

## Regra transversal

Nenhuma sprint inicia automaticamente a seguinte. Sprints 3 e 4 requerem nova
autorização por envolverem downloads, recursos de hardware ou pesos.

