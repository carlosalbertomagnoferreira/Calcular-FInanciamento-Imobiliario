# Roadmap
## Simulador de Financiamento Imobiliário Banco do Brasil

Versão do documento: 1.2

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
- pyproject.toml
- uv.lock
- Definição do Python 3.13 como versão oficial
- Dados de referência (PDF e CSV experimental)

### Critério de aceite

Projeto executando:

```bash
uv run python main.py
```

---

# Versão 0.2
## Leitura do Extrato

Status: concluída.

### Objetivos

Entregar a primeira funcionalidade do produto: importar e validar, sem alterar, o CSV de referência.

### Entregas

Leitor CSV desacoplado da CLI.

Validação de:

- colunas
- tipos
- datas
- valores

Conversão de números brasileiros e datas para um DataFrame normalizado.

Tratamento explícito de duplicidades, campos vazios e saldos iguais a zero, sem ainda interpretar eventos financeiros ou calcular parcelas.

Testes unitários para o leitor e para cada regra de validação.

### Fora do escopo

- extração de PDF;
- reconstrução financeira;
- cálculo de TR, juros, amortização ou saldo;
- calibração, projeção e CLI.

### Critério

Leitura do CSV de referência e de qualquer CSV que cumpra o contrato de colunas, sem alterar o arquivo de origem e com erros de validação compreensíveis.

---

# Versão 0.3
## Reconstrução do Contrato

Status: concluída.

### Objetivos

Reconstruir todos os eventos históricos, preservando os valores reportados pelo extrato.

### Entregas

Calcular:

- taxa mensal
- juros
- amortização
- saldo
- TR

Registrar diagnósticos de diferença de juros, prestação e saldo, sem forçar uma recorrência PRICE antes da calibração.

### Critério

Reconstrução dos 164 eventos do CSV de referência, sem alterar o extrato de origem.

---

# Versão 0.4
## Calibração

Status: concluída com calibração avançada adiada.

### Objetivos

Comparar cálculos com o contrato real.

### Entregas

Calcular erro percentual.

Classificar eventos elegíveis e gerar relatório auditável de métricas.

Ajustar parâmetros somente após validar que os desvios não decorrem de componentes ou eventos não classificados.

Parâmetros candidatos:

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

Status: concluída.

### Objetivos

Projetar todas as parcelas futuras.

### Entregas

Gerar DataFrame de projeção com cenário padrão de média das últimas 12 TRs válidas ou TR personalizada.

Permitir a exportação opcional do resultado em CSV pelo comando `projetar --saida`.

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

Status: concluída.

### Objetivos

Criar relatórios financeiros.

### Entregas

Resumo do contrato.

Saldo atual.

Saldo projetado.

Total pago.

Total restante.

Economia de juros (entrega da versão 0.8, quando houver cenário de amortização para comparação).

Data prevista de quitação.

---

# Versão 0.7
## Gráficos

Status: concluída.

### Objetivos

Visualização.

### Entregas

Saldo devedor.

Prestação.

TR.

Juros.

Amortização.

Evolução do contrato.

Os seis gráficos são exportados em PNG pelo comando `graficos --diretorio`.

---

# Versão 0.8
## Simulação de Amortizações

Status: concluída.

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

O comando `amortizar` compara o cenário original e o amortizado, informando
juros economizados e saldo antes/depois do aporte. No modo de prazo, também
informa o prazo abatido; nos modos de prestação e parcelas, compara as cinco
próximas prestações. Datas são normalizadas para o vencimento mensal e validadas
contra o prazo do contrato; em recorrências, o saldo após amortizar refere-se à
data final de `--ate`.

---

# Versão 0.9 — concluída
## Planejamento de Metas e Estratégias

### Objetivos

Transformar projeções em informações acionáveis para decisão financeira.

Para reduzir risco e permitir entregas incrementais, a versão será executada em
quatro subfases. As fases 0.9.2 e 0.9.3 poderão ser desenvolvidas em paralelo
após a consolidação da base compartilhada da 0.9.1.

### 0.9.1 — Base de estratégias — concluída

- Consolidar o modelo de estratégia de amortização, frequência e agenda de
  aportes.
- Fazer `amortizar` e `comparar` consumirem as mesmas regras de criação,
  normalização e validação da agenda.
- Remover duplicações de regras de negócio e ampliar os testes dessa base.

### 0.9.2 — Comparação de cenários — concluída

