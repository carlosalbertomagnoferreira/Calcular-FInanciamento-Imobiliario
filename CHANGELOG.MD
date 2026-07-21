# CHANGELOG.md

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

O formato segue o padrão **Keep a Changelog**.

Versionamento baseado em **Semantic Versioning (SemVer)**.

---

# [Unreleased]

## Added

- Dockerfile multi-stage e Docker Compose para executar dashboard e CLI com
  usuário sem privilégios, healthcheck e filesystem raiz somente leitura
- Guia de execução em Docker, incluindo portas, volume privado, UID/GID e
  comandos operacionais

## Changed

- PDFs de extratos bancários deixam de ser versionados e devem ser fornecidos
  localmente pelo usuário nos fluxos de conversão e dashboard
- Dependências diretas reduzidas às bibliotecas efetivamente usadas em produção
- Versão do projeto preparada para 1.3.0
- Testes de extração, upload e CLI deixam de depender do PDF privado removido e
  passam a usar texto determinístico derivado do CSV anonimizado
- `extrair-pdf` passa a exigir explicitamente o argumento `--pdf`
- Dashboard recebe smoke test nativo do Streamlit sem upload de dados privados
- Tabela de simulação do dashboard passa a exibir apenas valores essenciais e
  comparativos de prestação e saldo contra o cenário-base

---

# [1.2.0] - 2026-07-19

## Added

- Conversão de extrato PDF textual fornecido pelo usuário para CSV validado pelo
  comando `extrair-pdf`
- Dashboard Streamlit para upload seguro de CSV ou PDF textual fornecido pelo
  usuário, análise, gráficos, downloads e simulações avançadas
- Planejamento de metas no dashboard com aportes únicos ou recorrentes e
  visualização da projeção recalculada

## Changed

- Documentação revisada para registrar a conclusão da versão 1.2

## [1.0.0] - 2026-07-19

### Added

- Logging opt-in na CLI por meio de `--log-level`
- Cobertura mínima obrigatória de 90% e regressões para comandos públicos

### Changed

- Documentação de arquitetura e comandos revisada para a primeira versão estável

## [0.9.0] - 2026-07-19

### Added

- Base compartilhada de estratégias, frequências e agendas de amortização para
  os comandos `amortizar` e `comparar`
- Comparação de múltiplas estratégias nomeadas, com métricas financeiras
- Planejamento do aporte mínimo para uma data de quitação-alvo
- Planejamento do aporte mínimo para uma prestação-alvo, incluindo acessórios

### Changed

- Roadmap da versão 0.9 redefinido para planejamento de metas e estratégias,
  dividido nas subfases 0.9.1 a 0.9.4

## [0.8.0] - Simulação de Amortizações

### Added

- Amortizações únicas, mensais, anuais e programadas
- Modos de redução de prazo, prestação e alias `parcelas`
- Comparação de juros, prazo, saldo e próximas prestações entre os cenários

### Changed

- Modos de prestação e parcelas passam a informar o saldo antes e após o aporte
- Datas de amortização normalizadas para o vencimento mensal e validadas contra o prazo
- Saldo de amortizações recorrentes reportado na data final de `--ate`

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
- docs/produto/spec.md
- docs/arquitetura/arquitetura.md
- docs/produto/roadmap.md
- docs/desenvolvimento/tarefas.md
- CONTRIBUTING.md
- CHANGELOG.md
- docs/arquitetura/decisoes.md

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
