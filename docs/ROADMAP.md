# Roadmap

## Fase 0 — Fundação

- Estrutura de repositório, política de segurança e documentação.
- Seleção de um PDK aberto/licenciado e ambiente fixado.
- Design de referência pequeno com teste e baseline de PPA.

## Fase 1 — Fluxo verificável

- Orquestrador para lint, simulação, Yosys e OpenROAD.
- Manifestos e armazenamento de relatórios por execução.
- Portas de qualidade que bloqueiam resultados funcionais inválidos.

## Fase 2 — Assistente de projeto

- Esquemas versionados de solicitação e proposta LLM, com validação estrutural.
- Perfil local de fumaça e baseline de avaliação separados.
- Recuperação de documentação e exemplos licenciados.
- Geração assistida de RTL/testes para blocos pequenos.
- Ciclo fechado de proposta → verificação → PPA válido → feedback estruturado,
  com orçamento de tentativas e aprovação humana.

## Fase 3 — Aprendizado com feedback

- Dataset curado de propostas e evidências de verificação.
- Avaliação congelada, reprodução de baselines e comparação de modelos.
- Busca controlada de variantes sob orçamento de ferramentas.

## Fase 4 — Blocos de GPU

- ALU, registradores, scheduler simples e unidades de memória como benchmarks incrementais.
- Integração somente após contratos, cobertura e resultados físicos estáveis por bloco.
- Baseline funcional inicial: `vreg8x64`, banco vetorial com duas leituras, uma
  escrita e `r0` imutável; ainda sem PPA ou integração à VMAC.
- `vpu16_decode`: codifica `VMAC`, `VLOAD` e `VSTORE` para computação e memória
  vetorial local.
- Integração inicial: `mini_gpu_vmac_core` executa VMAC e transferências entre
  registradores vetoriais e a scratchpad local; fetch e PC continuam fora deste
  primeiro núcleo.
- Configuração iterativa da integração: `USE_ITERATIVE=1` introduz dez ciclos
  de ocupação por VMAC e estabelece a porta de entrada para um scheduler.
- Scheduler inicial: `ENABLE_QUEUE=1` retém uma instrução VMAC enquanto a
  unidade iterativa trabalha e a inicia depois do write-back.
- `scratchpad16x64`: memória local de 16 palavras vetoriais de 64 bits,
  integrada por VLOAD/VSTORE. A próxima etapa é definir dependências e hazards
  de memória para além do protocolo `issue_ready`/`issue_accepted`, que evita
  o aceite de operações durante `busy`.
