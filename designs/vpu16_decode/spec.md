# VPU16 decode — instruções vetoriais mínimas

## Português

`vpu16_decode` é o decodificador combinacional do caminho inicial de computação
e memória local da mini GPU. Os opcodes reconhecidos são:

| Opcode | Instrução | Efeito arquitetural |
| --- | --- | --- |
| `4'h1` | `VMAC dst, src_a, src_b, acc` | `dst = acc + src_a × src_b`, por lane |
| `4'h2` | `VLOAD dst, [addr]` | carrega a palavra `addr` da scratchpad em `dst` |
| `4'h3` | `VSTORE src, [addr]` | grava `src` na palavra `addr` da scratchpad |

`VMAC` usa todos os campos abaixo. Para `VLOAD` e `VSTORE`, `dst` (bits
`11:9`) identifica o registrador de destino ou fonte e `addr` usa os bits
`3:0`; os bits `8:4` são reservados e devem ser zero nos programas de exemplo.

```text
15        12 11       9 8        6 5        3 2        0
+------------+----------+----------+----------+----------+
| opcode     | dst/src  | src_a    | src_b    | acc/addr |
+------------+----------+----------+----------+----------+
```

`valid=1` somente para os três opcodes listados. Os campos permanecem
observáveis para encoding inválido, mas somente uma instrução válida pode
atualizar estado. O bloco não possui clock nem estado. O modelo C e o
testbench RTL verificam cada opcode, os campos e uma codificação inválida.

## English

`vpu16_decode` is the combinational decoder for the mini GPU's initial
compute and local-memory path. Recognized opcodes are:

| Opcode | Instruction | Architectural effect |
| --- | --- | --- |
| `4'h1` | `VMAC dst, src_a, src_b, acc` | `dst = acc + src_a × src_b`, per lane |
| `4'h2` | `VLOAD dst, [addr]` | load scratchpad word `addr` into `dst` |
| `4'h3` | `VSTORE src, [addr]` | store `src` into scratchpad word `addr` |

`VMAC` uses every field above. For `VLOAD` and `VSTORE`, `dst` (bits `11:9`)
identifies the destination or source register and `addr` uses bits `3:0`; bits
`8:4` are reserved and should be zero in example programs.

`valid=1` only for the three listed opcodes. Fields remain observable for an
invalid encoding, but only a valid instruction may update state. The block has
no clock or state. Its C model and RTL testbench cover every opcode, fields,
and an invalid encoding.
