# Sequência obrigatória do EF-GPU / Required EF-GPU process sequence

## Português

Esta é a ordem obrigatória para evoluir hardware, dados e modelos no EF-GPU.
Uma etapa só começa quando a anterior tiver os artefatos exigidos. Falhas não
avançam; elas geram evidência, correção ou encerramento da tentativa.

```text
0. Escopo e licença
        ↓
1. Especificação e contrato
        ↓
2. Modelo de referência + testes
        ↓
3. RTL pequeno e versionado
        ↓
4. Simulação / formal / síntese
        ↓
5. Integração in-order e programa de sistema
        ↓
6. Admissão no corpus
        ↓
7. Treino LoRA aprovado
        ↓
8. Avaliação congelada + agente restrito
        ↓
9. Fluxo físico OpenROAD
        ↓
10. Revisão humana e decisão de release
```

| Etapa | Processo | Saída obrigatória | Porta para avançar |
| --- | --- | --- | --- |
| 0 | Confirmar objetivo, fontes, licença e autorização. | Escopo e proveniência. | Sem IP/PDK proprietário, pesos ou credenciais sem autorização. |
| 1 | Escrever especificação, interface, reset, clocks, latência e critérios. | `spec.md` e, para agente, JSON em `schemas/`. | Contrato revisado e sem ambiguidade. |
| 2 | Criar modelo C quando aplicável e testbench determinístico. | Casos normais, borda e falha esperada. | Modelo e testes concordam com a especificação. |
| 3 | Implementar um bloco pequeno com mudança Git focada. | RTL, documentação e scripts. | Interface e riscos de compatibilidade documentados. |
| 4 | Executar lint, simulação, formal quando disponível e Yosys. | Logs/manifests e resultado reproduzível. | Todos os testes passam; não alegar PPA físico. |
| 5 | Integrar somente blocos aprovados usando handshake explícito. | Teste de integração e programa VPU16. | Sem perda silenciosa de comandos, hazards documentados. |
| 6 | Registrar exemplo no corpus com hashes e split por família. | JSONL validado e manifesto. | Licença, revisão, simulação e síntese aprovadas; sem vazamento de conteúdo. |
| 7 | Preparar LoRA/QLoRA apenas após corpus suficiente. | Revisão do peso base, hiperparâmetros, seed e adapter hash. | Aprovação explícita para treino e uso de hardware. |
| 8 | Comparar modelo base e adapter em benchmark congelado. | Taxas de compilação/teste/síntese e custo. | Adapter não piora portas críticas e continua não confiável. |
| 9 | Executar OpenROAD só para candidato funcional e configuração fixada. | Relatórios de área, timing, DRC e manifest. | Nenhum resultado físico equivale a sign-off automaticamente. |
| 10 | Revisar evidências, limites e impacto antes de publicar. | Decisão e justificativa versionadas. | Somente humano autoriza tape-out, GDSII ou mudança de baseline. |

### Ciclos de correção

- Falha em 1–3: corrigir especificação, modelo ou RTL; não gerar métrica PPA.
- Falha em 4: registrar o erro e retornar à etapa 2 ou 3.
- Falha em 5: corrigir protocolo/hazard e repetir integração; não adicionar ao
  corpus como exemplo aprovado.
- Falha em 6–8: excluir do treino e preservar o benchmark; não retreinar com
  dados sem revisão.
- Falha em 9: retornar ao candidato funcional; não publicar artefato físico.

O estado atual está entre as etapas 5 e 6: há um programa VPU16 integrado e um
corpus interno inicial, mas ele ainda é pequeno demais para treinamento LoRA.

## English

This is the required order for evolving EF-GPU hardware, data, and models. A
stage starts only after its predecessor has the required artifacts; failures
produce evidence and return to a correction stage rather than advancing.

1. Define scope, provenance, licenses, and authorization.
2. Write the specification, interface, reset, clocks, latency, and criteria.
3. Build a reference model and deterministic tests.
4. Implement a small versioned RTL block.
5. Run lint, simulation, formal where available, and Yosys.
6. Integrate passing blocks through explicit in-order handshakes.
7. Admit only reviewed, licensed, verified examples into split corpus data.
8. Train LoRA/QLoRA only after explicit approval and sufficient data.
9. Compare base and adapter on frozen benchmarks through EDA gates.
10. Run OpenROAD only for functional candidates, then require human review.

No physical report is sign-off, and no model output is trusted RTL. The current
project is between integration and corpus expansion: it has an executing VPU16
program and a seed corpus that is still too small for LoRA training.
