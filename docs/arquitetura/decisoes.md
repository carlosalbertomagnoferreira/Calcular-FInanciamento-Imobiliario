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

### Versão oficial

Python 3.13. A versão é declarada em `.python-version` e em `pyproject.toml`.

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

## Não alterar as fontes de entrada nem versionar PDFs bancários

### Status

Aceito

### Motivação

O PDF textual fornecido localmente pelo usuário é uma fonte externa do extrato.
Por conter dados bancários, ele não deve ser incluído no repositório e permanece
ignorado pelo Git. `extrato.csv` é a referência anonimizada versionada e a fonte
de trabalho da aplicação.

Nenhuma fonte de entrada pode ser alterada pela aplicação. O dashboard processa
uploads em diretório temporário, e o comando `extrair-pdf` grava o CSV em um
caminho de saída distinto indicado pelo usuário.

Os testes unitários simulam a saída textual do `pdfplumber` com o CSV anonimizado.
Um PDF externo pode ser usado apenas em integração opcional configurada por
`EXTRATO_PDF_TESTE`, sem cópia ou persistência pelo projeto.

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

# ADR-021

## Reconstrução histórica orientada pelos valores reportados

### Status

Aceito

### Contexto

O extrato contém eventos que não são necessariamente parcelas mensais, incluindo períodos de carência, encargos e ajustes. O saldo atualizado não segue uma recorrência PRICE simples em todas as linhas.

### Decisão

Na reconstrução histórica, os campos reportados pelo Banco do Brasil são autoritativos. `Capital` representa a amortização histórica; `Saldo Atualizado` não é sobrescrito por um saldo calculado; e a TR é não definida quando o saldo devedor é zero.

O sistema calcula valores teóricos e resíduos apenas como diagnósticos. A explicação ou absorção desses resíduos pertence à calibração da versão 0.4.

### Consequências

O histórico permanece auditável e nenhuma hipótese financeira é escondida em uma fórmula de saldo. A projeção continuará bloqueada até a validação e calibração do modelo.

---

# ADR-022

## Vencimento mensal no dia 10

### Status

Aceito

### Decisão

O contrato de referência possui vencimento regular no dia 10 de cada mês. A parcela 360 vence em 10/02/2046; portanto, a validação de sequências mensais deve usar o dia 10 como âncora contratual, salvo se outro contrato informar uma regra diferente.

### Consequências

Eventos fora do dia 10 não são aceitos automaticamente como parcelas regulares na sequência ancorada. Eles continuam preservados como eventos históricos para auditoria.

---

# ADR-023

## Imagem Docker mínima e execução sem privilégios

### Status

Aceito

### Contexto

O dashboard e a CLI precisam de uma forma reproduzível de execução sem carregar
bibliotecas previstas apenas para versões futuras nem expor dados bancários no
artefato distribuído.

### Decisão

Usar um Dockerfile multi-stage baseado em Python 3.13 slim. O `uv.lock` define as
dependências, o estágio final recebe somente runtime e código necessário, e o
Streamlit é o processo padrão. O Compose aplica usuário sem root, raiz somente
leitura, `tmpfs`, remoção de capabilities, `no-new-privileges` e volume local
ignorado para a CLI.

### Consequências

Dependências futuras somente serão adicionadas quando houver código que as use.
PDFs, testes, documentação, caches e dados locais não entram na imagem. Alterações
de dependências ou inicialização devem validar lock, Compose, build, healthcheck
e smoke test da CLI.

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
