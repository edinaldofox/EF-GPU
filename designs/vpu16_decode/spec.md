# VPU16 decode — instrução vetorial mínima

## Português

`vpu16_decode` é o decodificador combinacional para a primeira instrução da
mini GPU: `VMAC`. A instrução tem 16 bits:

```text
15        12 11       9 8        6 5        3 2        0
+------------+----------+----------+----------+----------+
| opcode     | dst      | src_a    | src_b    | acc      |
+------------+----------+----------+----------+----------+
```

`opcode = 4'h1` reconhece `VMAC`; qualquer outro opcode é inválido. Os campos
de registrador permanecem observáveis mesmo para opcode inválido, mas somente
`valid=1` autoriza uma futura unidade de execução a escrever estado. O bloco
não possui clock nem estado, e não executa a multiplicação.

O modelo C e o testbench RTL verificam a mesma codificação. Síntese Yosys é
executada antes de uma integração com o banco vetorial; não há PPA ou OpenROAD
para este bloco isolado ainda.

## English

`vpu16_decode` is the combinational decoder for the mini GPU's first
instruction: `VMAC`. The 16-bit layout is opcode, destination, source A,
source B, and accumulator register, with three bits per register field.

`opcode = 4'h1` recognizes `VMAC`; every other opcode is invalid. Register
fields remain observable for invalid encodings, but only `valid=1` may let a
future execution unit update state. The block has no clock or state and does
not perform multiplication.

The C model and RTL testbench check the same encoding. Yosys synthesis runs
before vector-register integration; this isolated block has no PPA or OpenROAD
claim yet.
