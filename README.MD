# Simulador de Financiamento BB

Projeto para reconstrução e simulação de financiamentos imobiliários do Banco do Brasil.

O objetivo é criar um modelo matemático do contrato capaz de reproduzir o comportamento do financiamento e projetar as parcelas futuras.

---

# Estado atual

O projeto está na versão 0.5. A importação, validação, reconstrução histórica e projeção de parcelas futuras estão disponíveis. `main.py` continua sendo apenas o arquivo inicial criado pelo `uv`; uma interface de linha de comando será criada em etapa posterior.

A reconstrução histórica preserva os valores reportados pelo banco e expõe diagnósticos de juros, prestação e saldo. A projeção parte da parcela 126 e oferece TR média histórica ou personalizada. Relatórios, gráficos e amortizações são funcionalidades planejadas para versões posteriores.

---

# Dados de referência

`extrato319405086.pdf` é o extrato-base original. `extrato.csv` é o CSV de referência do projeto.

Esses arquivos não devem ser alterados pela aplicação. O `extrator2.py` é apenas uma prova de conceito; o extrator definitivo será implementado posteriormente como um componente próprio, sem sobrescrever os dados de referência.

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

Gerar relatório em Markdown ou texto simples:

```bash
uv run python main.py relatorio
uv run python main.py relatorio --formato txt
```

---

# Roadmap

O roadmap detalhado está em [ROADMAP.md](ROADMAP.md). A próxima versão será a 0.4: calibração do modelo contra o histórico.

---

# Licença

MIT
