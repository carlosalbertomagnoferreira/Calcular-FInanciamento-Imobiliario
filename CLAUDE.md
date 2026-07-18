# CLAUDE.md

# Instruções para Agentes de IA

Este documento contém as regras operacionais para qualquer agente de IA que trabalhe neste repositório.

Antes de modificar qualquer código, leia também:

1. SPEC.md
2. ARCHITECTURE.md
3. DECISIONS.md
4. ROADMAP.md

O README.MD é destinado aos usuários, não às regras de implementação.

---

# Objetivo do Projeto

Este projeto implementa um simulador de financiamento imobiliário do Banco do Brasil.

O objetivo NÃO é criar um simulador financeiro genérico.

O objetivo é construir um **Digital Twin** do contrato, capaz de reproduzir matematicamente o comportamento do financiamento utilizando o histórico do extrato oficial.

A projeção futura somente poderá ser realizada após validar o modelo utilizando os dados históricos.

---

# Regras Obrigatórias

## Nunca alterar a matemática do contrato sem atualizar o SPEC.md.

Qualquer alteração em:

- juros
- amortização
- cálculo da TR
- saldo devedor
- fórmula PRICE

deve atualizar também a documentação.

---

## Nunca misturar responsabilidades.

É proibido colocar regras financeiras em:

- CLI
- gráficos
- exportadores
- leitores de arquivos

Toda regra financeira pertence ao domínio.

---

## Nunca modificar o CSV original.

O CSV representa a fonte oficial dos dados.

Sempre trabalhar sobre cópias.

---

## Nunca utilizar valores fixos.

Sempre que possível:

- descobrir parâmetros automaticamente
- calcular taxas a partir do histórico
- utilizar configuração centralizada

---

## Nunca remover testes existentes.

Ao alterar um cálculo financeiro:

- atualizar testes
- criar novos testes quando necessário

---

# Fluxo Obrigatório

Toda implementação deve seguir esta ordem:

Leitura

↓

Validação

↓

Reconstrução

↓

Calibração

↓

Comparação

↓

Projeção

↓

Relatórios

↓

Exportação

Nunca inverter essas etapas.

---

# Antes de Implementar

Sempre verificar:

- SPEC.md
- DECISIONS.md
- ARCHITECTURE.md

Se existir conflito:

DECISIONS.md possui prioridade.

---

# Antes de Criar Código Novo

Pergunte:

Existe algum módulo que já resolve esse problema?

Evite duplicação.

Prefira reutilização.

---

# Estilo de Código

Obrigatório:

- Python 3.13
- type hints
- dataclasses quando apropriado
- docstrings (Google Style)
- logging
- funções pequenas
- classes coesas

---

# Qualidade

Antes de considerar uma tarefa concluída:

Executar:

```bash
uv run --group dev ruff check .
uv run --group dev black --check .
uv run --group dev mypy .
uv run --group dev pytest
```

Todos devem passar.

---

# Performance

Este projeto trabalha com aproximadamente 360 parcelas.

Priorize:

1. Correção matemática
2. Clareza
3. Testabilidade

Não faça micro-otimizações desnecessárias.

---

# Arquitetura

O projeto segue uma arquitetura em camadas.

Dependências permitidas:

CLI

↓

Services

↓

Domain

↓

Models

↓

Infrastructure

Nunca inverter dependências.

---

# Padrões

Utilizar:

- Strategy Pattern para cálculos configuráveis
- Factory para leitores e exportadores
- Dependency Injection sempre que possível

Evitar:

- Singletons
- Estado global
- Variáveis globais
- Dependências ocultas

---

# Testes

Todo cálculo financeiro deve possuir:

- teste unitário
- caso de sucesso
- caso limite
- validação numérica

Nunca implementar funcionalidades financeiras sem testes.

---

# Documentação

Toda alteração relevante deve atualizar:

- README.MD (se impactar o uso)
- SPEC.md (se alterar regras)
- ARCHITECTURE.md (se alterar estrutura)
- DECISIONS.md (se alterar decisões arquiteturais)
- CHANGELOG.md (se houver nova versão)

---

# Commits

Utilizar Conventional Commits.

Exemplos:

feat:

fix:

refactor:

docs:

test:

perf:

chore:

---

# Em caso de dúvida

Nunca assumir.

Consultar:

1. SPEC.md
2. DECISIONS.md

Se ainda houver dúvida, preservar o comportamento existente e registrar a necessidade de esclarecimento.

---

# Objetivo Final

Produzir uma biblioteca Python reutilizável para reconstrução e simulação de financiamentos imobiliários.

A CLI, o Dashboard Streamlit e uma futura API REST deverão utilizar exatamente o mesmo núcleo de regras de negócio.

Todo código novo deve contribuir para essa visão.
