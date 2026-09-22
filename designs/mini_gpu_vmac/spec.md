# Mini GPU VMAC core

## Português

Este é o primeiro núcleo integrado da EF-GPU. Ele conecta:

```text
instrução VPU16 → decode → VREG8x64 (3 leituras) → SIMD4x8 VMAC → VREG8x64
```

O host carrega `r1`–`r7` pela porta de escrita enquanto o núcleo está ocioso.
Uma instrução `VMAC dst, src_a, src_b, acc` válida é aceita somente quando
`busy=0`. No ciclo de aceitação, o núcleo lê os três registradores; cada lane
usa os 8 bits baixos de sua palavra de 16 bits em `src_a` e `src_b`, soma o
produto ao lane de 16 bits de `acc` e grava o resultado de 64 bits em `dst`.
`done` pulsa quando a escrita de retorno ocorre. Escritas do host concorrentes
com issue ou execução são bloqueadas; leituras de depuração são definidas
somente quando o núcleo está ocioso.

O core usa a VMAC combinacional, mas a interface expõe `busy/done` para que a
mesma arquitetura possa receber depois a unidade iterativa. Este é um núcleo
didático de uma instrução, não uma GPU completa: não há fetch, PC, memória ou
scheduler independente. Não há PPA nem configuração OpenROAD ainda.

## English

This is the first integrated EF-GPU core:

```text
VPU16 instruction → decode → VREG8x64 (3 reads) → SIMD4x8 VMAC → VREG8x64
```

The host loads `r1`–`r7` while the core is idle. A valid
`VMAC dst, src_a, src_b, acc` is accepted only when `busy=0`. On acceptance,
the core reads three registers; every lane uses the low eight bits of its
16-bit source words, adds the product to the 16-bit accumulator lane, and
writes the 64-bit result to `dst`. `done` pulses when write-back occurs.
Concurrent host writes are blocked during issue/execution, and debug reads are
defined only while idle.

The core uses the combinational VMAC but exposes `busy/done` so the iterative
unit can replace it later. It is a didactic one-instruction core, not a full
GPU: it has no fetch, PC, memory, or independent scheduler. No PPA or OpenROAD
claim exists yet.
