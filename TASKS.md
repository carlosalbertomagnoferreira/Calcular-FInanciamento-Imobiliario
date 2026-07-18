# TASKS.md

# Backlog do Projeto

Projeto: Simulador de Financiamento Imobiliário BB

Este arquivo representa o backlog técnico do projeto.

As tarefas somente poderão ser marcadas como concluídas quando:

- código implementado
- testes criados
- documentação atualizada
- lint aprovado
- revisão concluída

---

# Fase 0 — Infraestrutura

## Projeto

- [ ] Criar estrutura de diretórios
- [ ] Configurar ambiente virtual
- [ ] Criar pyproject.toml
- [ ] Criar requirements.txt
- [ ] Configurar Ruff
- [ ] Configurar Black
- [ ] Configurar MyPy
- [ ] Configurar PyTest
- [ ] Configurar Logging
- [ ] Criar arquivo config.py

---

# Fase 1 — Importação

## CSV

- [ ] Ler CSV
- [ ] Validar colunas obrigatórias
- [ ] Validar datas
- [ ] Validar valores
- [ ] Converter números brasileiros
- [ ] Criar DataFrame limpo

---

## Modelos

- [ ] Criar dataclass Contrato
- [ ] Criar dataclass Parcela
- [ ] Criar dataclass Simulação
- [ ] Criar dataclass Resultado

---

# Fase 2 — Reconstrução

## Taxas

- [ ] Calcular taxa mensal
- [ ] Calcular TR histórica
- [ ] Calcular média móvel da TR
- [ ] Calcular TR personalizada

---

## PRICE

- [ ] Calcular juros
- [ ] Calcular amortização
- [ ] Calcular saldo final
- [ ] Validar prestação

---

## Histórico

- [ ] Reconstruir parcelas históricas
- [ ] Comparar saldo
- [ ] Comparar juros
- [ ] Comparar amortização
- [ ] Calcular erro percentual

---

# Fase 3 — Calibração

- [ ] Ajustar parâmetros
- [ ] Minimizar erro
- [ ] Validar tolerâncias
- [ ] Gerar relatório de calibração

---

# Fase 4 — Projeção

- [ ] Projetar parcelas restantes
- [ ] Calcular saldo futuro
- [ ] Calcular juros futuros
- [ ] Calcular amortização futura
- [ ] Exportar CSV

---

# Fase 5 — Relatórios

- [ ] Resumo financeiro
- [ ] Economia de juros
- [ ] Data de quitação
- [ ] Total restante
- [ ] Relatório Markdown
- [ ] Relatório TXT

---

# Fase 6 — Gráficos

- [ ] Saldo devedor
- [ ] Prestação
- [ ] Juros
- [ ] Amortização
- [ ] TR
- [ ] Evolução do contrato

---

# Fase 7 — Amortizações

## Redução de Prazo

- [ ] Implementar algoritmo
- [ ] Validar cálculos
- [ ] Testar cenários

---

## Redução da Prestação

- [ ] Implementar algoritmo
- [ ] Validar cálculos
- [ ] Testar cenários

---

## Cenários

- [ ] Amortização única
- [ ] Amortização mensal
- [ ] Amortização anual
- [ ] Calendário de amortizações

---

# Fase 8 — CLI

- [ ] Comando projetar
- [ ] Comando amortizar
- [ ] Comando relatorio
- [ ] Comando graficos
- [ ] Comando comparar

---

# Fase 9 — PDF

- [ ] Ler PDF
- [ ] Extrair tabela
- [ ] Validar dados
- [ ] Exportar CSV

---

# Fase 10 — Dashboard

- [ ] Upload PDF
- [ ] Upload CSV
- [ ] Simulação
- [ ] Download CSV
- [ ] Download Relatório
- [ ] Dashboard Streamlit

---

# Testes

## Unitários

- [ ] Taxa mensal
- [ ] TR
- [ ] Juros
- [ ] Amortização
- [ ] Saldo
- [ ] Prestação

---

## Integração

- [ ] CSV
- [ ] Reconstrução
- [ ] Projeção
- [ ] Relatórios

---

## Regressão

- [ ] Comparação com contrato real
- [ ] Cenários conhecidos

---

# Documentação

- [ ] README
- [ ] SPEC
- [ ] ARCHITECTURE
- [ ] AGENT
- [ ] CHANGELOG
- [ ] API

---

# Versão 1.0

Critérios para release:

- [ ] Todos os testes aprovados
- [ ] Cobertura > 90%
- [ ] Ruff OK
- [ ] Black OK
- [ ] MyPy OK
- [ ] Documentação completa
