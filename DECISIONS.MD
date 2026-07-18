# DECISIONS.md

# Registro de Decisões Arquiteturais

Este documento registra as principais decisões técnicas do projeto.

Cada decisão possui um identificador permanente.

Formato inspirado em ADR (Architecture Decision Records).

---

# ADR-001

## Utilizar Python

### Status

Aceito

### Motivação

Python oferece excelente ecossistema para:

- análise financeira
- ciência de dados
- visualização
- processamento de PDFs

Além disso, reduz significativamente o tempo de desenvolvimento.

---

# ADR-002

## Utilizar Pandas como estrutura principal

### Status

Aceito

### Motivação

Todo o contrato financeiro é naturalmente representado como uma tabela temporal.

O Pandas oferece:

- operações vetorizadas
- filtros
- agregações
- exportação
- integração com gráficos

---

# ADR-003

## Não alterar o CSV original

### Status

Aceito

### Motivação

O CSV representa a fonte oficial do contrato.

Toda transformação deverá ocorrer sobre cópias.

---

# ADR-004

## Utilizar dataclasses

### Status

Aceito

### Motivação

Reduz código boilerplate.

Melhora legibilidade.

Facilita testes.

---

# ADR-005

## Arquitetura em camadas

### Status

Aceito

### Camadas

CLI

↓

Serviços

↓

Domínio

↓

Modelos

↓

Utilitários

### Motivação

Separação de responsabilidades.

---

# ADR-006

## Toda regra financeira permanece no domínio

### Status

Aceito

### Motivação

Evitar duplicação.

Facilitar testes.

Permitir reutilização.

---

# ADR-007

## Estratégia para cálculo da TR

### Status

Aceito

### Motivação

Permitir diferentes cenários.

Exemplos:

TR histórica

TR média

TR fixa

TR personalizada

Sem alterar o restante do sistema.

---

# ADR-008

## Utilizar Typer para CLI

### Status

Aceito

### Motivação

API moderna.

Boa documentação.

Excelente integração com type hints.

---

# ADR-009

## Utilizar Rich

### Status

Aceito

### Motivação

Melhor experiência na linha de comando.

Tabelas.

Cores.

Progress bars.

---

# ADR-010

## Utilizar Matplotlib

### Status

Aceito

### Motivação

Biblioteca consolidada.

Boa integração com Pandas.

Sem dependências externas.

---

# ADR-011

## Utilizar Strategy Pattern

### Status

Aceito

### Aplicações

TR

Amortização

Projeção

Relatórios

### Motivação

Evitar if/else espalhados.

Facilitar novos cenários.

---

# ADR-012

## Utilizar Factory Pattern

### Status

Aceito

### Aplicações

Exportadores

Leitores

Relatórios

---

# ADR-013

## Reconstrução antes da projeção

### Status

Aceito

### Motivação

Nenhuma projeção será realizada antes de validar o modelo utilizando o histórico real.

Fluxo obrigatório:

CSV

↓

Reconstrução

↓

Calibração

↓

Validação

↓

Projeção

---

# ADR-014

## Calibração Automática

### Status

Aceito

### Motivação

Os contratos do Banco do Brasil podem conter:

- seguros
- acessórios
- encargos
- amortizações extraordinárias

O modelo deverá ajustar automaticamente seus parâmetros.

---

# ADR-015

## Priorizar precisão em vez de performance

### Status

Aceito

### Motivação

O conjunto de dados possui poucas centenas de parcelas.

Precisão matemática é mais importante que micro otimizações.

---

# ADR-016

## Exportação desacoplada

### Status

Aceito

### Motivação

O domínio nunca deverá conhecer:

CSV

Excel

JSON

Parquet

Esses formatos pertencem à camada de infraestrutura.

---

# ADR-017

## Dashboard separado da biblioteca

### Status

Aceito

### Motivação

A lógica financeira deve permanecer independente da interface.

CLI

Dashboard

API

Todos utilizarão a mesma biblioteca.

---

# ADR-018

## Preparação para múltiplos bancos

### Status

Aceito

### Motivação

Inicialmente o projeto suportará apenas o Banco do Brasil.

A arquitetura deverá permitir futuramente:

- Caixa
- Itaú
- Santander
- Bradesco
- Sicredi
- Sicoob

Sem alterações profundas.

---

# ADR-019

## Testes como requisito obrigatório

### Status

Aceito

### Motivação

Todo cálculo financeiro deve possuir testes automatizados.

Não existe funcionalidade "pronta" sem testes.

---

# ADR-020

## Digital Twin do Contrato

### Status

Aceito

### Motivação

Este projeto não é um simulador genérico de financiamentos.

Seu objetivo é reconstruir matematicamente o contrato real do Banco do Brasil, reproduzindo o comportamento observado no histórico antes de realizar projeções.

Toda nova funcionalidade deve preservar essa premissa.

---

# Processo para novas decisões

Novas decisões deverão conter:

- Identificador (ADR-XXX)
- Status
- Contexto
- Problema
- Alternativas consideradas
- Decisão tomada
- Consequências

Nenhuma decisão arquitetural importante deve existir apenas no código.

Todas devem ser registradas neste documento.
