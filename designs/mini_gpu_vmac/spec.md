# Mini GPU VMAC core

## Português

Este é o núcleo integrado inicial da EF-GPU:

```text
instrução VPU16 → decode → VREG8x64 (3 leituras) → SIMD4x8 VMAC → VREG8x64
                         ↘ Scratchpad16x64 ↗
```

O host carrega registradores e a scratchpad enquanto o núcleo está ocioso. Uma
instrução válida é aceita somente quando `busy=0`.

- `VMAC dst, src_a, src_b, acc` lê três registradores. Cada lane usa os 8 bits
  baixos de `src_a` e `src_b`, soma o produto ao lane de 16 bits de `acc` e
  grava o resultado de 64 bits em `dst`.
- `VLOAD dst,[addr]` carrega uma palavra de 64 bits da scratchpad de 16 palavras
  para o banco vetorial.
- `VSTORE src,[addr]` grava um registrador vetorial na scratchpad.

VLOAD e VSTORE ocupam um ciclo após o aceite; `done` pulsa no write-back.
Escritas do host concorrentes com issue ou execução são bloqueadas; leituras de
depuração são definidas somente quando o núcleo está ocioso.

Por padrão, o core usa VMAC combinacional. `USE_ITERATIVE=1` seleciona a VMAC
iterativa e mantém o core ocupado por dez ciclos por VMAC. `ENABLE_QUEUE=1`
adiciona uma fila de uma VMAC: uma VMAC válida recebida durante `busy` é retida
e iniciada no ciclo posterior ao write-back. VLOAD/VSTORE recebidas durante
`busy` são descartadas, evitando reordenação de memória antes de existir uma
política explícita de dependências. `queue_full=1` informa que uma nova VMAC
seria descartada.

É um núcleo didático: não há fetch, PC, macro SRAM, PPA nem configuração física
OpenROAD para este core.

## English

This is the EF-GPU's initial integrated core:

```text
VPU16 instruction → decode → VREG8x64 (3 reads) → SIMD4x8 VMAC → VREG8x64
                           ↘ Scratchpad16x64 ↗
```

The host loads registers and scratchpad while the core is idle. A valid
instruction is accepted only when `busy=0`.

- `VMAC dst, src_a, src_b, acc` reads three registers. Each lane uses the low
  8 bits of `src_a` and `src_b`, adds the product to the 16-bit lane of `acc`,
  and writes the 64-bit result to `dst`.
- `VLOAD dst,[addr]` loads a 64-bit word from the 16-word scratchpad into the
  vector bank.
- `VSTORE src,[addr]` stores a vector register into scratchpad.

VLOAD and VSTORE take one cycle after acceptance; `done` pulses at write-back.
Host writes concurrent with issue or execution are blocked; debug reads are
defined only while idle.

The core defaults to combinational VMAC. `USE_ITERATIVE=1` selects iterative
VMAC and keeps the core busy for ten cycles per VMAC. `ENABLE_QUEUE=1` adds a
one-entry VMAC queue: a valid VMAC received during `busy` is retained and starts
in the cycle after write-back. VLOAD/VSTORE received during `busy` are dropped,
avoiding memory reordering before an explicit dependency policy exists.
`queue_full=1` reports that a new VMAC would be dropped.

This is a didactic core: it has no fetch, PC, SRAM macro, PPA, or physical
OpenROAD configuration.
