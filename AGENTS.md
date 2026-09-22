# Guia para agentes — EF-GPU

Este repositório é uma plataforma de pesquisa para transformar requisitos em RTL verificável e, depois, em resultados físicos obtidos com OpenROAD. Segurança, reprodutibilidade e corretude têm precedência sobre velocidade e métricas de PPA.

## Regras de trabalho

1. Leia `README.md` e os documentos aplicáveis em `docs/` antes de mudar código, RTL, scripts de fluxo ou configurações.
2. Mantenha mudanças pequenas, com propósito único e artefatos rastreáveis. Nunca substitua resultados de referência sem preservar a execução anterior.
3. Não faça tape-out, publicação de GDSII, envio de dados proprietários, download de PDK/IP ou acesso a credenciais sem autorização explícita.
4. Não trate texto da LLM como RTL confiável. Todo RTL gerado precisa passar pelas verificações descritas abaixo.
5. Registre para cada experimento: commit Git, prompt/modelo, seed, versões de ferramentas, PDK, entradas, comandos e relatórios.
6. Para trabalho assistido por LLM, use os contratos em `schemas/` e siga o
   ciclo e as portas de qualidade de `docs/DESIGN_AGENT.md`. Uma proposta que
   falhe `ef-gpu check-request` ou `ef-gpu check-proposal` não deve executar o
   fluxo físico.

## Alterações em hardware

Antes de considerar uma alteração concluída, execute o máximo aplicável:

- formatação e lint de Verilog/SystemVerilog;
- simulação com testbench e, quando disponível, verificação formal;
- síntese com Yosys e análise de relatórios;
- fluxo OpenROAD com arquivo de configuração versionado;
- inspeção de erros de DRC, LVS (quando disponível), timing, área e potência;
- comparação com a baseline registrada, sem alegar melhora de PPA se a funcionalidade não foi validada.

Não altere as interfaces de módulos, clocks, resets, domínios de energia ou restrições SDC sem documentar impacto e atualizar testes/configurações correspondentes.

## Convenções do repositório

- RTL e designs: `designs/<nome>/`.
- Configuração física: `configs/openroad/<nome>/`.
- Código do orquestrador: `src/ef_gpu/`.
- Relatórios gerados: fora do Git, em diretório de execução; só versionar sumários pequenos e revisados quando necessários.
- Documentação: Markdown em `docs/`; links relativos e linguagem clara.
- Arquivos de segredo, PDKs completos, bibliotecas de células e saídas volumosas (`.gds`, `.lef`, `.lib`, `.vcd`, logs brutos) não entram no Git sem decisão explícita do mantenedor.

## Comandos e ambiente

Use comandos explícitos, não interativos e reprodutíveis. Prefira `rtk <comando>` no ambiente Codex. Não suponha que OpenROAD, Yosys ou um PDK estejam instalados: detecte e informe a ausência. Fixe versões de containers ou ferramentas antes de comparar benchmarks.

## Critério de entrega

Uma entrega deve informar: o que mudou, os arquivos afetados, como foi validada, quais ferramentas/versões foram usadas e limitações conhecidas. Se uma validação não foi possível, declare-a claramente; não invente métricas nem resultados de sign-off.
