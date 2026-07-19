# Simulador de Financiamento BB

Projeto para reconstrução e simulação de financiamentos imobiliários do Banco do Brasil.

O objetivo é criar um modelo matemático do contrato capaz de reproduzir o comportamento do financiamento e projetar as parcelas futuras.

---

# Estado atual

O projeto está na versão 0.8. A importação, validação, reconstrução histórica, projeção, relatórios, gráficos e simulações de amortização estão disponíveis pela linha de comando.

A reconstrução histórica preserva os valores reportados pelo banco e expõe diagnósticos de juros, prestação e saldo. A projeção parte da parcela 126 e, por padrão, usa a média das últimas 12 TRs válidas; também aceita uma TR mensal personalizada. Gráficos e amortizações são funcionalidades planejadas para versões posteriores.

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

---

# Roadmap

O roadmap detalhado está em [ROADMAP.md](ROADMAP.md). As próximas evoluções incluem calibração avançada e comparação de cenários.

---

# Licença

MIT
