# Arquitetura do EF-GPU

## Objetivo

Converter uma intenção de projeto em candidatos a circuito que sejam verificáveis e reproduzíveis. O sistema deve otimizar PPA apenas dentro de contratos funcionais e físicos explícitos.

## Componentes

| Componente | Responsabilidade | Saída versionada |
| --- | --- | --- |
| Especificação | Define ISA/bloco, interfaces, clocks, limites e testes de aceitação | `spec.md` |
| LLM de projeto | Propõe plano, RTL, testbench, SDC e hipóteses | pacote de proposta |
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

## Limites da primeira versão

A primeira versão deve focar blocos independentes e pequenos: ALU inteira, registrador, FIFO, arbiter e unidade de execução simples. Integração de uma GPU completa, IP de terceiros, múltiplos clocks e tape-out ficam fora do escopo inicial.
