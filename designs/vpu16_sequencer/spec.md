# VPU16 sequencer

## Português

`vpu16_sequencer` é o primeiro fetch/PC da EF-GPU. Armazena 16 instruções VPU16,
começa no PC zero e mantém `issue_valid` e a instrução atual estáveis até
`issue_accepted=1`. O PC avança somente após esse aceite; ao aceitar a última
instrução de `program_length`, `halted` sobe. O host grava o programa apenas
quando `running=0`. Não há saltos, cache ou execução fora de ordem.

O teste integrado executa `VLOAD r1,[1]`, `VLOAD r2,[2]`, `VLOAD r3,[3]`, VMAC e
`VSTORE r4,[4]`, verificando o resultado na scratchpad.

## English

`vpu16_sequencer` is EF-GPU's first fetch/PC block. It stores 16 VPU16
instructions, starts at PC zero, and holds `issue_valid` and the current
instruction stable until `issue_accepted=1`. The PC advances only after that
acceptance and `halted` rises after the final instruction. The host writes the
program only while `running=0`. There are no branches, cache, or out-of-order
execution.
