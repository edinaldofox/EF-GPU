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
- `vpu16_decode`: codifica o primeiro formato de instrução (`VMAC`) e será
  integrado ao banco vetorial e à unidade SIMD somente após suas baselines.
