# ROADMAP.md

# Roadmap
## Simulador de Financiamento Imobiliário Banco do Brasil

Versão do documento: 1.0

---

# Visão

Criar uma ferramenta completa para reconstrução, simulação e análise de financiamentos imobiliários do Banco do Brasil.

No futuro o projeto deverá suportar múltiplos bancos, dashboard web, API REST e comparação entre contratos.

---

# Objetivos

O projeto será desenvolvido incrementalmente.

Cada versão deverá possuir:

- funcionalidades completas
- documentação
- testes automatizados
- versionamento

Nenhuma funcionalidade deverá ser considerada concluída sem testes.

---

# Versão 0.1
## Fundação do Projeto

### Objetivos

Criar toda a estrutura inicial.

### Entregas

- Estrutura de diretórios
- README
- AGENT
- SPEC
- ARCHITECTURE
- Configuração do projeto
- requirements.txt
- pyproject.toml
- Logger
- Configurações globais

### Critério de aceite

Projeto executando:

```bash
python main.py --help
```

---

# Versão 0.2
## Leitura do Extrato

### Objetivos

Importar corretamente o CSV.

### Entregas

Leitor CSV

Validação de:

- colunas
- tipos
- datas
- valores

Conversão automática para DataFrame.

### Critério

Leitura de qualquer CSV compatível.

---

# Versão 0.3
## Reconstrução do Contrato

### Objetivos

Reconstruir todas as parcelas históricas.

### Entregas

Calcular:

- taxa mensal
- juros
- amortização
- saldo
- TR

### Critério

Reconstrução das 125 parcelas existentes.

---

# Versão 0.4
## Calibração

### Objetivos

Comparar cálculos com o contrato real.

### Entregas

Calcular erro percentual.

Ajustar automaticamente:

- TR média
- tolerâncias

### Critério

Erro inferior a:

Prestação:

< 1%

Saldo:

< 0.5%

---

# Versão 0.5
## Projeção

### Objetivos

Projetar todas as parcelas futuras.

### Entregas

Gerar:

projecao.csv

### Informações

Para cada parcela:

- data
- saldo inicial
- correção
- juros
- amortização
- prestação
- saldo final

---

# Versão 0.6
## Relatórios

### Objetivos

Criar relatórios financeiros.

### Entregas

Resumo do contrato.

Saldo atual.

Saldo projetado.

Total pago.

Total restante.

Economia de juros.

Data prevista de quitação.

---

# Versão 0.7
## Gráficos

### Objetivos

Visualização.

### Entregas

Saldo devedor.

Prestação.

TR.

Juros.

Amortização.

Evolução do contrato.

---

# Versão 0.8
## Simulação de Amortizações

### Objetivos

Permitir amortizações extraordinárias.

### Modos

Redução de prazo.

Redução da prestação.

### Cenários

Valor único.

Mensal.

Anual.

Programado.

---

# Versão 0.9
## Comparação de Cenários

### Objetivos

Comparar:

Cenário original

×

Novo cenário

### Métricas

Economia.

Juros.

Prazo.

Prestação.

Saldo.

---

# Versão 1.0
## Simulador Completo

### Objetivos

Primeira versão estável.

### Funcionalidades

Reconstrução.

Calibração.

Projeção.

Amortização.

Gráficos.

Relatórios.

CLI completa.

Exportação.

Testes.

Documentação.

---

# Versão 1.1
## Conversor PDF → CSV

### Objetivos

Eliminar necessidade de gerar CSV manualmente.

### Fluxo

PDF

↓

Extração

↓

CSV

↓

Simulação

---

# Versão 1.2
## Dashboard

Tecnologia

Streamlit

### Recursos

Upload PDF.

Upload CSV.

Simulação.

Gráficos.

Download.

---

# Versão 1.3
## Comparador de Financiamentos

### Objetivos

Comparar contratos.

Banco A

×

Banco B

Comparar:

- juros
- saldo
- prazo
- economia

---

# Versão 1.4
## Banco de Dados

Persistência.

SQLite inicialmente.

Depois PostgreSQL.

---

# Versão 1.5
## API REST

FastAPI.

Endpoints.

Projetar.

Simular.

Exportar.

---

# Versão 2.0
## Multi Banco

Adicionar suporte para:

Caixa.

Itaú.

Santander.

Bradesco.

Sicredi.

Sicoob.

---

# Melhorias Técnicas

## Logging

Adicionar níveis.

INFO

DEBUG

WARNING

ERROR

---

## Performance

Meta:

Reconstrução:

< 2 segundos

Projeção:

< 1 segundo

---

## Testes

Cobertura mínima:

90%

Testes unitários.

Testes de integração.

Testes de regressão.

---

# Backlog

## Alta prioridade

- Conversor PDF
- Simulação
- Dashboard
- Comparação

---

## Média prioridade

Excel

Parquet

JSON

API

---

## Baixa prioridade

OCR

Mobile

Docker

Kubernetes

---

# Ideias Futuras

Machine Learning para prever TR.

Importação automática do Banco do Brasil.

Leitura direta do PDF.

Dashboard online.

Modo consultor financeiro.

Relatórios PDF.

Exportação para Power BI.

Comparação de investimentos × amortização.

Simulação de antecipação de parcelas.

Modo "quanto economizo se amortizar todo mês".

Simulação de portabilidade.

---

# Definição de Pronto (Definition of Done)

Uma funcionalidade somente poderá ser considerada concluída quando possuir:

- Código implementado
- Testes automatizados
- Documentação atualizada
- Tipagem completa
- Lint sem erros
- Cobertura mínima atendida
- Aprovação dos testes

---

# Critérios de Qualidade

Todo código deverá:

- possuir type hints
- utilizar dataclasses quando apropriado
- possuir docstrings
- seguir PEP8
- passar no Ruff
- passar no Black
- passar no MyPy
- passar no Pytest

---

# Objetivo Final

Transformar este projeto em uma biblioteca Python reutilizável para análise de financiamentos imobiliários, acompanhada de uma aplicação web (Streamlit), uma API REST (FastAPI) e suporte a múltiplas instituições financeiras.
