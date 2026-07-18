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
- reconstruir todos os eventos históricos
- identificar parâmetros financeiros
- projetar parcelas futuras
- gerar cenários
- calcular economia de juros
- simular amortizações

---

# Entrada

Arquivo CSV. Cada linha representa um evento histórico do extrato e não é, necessariamente, uma parcela mensal PRICE.

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

Vencimento das parcelas:

Dia 10 de cada mês. A parcela 360 vencerá em 10/02/2046.

Taxa efetiva anual de referência:

5.116%

Taxa nominal anual de referência:

4.992%

Marco de parcelas quitadas na emissão do extrato:

125 parcelas (360 meses de prazo original - 235 meses remanescentes).

Para este contrato, as linhas de 10/03/2016 a 10/07/2026 formam uma sequência mensal ancorada: vencimento no dia 10, sem lacunas, saldo devedor positivo, encargos zerados e valor pago igual à prestação. Elas correspondem às parcelas 1 a 125. Seis parcelas de carência, entre junho e novembro de 2020, possuem capital zero e continuam válidas na sequência contratual.

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

Quando o saldo devedor for zero, a TR histórica será registrada como não definida. Nunca utilizar TR fixa para substituir uma observação não definida.

---

# Reconstrução histórica

Cada evento histórico deverá preservar os valores reportados:

- Data
- Saldo Devedor
- Correção Monetária
- Saldo Atualizado
- Prestação
- Capital
- Juros
- Acessórios
- Correção Prestação
- Encargos
- Valor Pago

A reconstrução também deverá acrescentar, sem sobrescrever os valores reportados:

- taxa mensal calculada;
- TR histórica, quando definida;
- amortização reportada;
- juros estimados;
- resíduo da prestação;
- saldo teórico sem ajustes;
- ajuste de saldo não classificado.

---

# Ordem da reconstrução

Para cada evento:

Valores reportados pelo extrato

↓

Taxa mensal e TR histórica, quando aplicável

↓

Amortização reportada pelo campo Capital

↓

Juros estimados e componentes conhecidos da prestação

↓

Diagnósticos de resíduo da prestação e ajuste de saldo

O fluxo não calcula nem substitui um saldo final histórico. O `Saldo Atualizado` do extrato permanece autoritativo até que a calibração explique os ajustes observados.

---

# Fórmulas

## Juros estimados

Juros estimados = Saldo Devedor × taxa_mensal

O resultado é diagnóstico. `Juros` é o valor histórico autoritativo; diferenças podem decorrer de critérios do contrato ainda não calibrados, como datas de apropriação e períodos especiais.

---

## Amortização histórica

Amortização reportada = Capital

O campo `Capital` do extrato é a fonte autoritativa da amortização histórica. A diferença entre prestação e seus componentes conhecidos é registrada como resíduo; ela não deve ser absorvida artificialmente na amortização.

---

## Saldo teórico sem ajustes

Saldo teórico sem ajustes = Saldo Devedor + Correção Monetária - Capital

Esse cálculo é somente um diagnóstico. `Saldo Atualizado` é o valor autoritativo do histórico, pois o extrato pode conter liberações, períodos de carência e outros ajustes não classificados.

## Ajuste de saldo não classificado

Ajuste = Saldo Atualizado - Saldo teórico sem ajustes

---

# Calibração

O sistema deverá classificar os eventos antes de calibrar o modelo. Eventos com saldo devedor zero, encargos de inadimplência, capital zero ou ajuste de saldo relevante poderão permanecer no relatório histórico, mas não devem ser usados automaticamente como amostra de uma parcela PRICE regular.

Os critérios iniciais são configuráveis e classificam como elegível apenas o evento com saldo devedor positivo, capital positivo, sem encargos, ajuste de saldo de até R$ 25,00 e resíduo de prestação de até 1%. Resíduos superiores são classificados como componente não identificado. Os demais eventos são mantidos no relatório com o motivo da exclusão.

A validade da parcela e a elegibilidade de calibração são conceitos distintos. A sequência mensal ancorada identifica parcelas reais do contrato; o filtro de calibração continua conservador enquanto os componentes não identificados não forem explicados.

Após a classificação, a calibração deverá comparar os valores calculados com os valores reportados, sem sobrescrever o extrato. Os parâmetros ajustáveis, os critérios de inclusão e as tolerâncias serão registrados no relatório de calibração.

Nesta etapa, a taxa efetiva anual contratual é preservada. A calibração mede os desvios e não altera automaticamente o contrato quando a amostra indicar eventos ou componentes ainda não explicados.

---

# Critérios de aceitação

Os limites abaixo serão aplicados apenas aos eventos elegíveis para calibração:

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
