# Configuração física da ALU8

Top module: `ef_gpu_alu8`.

Fontes RTL:

```text
designs/alu8/rtl/alu8_core.sv
designs/alu8/rtl/ef_gpu_alu8.sv
```

As restrições de 100 MHz estão em `constraints.sdc`. Este diretório ainda não contém um script de implementação porque um PDK não foi selecionado ou autorizado. Para rodar OpenROAD são necessários, no mínimo, LEF de tecnologia/células, Liberty, regras de routing e um fluxo que associe esses arquivos licenciados ao design. Não compare PPA antes de fixar esses elementos.
