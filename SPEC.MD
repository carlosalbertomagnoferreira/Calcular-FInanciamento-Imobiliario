# SPEC.md

# Especificação Funcional
## Simulador de Financiamento Imobiliário Banco do Brasil

Versão: 1.0

---

# Objetivo

Construir um simulador capaz de reconstruir matematicamente um financiamento
imobiliário do Banco do Brasil a partir do extrato oficial.

O simulador deverá reproduzir o comportamento histórico do contrato e projetar
todo o período restante até a quitação.

O projeto NÃO tem como objetivo apenas estimar parcelas.

O objetivo é criar um modelo matemático equivalente ao contrato.

---

# Escopo

O sistema deverá:

- importar o histórico do contrato
- validar os dados
- reconstruir todas as parcelas
- identificar parâmetros financeiros
- projetar parcelas futuras
- gerar cenários
- calcular economia de juros
- simular amortizações

---

# Entrada

Arquivo CSV.

Colunas obrigatórias:

| Coluna | Tipo |
|---------|------|
| Data | Date |
| Saldo Devedor | Decimal |
| Correção Monetária | Decimal |
| Saldo Atualizado | Decimal |
| Prestação | Decimal |
| Juros | Decimal |
| Acessórios | Decimal |
| Correção Prestação | Decimal |
| Encargos | Decimal |
| Valor Pago | Decimal |
| Capital | Decimal |

---

# Dados do contrato

Sistema:

PRICE

Indexador:

TR

Prazo:

360 meses

Taxa efetiva anual:

5.116%

Taxa nominal anual:

4.992%

---

# Conversões

## Taxa mensal

A taxa mensal deverá ser calculada por:

i = (1 + ia)^(1/12) - 1

onde

ia = taxa anual

---

## TR mensal

A TR aplicada em cada parcela deverá ser calculada por:

TR = Correção Monetária / Saldo Devedor

Sempre utilizar os dados históricos.

Nunca utilizar TR fixa.

---

# Reconstrução

Cada parcela deverá possuir:

Data

Saldo Inicial

Correção Monetária

Saldo Corrigido

Juros

Amortização

Prestação

Saldo Final

---

# Ordem dos cálculos

Para cada parcela:

Saldo Inicial

↓

Correção TR

↓

Saldo Corrigido

↓

Juros

↓

Prestação

↓

Amortização

↓

Saldo Final

---

# Fórmulas

## Juros

Juros = Saldo Corrigido × taxa_mensal

---

## Amortização

Amortização = Prestação - Juros

---

## Saldo Final

Saldo Final = Saldo Corrigido - Amortização

---

# Calibração

O sistema deverá reconstruir todas as parcelas históricas.

Após reconstrução deverá comparar:

Prestação calculada

×

Prestação real

Saldo calculado

×

Saldo real

Caso o erro ultrapasse a tolerância definida,
os parâmetros deverão ser recalibrados.

---

# Critérios de aceitação

Erro máximo:

Prestação

< 1%

Saldo devedor

< 0.5%

Juros

< 1%

---

# Projeção

Após validação do histórico,
projetar todas as parcelas restantes.

O modelo deverá utilizar:

TR média

ou

TR personalizada.

---

# Cenários

Suportar:

TR média histórica

TR fixa

TR = 0

TR personalizada

---

# Amortizações

Permitir:

Valor único

Amortizações mensais

Amortizações anuais

Amortizações programadas

---

# Modos

## Redução de prazo

Mantém valor da prestação.

Reduz quantidade de parcelas.

---

## Redução de prestação

Mantém prazo.

Reduz valor das prestações.

---

# Relatórios

O sistema deverá produzir:

Saldo atual

Saldo projetado

Total pago

Total restante

Total de juros

Economia de juros

Prazo final

Nova prestação

Nova data de quitação

---

# Arquivos gerados

dados/projecao.csv

dados/relatorio.csv

graficos/saldo.png

graficos/prestacoes.png

graficos/juros.png

graficos/amortizacao.png

relatorio.txt

---

# Interface

CLI utilizando Typer.

Comandos previstos:

projetar

relatorio

graficos

amortizar

comparar

dashboard

---

# Dashboard

Versão futura.

Tecnologia:

Streamlit

Permitirá:

Upload PDF

Upload CSV

Comparação de cenários

Gráficos interativos

Download dos resultados

---

# Conversor PDF

Versão futura.

Fluxo:

PDF

↓

Extração

↓

Validação

↓

CSV

↓

Reconstrução

---

# Qualidade

Cobertura mínima de testes:

90%

Todos os cálculos devem possuir testes unitários.

---

# Performance

O sistema deverá ser capaz de reconstruir
360 parcelas em menos de 2 segundos.

---

# Logging

Registrar:

Leitura

Reconstrução

Calibração

Projeção

Exportação

Erros

---

# Tratamento de erros

CSV inválido

Campos ausentes

Datas inválidas

Valores negativos

Duplicidade de parcelas

Campos obrigatórios vazios

---

# Roadmap

## v1

Leitura CSV

Reconstrução

Projeção

CSV

Gráficos

---

## v2

PDF → CSV

---

## v3

Dashboard

---

## v4

Suporte Caixa

---

## v5

Suporte Itaú

---

## v6

Suporte Santander

---

## v7

API REST

---

# Fora do escopo

Refinanciamentos.

Portabilidade.

Renegociação.

Contratos SAC.
