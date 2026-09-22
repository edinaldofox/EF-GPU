# Sprint 1 — núcleo executável e corpus v2

## Objetivo

Consolidar uma cadeia segura de programa vetorial executável e ampliar o corpus
interno sem baixar dados, pesos ou IP externo.

## Backlog seguro

- [x] Definir sequência obrigatória e portas de bloqueio.
- [x] Adicionar `vpu16_sequencer` e executar VLOAD→VMAC→VSTORE integrado.
- [x] Reexecutar simulação e síntese dos blocos que fundamentam o corpus.
- [x] Preservar o corpus v1 como benchmark/seed versionado.
- [x] Materializar corpus interno v2, incluindo a família `vpu16_sequencer`.
- [x] Validar split, hashes de fonte e exportação SFT sem benchmarks.
- [x] Publicar manifesto, documentação e commit da entrega.

## Limites da sprint

Esta sprint não baixa corpus externo, pesos, PDK/IP, não treina LoRA e não faz
tape-out. Esses itens exigem autorização e entram no planejamento da Sprint 2.
