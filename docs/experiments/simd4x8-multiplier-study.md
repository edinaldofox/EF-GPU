# Estudo de multiplicadores SIMD4x8

## Hipótese

Um `VMAC` combinacional entrega um resultado por ciclo, mas deve usar mais células e ter caminho crítico maior. Um `VMAC` iterativo reutiliza somadores por oito ciclos, reduzindo a lógica combinacional por lane e aumentando a latência.

## Controle experimental

- PDK: `sky130hd` incluído na imagem OpenROAD fixada pelo digest do projeto.
- Clock: 100 MHz (período de 10 ns), com 0,20 ns de incerteza.
- Lanes: quatro; operandos unsigned de 8 bits; acumuladores/resultados de 16 bits por lane.
- Interface: idêntica entre variantes (`clk`, `rst_n`, `start`, `a`, `b`, `acc`, `busy`, `done`, `result`).
- A variante iterativa tem latência de oito ciclos; a combinacional registra o resultado no ciclo de `start`.

## Como executar

```bash
./scripts/synth-simd4x8.sh
./scripts/openroad-simd4x8.sh
```

Os relatórios ficam em `.openroad-work/`, que não é versionado. Registre no commit os valores de área, WNS/TNS, DRC e potência se disponível. Nunca compare PPA com outro PDK, outra imagem ou outra restrição de clock.

## Limitações

O fluxo mede implementação digital com bibliotecas `sky130hd`; não valida a função com um simulador externo, não executa LVS/IR-drop completo e não representa uma GPU comercial. Nesta máquina, `repair_timing` após CTS encerra com `illegal instruction` na imagem fixada; a configuração o desabilita para permitir que as demais etapas sejam investigadas. Portanto, qualquer PPA produzido aqui é **preliminar** e não serve para decisão de arquitetura até executar o fluxo completo em um ambiente compatível.
