# VREG8x64 — banco de registradores vetoriais

## Português

`vreg8x64` é o primeiro bloco de estado da mini GPU EF-GPU. Possui oito
registradores de 64 bits; cada registrador representa quatro lanes de 16 bits,
compatíveis com o resultado da VMAC SIMD4x8. Há duas portas de leitura
combinacionais independentes e uma porta de escrita síncrona.

- `r0` lê sempre zero e ignora escritas.
- `r1` a `r7` são atualizados na borda de subida quando `write_enable` está alto.
- Reset assíncrono ativo em nível baixo limpa o armazenamento.
- Leitura no mesmo ciclo de escrita não tem bypass definido; o testbench lê
  somente após a borda de escrita.

O modelo C em `model/` é a referência sem estado temporal para os valores
arquiteturais. O testbench RTL verifica reset, `r0`, sobrescrita e as duas
portas de leitura. O bloco ainda não possui configuração OpenROAD nem métricas
PPA; primeiro estabelecemos a baseline funcional e de síntese.

## English

`vreg8x64` is the first stateful block in the EF-GPU mini GPU. It has eight
64-bit registers, each representing four 16-bit lanes compatible with the
SIMD4x8 VMAC result. It provides two independent combinational read ports and
one synchronous write port.

- `r0` always reads as zero and ignores writes.
- `r1` through `r7` update on the rising edge when `write_enable` is high.
- Active-low asynchronous reset clears storage.
- Same-cycle read-during-write bypass is intentionally unspecified; the RTL
  testbench reads only after the write edge.

The C model in `model/` is the architectural value reference. The RTL
testbench covers reset, `r0`, overwrite, and both read ports. This block has no
OpenROAD configuration or PPA claim yet; functional and synthesis baselines
come first.
