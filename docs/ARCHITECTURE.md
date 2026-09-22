# Arquitetura do EF-GPU

## Objetivo

Converter uma intenção de projeto em candidatos a circuito que sejam verificáveis e reproduzíveis. O sistema deve otimizar PPA apenas dentro de contratos funcionais e físicos explícitos.

## Componentes

| Componente | Responsabilidade | Saída versionada |
| --- | --- | --- |
| Especificação | Define ISA/bloco, interfaces, clocks, limites e testes de aceitação | `spec.md` |
| LLM de projeto | Converte a solicitação estruturada em um plano, RTL, testbench, SDC e hipóteses | pacote de proposta JSON |
| Recuperação (RAG) | Seleciona documentação e exemplos licenciados relevantes, com origem | contexto citado da proposta |
| Validador | Lint, simulação, formal e checagem de políticas | evidência de corretude |
| Orquestrador | Executa etapas isoladas, coleta versões e relatórios | manifesto da execução |
| Fluxo EDA | Síntese, floorplan, placement, CTS, routing e análise | relatórios/PPA/GDSII quando autorizado |
| Avaliador | Compara candidatos válidos com baseline | dataset de feedback |

## Contrato de uma proposta

Cada proposta da LLM deve conter, no mínimo:

1. Identificador do design e commit de origem.
2. Descrição da alteração e das hipóteses.
3. RTL, testbench e lista de fontes sem dependências implícitas.
4. Restrições SDC e configuração do fluxo.
5. Prompt, modelo, parâmetros de amostragem e seed.

Uma proposta só pode seguir para otimização física após a validação funcional. Um resultado de PPA sem um teste aprovado é marcado como **inválido**.

Os contratos legíveis por máquina ficam em
[`schemas/design-request.schema.json`](../schemas/design-request.schema.json) e
[`schemas/design-proposal.schema.json`](../schemas/design-proposal.schema.json).
O comando `ef-gpu check-request` ou `ef-gpu check-proposal` executa uma
checagem estrutural sem dependências externas. A definição operacional do ciclo
está em [Agente de projeto](DESIGN_AGENT.md).

## Ciclo controlado de melhoria

1. Uma pessoa aprova a solicitação estruturada e uma baseline funcional.
2. A LLM recebe somente a solicitação, o contexto recuperado e os relatórios da
   execução anterior; ela não recebe autorização implícita para tape-out ou IP.
3. A proposta passa por validação estrutural, lint, simulação e formal quando
   disponível. Falha funcional encerra a tentativa.
4. Apenas candidatos válidos executam Yosys e OpenROAD. O orquestrador coleta
   área, timing, potência estimada, DRC e versões das ferramentas.
5. O avaliador produz feedback estruturado. A LLM pode propor outra variante
   dentro do orçamento, sem substituir a baseline.
6. Uma pessoa revisa a diferença funcional e de PPA antes de aceitar qualquer
   alteração.

## Limites da primeira versão

A primeira versão deve focar blocos independentes e pequenos: ALU inteira, registrador, FIFO, arbiter e unidade de execução simples. Integração de uma GPU completa, IP de terceiros, múltiplos clocks e tape-out ficam fora do escopo inicial.
