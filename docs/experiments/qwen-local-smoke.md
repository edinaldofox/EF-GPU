# Smoke test local — Qwen2.5-Coder 1.5B

Data: 2026-09-22. Backend: Ollama 0.18.2 local. Modelo:
`qwen2.5-coder:1.5b-instruct`, digest
`d7372fd828518a4d38b1eb196c673c31a85f2ed302b3d1e406c4c2d1b64a0668`, Q4_K_M,
1,5B parâmetros e 986 MB no armazenamento.

## Objetivo

Verificar a integração entre uma LLM local e o contrato de propostas do
EF-GPU, sem alterar RTL ou executar ferramentas EDA a partir de texto da LLM.

## Configuração

- Temperatura: `0`
- Seed: `42`
- Contexto: `1024` tokens
- Limite de resposta: `256` tokens
- Hardware observado: NVIDIA T400, 4 GB de VRAM

## Resultado

A chamada inicial de formato JSON funcionou. As duas primeiras propostas de
planejamento foram rejeitadas/consideradas fracas: repetiam a baseline ou
contradiziam a regra de interface. Depois de restringir a tarefa a uma melhoria
no testbench, a proposta validada pediu um caso adicional em
`designs/simd4x8/tb/tb_simd4x8_c_ref.sv`, declarou preservação de interface e
indicou a regressão C+RTL.

Conclusão: o modelo é adequado como ponto de partida para experimentar
contratos e recuperação curta, mas ainda não recebe permissão para alterar RTL.
O próximo incremento técnico é gerar patches em um worktree isolado e só então
executar as portas automáticas sobre esse candidato.
