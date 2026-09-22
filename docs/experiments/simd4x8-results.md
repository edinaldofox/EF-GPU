# Resultados preliminares — SIMD4x8 VMAC

Data da execução: 2026-09-22. Commit de trabalho: ainda não publicado. Ferramentas: imagem `openroad/orfs@sha256:573c1716efa0e286c4f641c26d343e20929d58d27fffbb22be2d0b93f09764f6`, PDK `sky130hd`, clock de 10 ns e incerteza de 0,20 ns.

| Variante | Latência funcional | Área após route | Utilização reportada | Route DRC | Antena |
| --- | ---: | ---: | ---: | ---: | ---: |
| `simd4x8_mac_comb_top` | 1 ciclo | 13.902 µm² | 38% | 0 entradas | 0 net / 0 pin |
| `simd4x8_mac_iter_top` | 8 ciclos | 25.642 µm² | 36% | 0 entradas | 0 net / 0 pin |

## Baseline funcional C + RTL

Em 2026-09-22, `./scripts/verify-simd4x8.sh` validou as duas variantes contra
um modelo de referência em C. O teste compila o modelo com GCC, gera quatro
casos de borda e 128 vetores pseudoaleatórios com seed fixa (`0x1badb002`) e
os aplica ao testbench SystemVerilog. Resultado: **132/132 vetores aprovados**
para `simd4x8_mac_comb_top` e `simd4x8_mac_iter_top`.

O ambiente de simulação é construído de
[`docker/sim/Dockerfile`](../../docker/sim/Dockerfile), com base Ubuntu fixada
por digest e Icarus Verilog 12.0-2build2. Esta verificação funcional é uma porta
anterior a qualquer comparação de PPA; ela não constitui equivalência formal,
análise de potência ou sign-off.

## Interpretação

O resultado é contraintuitivo somente à primeira vista: a versão iterativa não compartilha um multiplicador entre todas as lanes; ela possui **quatro** multiplicadores, cada um com registradores de acumulador, deslocamento, contador e controle. Para esta largura pequena e este PDK, os 8 ciclos não compensam o custo dos estados. A variante combinacional possui quatro multiplicadores inferidos e um único estágio de registro, por isso ocupa menos área nesta implementação.

Não há WNS/TNS, potência nem sign-off válidos: a imagem fixada encerra com `illegal instruction` dentro de `repair_timing` e novamente na etapa final do OpenROAD neste host. O workaround permitiu concluir floorplan, placement e detailed routing, mas pulou `repair_timing` e as métricas automáticas. Assim, estes dados servem para aprendizado e para comparar a área roteada sob condições idênticas; não devem orientar uma decisão de tape-out ou de microarquitetura final.
