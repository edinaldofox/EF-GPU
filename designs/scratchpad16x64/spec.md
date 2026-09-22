# Scratchpad16x64 — memória vetorial local

## Português

`scratchpad16x64` é uma memória local de 16 palavras de 64 bits para o caminho
didático da EF-GPU. Cada palavra pode guardar quatro lanes de 16 bits. Ela tem
duas leituras combinacionais independentes e uma escrita síncrona, permitindo
buscar dois vetores em paralelo antes de uma operação aritmética.

- Todos os endereços de `0` a `15` são graváveis; diferente de `vreg8x64`, não
  há registrador zero reservado.
- O reset assíncrono ativo em nível baixo zera as 16 palavras.
- Uma escrita ocorre na borda de subida quando `write_enable` está alto.
- Leituras são combinacionais. O valor de leitura durante uma escrita para o
  mesmo endereço não possui bypass definido; testes leem após a borda.

Este é um bloco funcional de referência, implementado com flip-flops para
manter reset explícito e o fluxo simples. Não é uma macro SRAM, não possui
configuração física OpenROAD e não faz alegação de área, frequência ou potência.
O modelo C e o testbench RTL cobrem reset, ambas as portas, palavra `0`, palavra
`15` e sobrescrita.

## English

`scratchpad16x64` is a 16-word, 64-bit local memory for the EF-GPU educational
path. Each word can hold four 16-bit lanes. It has two independent
combinational reads and one synchronous write, so two vectors can be fetched in
parallel before an arithmetic operation.

- Every address from `0` through `15` is writable; unlike `vreg8x64`, there is
  no reserved zero register.
- Active-low asynchronous reset clears all 16 words.
- A write occurs on the rising edge when `write_enable` is high.
- Reads are combinational. Same-address read-during-write has no defined bypass;
  tests read after the write edge.

This is a functional reference block implemented with flip-flops to keep reset
explicit and the flow simple. It is not an SRAM macro, has no OpenROAD physical
configuration, and makes no area, frequency, or power claim. The C model and
RTL testbench cover reset, both ports, word `0`, word `15`, and overwrite.