- Comparar o cenário-base e múltiplas estratégias de amortização em uma tabela.
- Informar aporte total, juros economizados, desembolso futuro, quitação, prazo,
  prestação e saldo para cada estratégia.

### 0.9.3 — Meta de quitação — concluída

- Encontrar, por busca numérica, o menor aporte único, mensal ou anual para
  quitar até uma data desejada.
- Retornar resultado nulo quando o cenário-base já atender à meta e uma
  explicação clara para metas inviáveis.

### 0.9.4 — Meta de prestação — concluída

#### 0.9.4.1 — Critério de avaliação — concluída

- Avaliar a primeira parcela posterior ao primeiro aporte normalizado.
- Considerar a prestação completa, incluindo acessórios contratuais.
- Considerar prestação de R$ 0,00 quando o aporte quitar o contrato antes da
  próxima parcela.

#### 0.9.4.2 — Busca do aporte mínimo — concluída

- Reutilizar a busca numérica em centavos para encontrar o menor aporte único,
  mensal ou anual que atenda à prestação-alvo.
- Retornar a prestação-base, a prestação obtida e a data avaliada.
- Tratar metas já atendidas, liquidação antecipada e entradas inviáveis.

#### 0.9.4.3 — Interface e validação — concluída

- Incluir `--meta-prestacao` no comando `planejar`, de forma exclusiva a
  `--meta-quitacao`.
- Exibir alvo, aporte mínimo, frequência, prestação-base e prestação obtida.
- Documentar o uso e cobrir cenários de CLI e recorrência com testes.

### Dependências de execução

```text
0.9.1 Base de estratégias
 ├── 0.9.2 Comparação de cenários
 └── 0.9.3 Meta de quitação
       └── 0.9.4 Meta de prestação
```

### Critério de aceite

Cada subfase deverá entregar comandos documentados, testes automatizados e
saída verificável. Para uma meta válida, apresentar o aporte mínimo e a
projeção resultante; para uma meta inviável, retornar uma explicação clara.


---

# Versão 1.0 — concluída
## Simulador Completo

### Objetivos

Primeira versão estável.

As funcionalidades financeiras, a CLI, a exportação e a documentação entregues
até a versão 0.9 compõem a base da primeira versão estável. A 1.0 concentra-se
em confiabilidade operacional, regressão e critérios formais de release.

### 1.0.1 — Observabilidade operacional — concluída

- Configurar logging padronizado e opt-in na CLI.
- Garantir mensagens de erro acionáveis sem poluir a saída de resultados.

### 1.0.2 — Regressão e qualidade — concluída

- Medir e elevar a cobertura automatizada para pelo menos 90%.
- Adicionar cenários de regressão com o extrato de referência e comandos da CLI.
- Consolidar validações financeiras já existentes como suíte de release.

### 1.0.3 — Documentação e release — concluída

- Revisar a documentação de uso e referência de comandos.
- Executar os critérios de qualidade e publicar a versão estável.

### Fora do escopo

- Calibração avançada permanece adiada até que os componentes históricos
  pendentes sejam explicados.
- Conversão de PDF textual é entregue na versão 1.1; PDFs escaneados ou com
  layouts distintos permanecem fora do escopo atual.

---

# Versão 1.1 — concluída
## Conversor PDF → CSV

### Objetivos

Eliminar necessidade de gerar CSV manualmente.

O comando `extrair-pdf` extrai as linhas financeiras do PDF textual, converte a
ordem visual dos componentes para o layout canônico e valida o CSV gerado antes
de disponibilizá-lo para simulação.

### Fluxo

PDF

↓

Extração

↓

CSV

↓

Simulação

---

# Versão 1.2 — concluída
## Dashboard

Tecnologia

Streamlit

### 1.2.1 — Fundação e upload — concluída

- Tela Streamlit para upload exclusivo de CSV ou PDF.
- Arquivos temporários, sem substituir as fontes de referência.
- Validação e mensagens de erro acionáveis.

### 1.2.2 — Análise básica — concluída

- Projeção, relatório financeiro e seis gráficos.

### 1.2.3 — Downloads e acabamento — concluída

- Download da projeção CSV e do relatório.
- Testes e documentação da interface.

### 1.2.4 — Simulações avançadas — concluída

- Amortização e comparação de estratégias na interface.
- Planejamento de metas de quitação e prestação, incluindo aportes únicos ou
  recorrentes e a projeção recalculada.

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
