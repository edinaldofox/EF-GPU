# Modelo e dados

## Estratégia de LLM

O modelo será desenvolvido em etapas: primeiro assistência baseada em recuperação de exemplos e regras; depois ajuste supervisionado em pares especificação→RTL/teste; por fim, otimização por feedback de verificadores e métricas físicas válidas.

## Requisitos para dados

- Registrar origem, licença, versão e transformação de cada item.
- Separar treino, validação e benchmark por família de design para evitar vazamento.
- Incluir RTL, testes, resultados de simulação e relatórios EDA quando a licença permitir.
- Remover segredos, PDKs não redistribuíveis e IP proprietário.
- Tratar resultados de ferramenta como evidência contextual, não como verdade universal.

## Avaliação

A avaliação deve medir: taxa de compilação, taxa de testes aprovados, equivalência/formal quando disponível, PPA somente entre candidatos válidos, custo de execução e taxa de intervenção humana. O conjunto de benchmark deve ficar congelado e versionado antes de comparar modelos.
