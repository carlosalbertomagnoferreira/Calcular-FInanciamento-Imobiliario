# CHANGELOG.md

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

O formato segue o padrão **Keep a Changelog**.

Versionamento baseado em **Semantic Versioning (SemVer)**.

---

# [Unreleased]

## Added

- Estrutura inicial do projeto
- Documentação arquitetural
- Especificação funcional
- Roadmap
- Guia de contribuição
- Backlog técnico
- Estrutura preparada para reconstrução do financiamento
- Ambiente padronizado com Python 3.13 e uv
- Formalização do escopo da versão 0.2
- Classificação configurável de eventos para calibração
- Relatório de erros percentuais de juros, prestação e saldo
- Classificação explícita de componentes de prestação não identificados
- Identificação ancorada das parcelas válidas 1 a 125

## Changed

- Cenário padrão de projeção passou a usar a média das últimas 12 TRs válidas

## [0.8.0] - Simulação de Amortizações

### Added

- Amortizações únicas, mensais, anuais e programadas
- Modos de redução de prazo, prestação e alias `parcelas`
- Comparação de juros, prazo, saldo e próximas prestações entre os cenários

## [0.7.0] - Gráficos

### Added

- Comando CLI para gerar gráficos em PNG
- Gráficos de saldo devedor, prestação, TR, juros, amortização e evolução do contrato

## [0.6.0] - Relatórios

### Added

- CLI com comandos para validar o extrato, projetar parcelas e gerar relatórios
- Relatórios em Markdown e texto simples com saldo, totais, juros, próxima prestação e quitação

### Changed

- Economia de juros explicitamente adiada para os cenários de amortização

## [0.4.0] - Calibração

### Added

- Classificação de eventos elegíveis e motivos de exclusão auditáveis
- Métricas de erros de juros, prestação e saldo

### Deferred

- Calibração avançada, dependente da explicação dos componentes pendentes

## [0.3.0] - Reconstrução Histórica

### Added

- Modelo imutável para eventos históricos do extrato
- Taxa efetiva mensal, TR histórica e juros estimados para diagnóstico
- Amortização baseada no campo Capital reportado
- Diagnósticos de resíduos de prestação e ajustes de saldo não classificados
- Testes automatizados da reconstrução do CSV de referência

## [0.5.0] - Projeção

### Added

- Cenário de projeção com TR personalizada ou média das TRs históricas válidas
- Projeção das parcelas 126 a 360 até 10/02/2046, exportável em CSV

## [0.2.0] - Importação do Extrato

### Added

- Leitor CSV com normalização de datas e valores brasileiros
- Validação de colunas, campos vazios, datas, valores e duplicidades
- Exceções específicas para erros de importação
- Testes automatizados para o leitor e o CSV de referência
- Stubs de pandas para validação estática

## Planned

- Projeção do contrato
- Simulação de amortizações

---

# [0.1.0] - Projeto Inicial

## Added

### Documentação

- README.MD
- AGENT.md
- SPEC.md
- ARCHITECTURE.md
- ROADMAP.md
- TASKS.md
- CONTRIBUTING.md
- CHANGELOG.md
- DECISIONS.md

### Estrutura

- Organização inicial das pastas
- Definição da arquitetura
- Planejamento das versões

---

# Versionamento

## MAJOR

Mudanças incompatíveis.

Exemplo:

- alteração da arquitetura
- mudança da API

---

## MINOR

Novas funcionalidades.

Exemplo:

- novos gráficos
- suporte ao Streamlit
- novos relatórios

---

## PATCH

Correções.

Exemplo:

- correção de cálculo
- correção de documentação
- melhorias internas

---

# Histórico Futuro

## 0.3.0

Reconstrução do contrato

## 0.4.0

Calibração

## 0.5.0

Projeção

## 0.6.0

Relatórios

## 0.7.0

Gráficos

## 0.8.0

Amortizações

## 0.9.0

Conversor PDF

## 1.0.0

Primeira versão estável
