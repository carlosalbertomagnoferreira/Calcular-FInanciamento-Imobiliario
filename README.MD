# Simulador de Financiamento BB

Projeto para reconstrução e simulação de financiamentos imobiliários do Banco do Brasil.

O objetivo é criar um modelo matemático do contrato capaz de reproduzir o comportamento do financiamento e projetar as parcelas futuras.

---

# Estado atual

O projeto está na versão 1.0. A importação, validação, reconstrução histórica, projeção, relatórios, gráficos, simulações de amortização e planejamento por metas estão disponíveis pela linha de comando.

A reconstrução histórica preserva os valores reportados pelo banco e expõe diagnósticos de juros, prestação e saldo. A projeção parte da parcela 126 e, por padrão, usa a média das últimas 12 TRs válidas; também aceita uma TR mensal personalizada. A versão 1.0 consolida estratégias nomeadas, comparação de cenários, planejamento por metas, logging operacional e uma suíte de regressão com cobertura mínima de 90%.

---

# Dados de referência

`extrato319405086.pdf` é o extrato-base original. `extrato.csv` é o CSV de referência do projeto.

Esses arquivos não devem ser alterados pela aplicação. A extração definitiva do PDF será implementada posteriormente como um componente próprio, sem sobrescrever os dados de referência.

---

# Instalação

Com o [uv](https://docs.astral.sh/uv/) instalado, clone o repositório e sincronize o ambiente:

```bash
git clone <repositorio>

cd calcular_financiamento_apartamento

uv sync
```

O `uv` cria e gerencia automaticamente o ambiente virtual em `.venv`, usando a versão do Python definida em `.python-version` e as dependências bloqueadas em `uv.lock`.

Para incluir também as dependências de desenvolvimento:

```bash
uv sync --all-groups
```

---

# Ambiente

Python 3.13 é a versão oficial do projeto.

O `uv` é o único gerenciador de ambiente e dependências adotado. Não usamos `requirements.txt`, criação manual de `venv` ou instalação direta com `pip`.

---

# Linha de comando

Para diagnósticos operacionais, adicione `--log-level` antes do comando. Os
níveis aceitos são `DEBUG`, `INFO`, `WARNING` e `ERROR`; o padrão é `WARNING`.

```bash
uv run python main.py --log-level INFO validar
```

Validar o extrato e a sequência de parcelas:

```bash
uv run python main.py validar
```

Projetar as parcelas restantes:

```bash
uv run python main.py projetar
```

Para também salvar a projeção em um CSV compatível com planilhas brasileiras:

```bash
uv run python main.py projetar --saida projecao.csv
```

Gerar relatório em Markdown ou texto simples:

```bash
uv run python main.py relatorio
uv run python main.py relatorio --formato txt
```

Gerar os seis gráficos do histórico e da projeção:

```bash
uv run python main.py graficos --diretorio graficos
```

Simular uma amortização extraordinária com redução de prazo ou de prestação:

```bash
uv run python main.py amortizar --valor 10000 --data 2026-08-10 --modo prazo
uv run python main.py amortizar --valor 10000 --data 2026-08-10 --modo parcelas
```

Para aportes recorrentes, use `--frequencia mensal` ou `--frequencia anual` com
`--ate`. Para uma agenda programada, repita `--amortizacao AAAA-MM-DD:VALOR`.
Datas informadas fora do dia 10 são aplicadas no vencimento daquele mês; datas
anteriores à primeira parcela projetada ou posteriores à quitação são rejeitadas.
O comando informa juros economizados e saldos antes/depois do aporte; no modo
`prazo`, também mostra o prazo abatido, e no modo `parcelas`, compara as cinco
próximas prestações. Em aportes recorrentes, o saldo após amortizar é o saldo na
data final informada em `--ate`.

Para comparar estratégias nomeadas, repita `--estrategia` no formato
`NOME:VALOR:DATA:MODO[:FREQUENCIA:ATE]`:

```bash
uv run python main.py comparar \
  --estrategia 'Prazo:10000:2026-08-10:prazo' \
  --estrategia 'Mensal:500:2026-08-10:prestacao:mensal:2026-10-10'
```

Para encontrar o menor aporte que quite o contrato até uma data, use:

```bash
uv run python main.py planejar --meta-quitacao 2045-02-10 --data 2026-08-10
uv run python main.py planejar --meta-prestacao 600 --data 2026-08-10 --modo prestacao
```

Em recorrências de planejamento, a data de `--meta-quitacao` também é usada
como última data do aporte quando `--ate` não for informado. Use `--ate` apenas
para encerrar os aportes antes da meta. Para a meta de prestação recorrente,
`--ate` é obrigatório, pois não há uma data-meta que determine o fim dos
aportes.

---

# Roadmap

A documentação detalhada está em [docs/index.md](docs/index.md). A versão 1.0 é a primeira versão estável; a calibração avançada permanece como evolução futura.

---

# Licença

MIT
