# Sprint 3 — fontes externas licenciadas

## Registro inicial

As fontes iniciais estão em
[`configs/training/external-sources-v1.json`](../configs/training/external-sources-v1.json).
Elas foram fixadas por commit e revisadas somente no escopo de RTL Verilog:

| Fonte | Licença | Split | Escopo inicial |
| --- | --- | --- | --- |
| SERV | ISC | treino | ALU serial, alinhador, RAM de registradores e buffer de dados/shift |
| PicoRV32 | ISC | benchmark | `picorv32.v` e seus módulos internos |
| RTL-RISCV32 | MIT | validação | contador de programa isolado |
| FemtoRV tutorial | BSD-3-Clause | validação | contadores síncronos de cinco bits, direto e com divisor de clock |
| FazyRV | MIT | treino | adders, comparador, registradores seriais, RAMs, alinhador, PC e decodificador RVC |
| Tachyum FMA RTL | Apache-2.0 | benchmark | primitivas de mux, registrador, incremento, soma e deslocamento |

Ambas são extraídas somente em diretórios temporários. Firmware, PDK, saídas
geradas, submódulos e arquivos não listados são excluídos. Cada linha admitida
deve conter commit, caminho, hash, licença e comando de verificação.

## Próxima porta

A admissão só ocorrerá para módulos que compilam/sintetizam no ambiente fixado.
O benchmark não pode compartilhar conteúdo-fonte com treino ou validação.

## Evidência de extração temporária

Os verificadores abaixo baixam o commit registrado para um diretório temporário,
confirmam o `HEAD` e o SHA-256 do arquivo de licença antes de montar o código
como somente leitura no contêiner. Eles não salvam RTL externo no repositório.

```bash
./scripts/verify-external-rtl.sh serv
./scripts/synth-external-rtl.sh serv serv_alu
./scripts/synth-external-rtl.sh serv serv_aligner
./scripts/verify-external-rtl.sh picorv32
./scripts/synth-external-rtl.sh picorv32 picorv32_pcpi_mul
```

As verificações funcionais atuais são testes de fumaça próprios do EF-GPU:
o alinhador e a ALU serial do SERV, e a instrução `MUL` (7 × 9 = 63) da
unidade PCPI iterativa do PicoRV32. Os três alvos também sintetizaram com
Yosys 0.68 na imagem OpenROAD fixada. A `serv_rf_ram` foi elaborada em uma
configuração explícita de largura oito antes da síntese, eliminando o aviso dos
parâmetros padrão inválidos da fonte; ela agora é exemplo admitido. O contador
FemtoRV verifica o estado inicial, três incrementos e UART inativa.
No RTL-RISCV32, os módulos `alu` e `instr_decode` também foram excluídos: o
Yosys encontrou latches implícitos. O contador de programa passou simulação e
síntese sem esse alerta e é a única família admitida dessa fonte.

## Corpus candidato e benchmark congelado

`./scripts/build-external-circuit-corpus.sh <novo-arquivo.jsonl>` refaz os
clones temporários, extrai somente os três exemplos que passaram ambas as
portas e grava um manifesto com o SHA-256 do benchmark. A extração é literal,
inclui os hashes de RTL/testbench/licença e registra que os testbenches são
criações do EF-GPU. O construtor rejeita checkout, licença ou destino já
existente incorretos. Este artefato ainda está abaixo da meta da Sprint 3
(100/20/20); portanto é candidato rastreável, não corpus autorizado para
treinar pesos.

Para registrar a porta de escala sem alterar o corpus, execute:

```bash
PYTHONPATH=src python3 -m ef_gpu.cli sprint3-corpus-readiness \
  datasets/circuit/external-candidates-v1.jsonl \
  --manifest datasets/circuit/external-candidates-v1.jsonl.manifest.json \
  --output <novo-relatorio.json>
```

O relatório confere o conteúdo exato do benchmark congelado e exige 100 exemplos
de treino, 20 de validação e 20 de benchmark. Ele nunca autoriza pesos por si só.
No corpus externo v13 atual, a contagem é 14/3/20; os déficits são 86/17/0. A
porta, portanto, permanece fechada de propósito.
