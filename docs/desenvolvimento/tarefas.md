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

- [x] Configurar `uv` e Python 3.13
- [x] Criar `pyproject.toml` e `uv.lock`
- [x] Adicionar configuração inicial de pre-commit
- [x] Registrar os dados de referência
- [x] Criar estrutura de pacotes da aplicação
- [x] Configurar PyTest para a aplicação
- [x] Configurar MyPy e stubs necessários
- [ ] Configurar logging

---

# Fase 1 — Importação (versão 0.2)

## CSV

- [x] Ler CSV
- [x] Validar colunas obrigatórias
- [x] Validar datas
- [x] Validar valores
- [x] Converter números brasileiros
- [x] Criar DataFrame limpo
- [x] Garantir que a leitura não altere o arquivo de origem
- [x] Criar exceções de validação específicas
- [x] Cobrir leitor e validações com testes unitários

---

## Modelos

- [ ] Criar dataclass Contrato
- [ ] Criar dataclass Parcela
- [ ] Criar dataclass Simulação
- [ ] Criar dataclass Resultado

---

# Fase 2 — Reconstrução

## Taxas

- [x] Calcular taxa mensal
- [x] Calcular TR histórica
- [x] Calcular média móvel da TR
- [x] Calcular TR personalizada

---

## PRICE

- [x] Calcular juros estimados para diagnóstico
- [x] Registrar amortização reportada pelo campo Capital
- [x] Calcular saldo teórico e ajuste não classificado
- [x] Validar componentes conhecidos da prestação por resíduo

---

## Histórico

- [x] Reconstruir eventos históricos
- [x] Comparar saldo por ajuste não classificado
- [x] Comparar juros por diferença estimada
- [x] Registrar amortização reportada
- [ ] Calcular erro percentual após a calibração

---

# Fase 3 — Calibração

- [x] Classificar eventos elegíveis e não elegíveis
- [x] Classificar resíduos relevantes como componente não identificado
- [x] Identificar a sequência ancorada de parcelas válidas 1–125
- [x] Gerar resumo com erros percentuais e tolerâncias
- [x] Registrar motivos de exclusão no relatório de calibração
- [ ] Calibração avançada: ajustar parâmetros após explicar componentes pendentes

---

# Fase 4 — Projeção

- [x] Projetar parcelas restantes
- [x] Calcular saldo futuro
- [x] Calcular juros futuros
- [x] Calcular amortização futura
- [x] Exportar CSV

---

# Fase 5 — Relatórios

- [x] Resumo financeiro
- [x] Economia de juros com cenário de amortização
- [x] Data de quitação
- [x] Total restante
- [x] Relatório Markdown
- [x] Relatório TXT

---

# Fase 6 — Gráficos

- [x] Saldo devedor
- [x] Prestação
- [x] Juros
- [x] Amortização
- [x] TR
- [x] Evolução do contrato

---

# Fase 7 — Amortizações

## Redução de Prazo

- [x] Implementar algoritmo
- [x] Validar cálculos
- [x] Testar cenários

---

## Redução da Prestação

- [x] Implementar algoritmo
- [x] Validar cálculos
- [x] Testar cenários

---

## Cenários

- [x] Amortização única
- [x] Amortização mensal
- [x] Amortização anual
- [x] Calendário de amortizações

---

# Fase 8 — CLI

- [x] Comando projetar
- [x] Comando amortizar
- [x] Comando relatorio
- [x] Comando graficos
- [x] Comando comparar

---

# Fase 8.1 — Planejamento de metas (versão 0.9)

## 0.9.1 — Base de estratégias

- [x] Consolidar estratégia, frequência e agenda de amortizações
- [x] Reutilizar a base em `amortizar` e `comparar`
- [x] Centralizar normalização e validações de datas e recorrências
- [x] Cobrir a base compartilhada com testes

## 0.9.2 — Comparação de cenários

- [x] Comparar múltiplas estratégias de amortização
- [x] Exibir aporte, desembolso, juros, quitação, prazo, prestação e saldo
- [x] Evoluir o comando `comparar` para cenários múltiplos
- [x] Cobrir a comparação com testes

## 0.9.3 — Meta de quitação

- [x] Calcular aporte mínimo para uma data de quitação-alvo
- [x] Aceitar estratégias únicas, mensais e anuais
- [x] Retornar aporte nulo quando o cenário-base já cumprir a meta
- [x] Explicar metas inviáveis
- [x] Criar a interface inicial do comando `planejar`
- [x] Cobrir a busca do aporte mínimo com testes de limite em centavos

## 0.9.4 — Meta de prestação

### 0.9.4.1 — Critério de avaliação

- [x] Avaliar a primeira parcela posterior ao aporte, com acessórios
- [x] Excluir a prestação da própria data do aporte
- [x] Considerar R$ 0,00 quando houver liquidação antes da próxima parcela

### 0.9.4.2 — Busca do aporte mínimo

- [x] Calcular aporte mínimo para uma prestação-alvo
- [x] Reutilizar o mecanismo de busca da meta de quitação
- [x] Tratar metas já atendidas e entradas inviáveis
- [x] Cobrir o limite em centavos e as recorrências com testes

### 0.9.4.3 — Interface e validação

- [x] Incluir `--meta-prestacao` no comando `planejar`
- [x] Exibir alvo, aporte, frequência e prestações comparadas
- [x] Documentar o uso da meta de prestação
- [x] Cobrir a CLI com testes

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
- [x] Projeção
- [x] Relatórios

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

## 1.0.1 — Observabilidade operacional

- [x] Configurar logging padronizado e opt-in na CLI
- [x] Cobrir configuração e mensagens operacionais com testes

## 1.0.2 — Regressão e qualidade

- [x] Medir cobertura automatizada
- [x] Atingir cobertura de pelo menos 90%
- [x] Adicionar cenários de regressão do extrato de referência e da CLI

## 1.0.3 — Documentação e release

- [x] Revisar documentação de uso e referência de comandos
- [x] Executar validação final de release

Critérios para release:

- [x] Todos os testes aprovados
- [x] Cobertura > 90%
- [x] Ruff OK
- [x] Black OK
- [x] MyPy OK
- [x] Documentação completa
