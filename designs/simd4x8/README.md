# SIMD4x8 MAC — mini unidade de computação GPU

Este design é um núcleo de computação vetorial didático: quatro lanes independentes processam a mesma operação sobre quatro pares de valores `unsigned` de 8 bits. Ele representa um bloco de execução de GPU, não uma GPU completa: não há scheduler, caches, threads, ISA ou memória externa.

Cada instrução conceitual `VMAC` calcula, por lane, `result = acc + (a * b)`, com resultado de 16 bits e overflow descartado em cada lane.

| Variante | Multiplicador | Latência de `VMAC` | Objetivo |
| --- | --- | --- | --- |
| `simd4x8_mac_comb_top` | `a * b` combinacional | 1 ciclo | referência de desempenho/área |
| `simd4x8_mac_iter_top` | shift-and-add | 8 ciclos | referência de área/energia conceitual |

As duas variantes possuem a mesma interface externa. `start` deve ser pulsado por um ciclo; `busy` bloqueia uma nova operação; `done` pulsa por um ciclo quando `result` é válido.

O design usa somente aritmética sem sinal. A próxima evolução deve adicionar banco de registradores vetoriais, fetch/decode e scratchpad, mantendo estas unidades como backend de execução.

`tb/tb_simd4x8_mac.sv` aplica um VMAC de quatro lanes às duas variantes. Ele está pronto para Icarus Verilog ou Verilator; a imagem OpenROAD fixada não inclui simulador.
