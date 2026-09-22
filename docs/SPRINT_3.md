# Sprint 3 — fontes externas licenciadas

## Registro inicial

As fontes iniciais estão em
[`configs/training/external-sources-v1.json`](../configs/training/external-sources-v1.json).
Elas foram fixadas por commit e revisadas somente no escopo de RTL Verilog:

| Fonte | Licença | Split | Escopo inicial |
| --- | --- | --- | --- |
| SERV | ISC | treino | módulos `rtl/serv_*.v` pequenos |
| PicoRV32 | ISC | benchmark | `picorv32.v` e seus módulos internos |

Ambas são extraídas somente em diretórios temporários. Firmware, PDK, saídas
geradas, submódulos e arquivos não listados são excluídos. Cada linha admitida
deve conter commit, caminho, hash, licença e comando de verificação.

## Próxima porta

A admissão só ocorrerá para módulos que compilam/sintetizam no ambiente fixado.
O benchmark não pode compartilhar conteúdo-fonte com treino ou validação.
