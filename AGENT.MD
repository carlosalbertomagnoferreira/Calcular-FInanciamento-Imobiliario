# AGENT.md

## Projeto

Simulador de financiamento imobiliário do Banco do Brasil.

O objetivo deste projeto é reconstruir matematicamente um financiamento
imobiliário utilizando o extrato oficial do Banco do Brasil e projetar
todo o contrato até sua quitação.

O projeto NÃO é um simples simulador financeiro.

O objetivo é criar um "Digital Twin" (gêmeo digital) do contrato.

---

# Fonte de dados

A entrada principal será um CSV obtido a partir do PDF do extrato do
Banco do Brasil.

O CSV possui as colunas:

- Data
- Saldo Devedor
- Correção Monetária
- Saldo Atualizado
- Prestação
- Juros
- Acessórios
- Correção Prestação
- Encargos
- Valor Pago
- Capital

O comando `extrair-pdf` converte o PDF textual do BB em um CSV separado e
validado, sem alterar os arquivos de referência.

---

# Tipo do financiamento

Sistema:

PRICE

Indexador:

TR

Taxa efetiva anual:

5.116%

O simulador deve funcionar para qualquer financiamento do BB que utilize
este mesmo layout de extrato.

---

# Objetivos

O software deverá ser capaz de:

- ler o CSV
- validar os dados
- reconstruir o contrato
- calcular a TR histórica
- calcular a taxa efetiva mensal
- projetar parcelas futuras
- gerar gráficos
- exportar CSV
- gerar relatórios
- simular amortizações extraordinárias
- comparar estratégias e planejar metas de amortização

---

# Filosofia

Nunca utilizar valores fixos.

Todo cálculo deve ser obtido a partir dos dados do contrato.

Sempre preferir reproduzir exatamente a matemática utilizada pelo Banco do Brasil.

Sempre que possível utilizar os próprios dados históricos para calibrar o modelo.

---

# Arquitetura

O projeto será dividido em módulos independentes.

simulador/

    leitor.py
    reconstrucao.py
    parcelas.py
    calibracao.py
    projecao.py
    amortizacao.py
    comparacao.py
    planejamento.py
    relatorio.py
    graficos.py
    exportacao.py
    logging.py

Cada módulo deve possuir responsabilidade única.

---

# Regras

Nunca misturar:

- leitura
- cálculos
- exportação
- interface

Cada responsabilidade deve possuir seu próprio módulo.

---

# Digital Twin

O simulador deve reconstruir todas as parcelas já pagas.

Após reconstruir:

comparar

valor calculado

versus

valor existente no CSV.

Caso exista divergência significativa,
ajustar automaticamente os parâmetros de calibração.

Somente após esta validação
projetar as parcelas futuras.

---

# Simulações

O sistema deverá suportar:

- redução de prazo
- redução de prestação
- amortizações extraordinárias
- amortizações recorrentes
- TR constante
- TR variável
- cenários personalizados

---

# Linha de comando

O projeto utiliza Typer na CLI. Os comandos disponíveis são `validar`,
`projetar`, `relatorio`, `graficos`, `amortizar`, `comparar` e `planejar`.
O nível de diagnóstico pode ser definido antes do comando com
`--log-level DEBUG|INFO|WARNING|ERROR`.

Exemplos:

uv run python main.py projetar

uv run python main.py relatorio

O comando `projetar` aceita `--saida` para exportar o CSV da projeção.
`comparar` aceita múltiplas estratégias nomeadas e `planejar` encontra o aporte
mínimo para metas de quitação ou prestação.

---

# Qualidade

Todo código deve possuir:

- type hints
- docstrings
- logging
- testes unitários

Utilizar:

black

ruff

pytest

mypy

---

# Bibliotecas

Preferencialmente utilizar:

pandas

numpy

matplotlib

typer

rich

scipy

pytest

pydantic

---

# Objetivo futuro

Criar uma aplicação Streamlit onde o usuário apenas faça upload
do PDF do Banco do Brasil.

Fluxo esperado:

PDF

↓

extração automática

↓

CSV

↓

Reconstrução

↓

Simulação

↓

Relatórios

↓

Dashboard

---

# Restrições

Nunca alterar os dados históricos do contrato.

As projeções devem ser geradas em novos DataFrames.

O CSV original deve permanecer imutável.

---

# Testes

Sempre validar:

- taxa mensal
- cálculo da TR
- cálculo dos juros
- saldo devedor
- amortização
- projeção
- economia de juros
- redução de prazo

Os testes devem utilizar dados reais do extrato.

---

# Estilo

Código simples.

Funções pequenas.

Alta legibilidade.

Baixo acoplamento.

Alta coesão.

Evitar duplicação.

Documentar fórmulas matemáticas.
