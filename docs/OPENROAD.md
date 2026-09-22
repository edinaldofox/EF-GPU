# Guia de integração com OpenROAD

## Papel no projeto

OpenROAD é a etapa determinística de implementação física. Ele recebe um netlist sintetizado, bibliotecas/tecnologia e restrições; produz bases de dados, relatórios e, quando o fluxo estiver aprovado, artefatos de layout.

## Pré-requisitos por execução

- Versão identificável de OpenROAD e Yosys.
- PDK, arquivos LEF/Liberty e regras de tecnologia com licença permitida.
- RTL e top module explícitos.
- Arquivo SDC com clocks, I/O delays e exceções justificadas.
- Configuração versionada em `configs/openroad/<design>/`.

## Sequência mínima

1. Validar RTL com lint e simulação.
2. Sintetizar e revisar warnings de Yosys.
3. Executar floorplan, placement, CTS e routing no OpenROAD.
4. Coletar área, WNS/TNS, violações de DRC, congestionamento e estimativa de potência quando suportada.
5. Salvar um manifesto que associe os relatórios ao commit, versões, PDK, seed e configuração.

## Política de resultados

Não compare números entre PDKs, bibliotecas, condições de clock ou versões de ferramentas diferentes sem rotulá-los como não comparáveis. “Sem erros” em um log não equivale a sign-off: DRC/LVS/IR-drop e outras análises dependem do fluxo e das ferramentas efetivamente executados.
