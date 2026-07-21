# Simulador de Financiamento BB

Projeto para reconstrução e simulação de financiamentos imobiliários do Banco do Brasil.

O objetivo é criar um modelo matemático do contrato capaz de reproduzir o comportamento do financiamento e projetar as parcelas futuras.

---

# Estado atual

O projeto está na versão 1.3. A importação, validação, reconstrução histórica,
projeção, relatórios, gráficos, simulações de amortização e planejamento por
metas estão disponíveis pela linha de comando. O dashboard Streamlit oferece o
mesmo fluxo principal por upload de CSV ou PDF textual e pode ser executado em
um contêiner Docker otimizado. A suíte padrão não depende de PDFs privados e a
versão 1.3 atende ao gate mínimo de 90% de cobertura.

A reconstrução histórica preserva os valores reportados pelo banco e expõe
diagnósticos de juros, prestação e saldo. A projeção parte da parcela 126 e,
por padrão, usa a média das últimas 12 TRs válidas; também aceita uma TR mensal
personalizada. A versão 1.2 também inclui a conversão de PDF textual para CSV,
estratégias recorrentes e downloads de resultados no dashboard. A suíte de
regressão exige cobertura mínima de 90%.

---

# Dados de referência

`extrato.csv` é o único extrato de referência versionado no projeto. PDFs de
extratos bancários não são armazenados no repositório e são ignorados pelo Git
por motivos de privacidade.

Para usar a conversão ou o dashboard, forneça localmente o seu próprio PDF
textual do Banco do Brasil. A aplicação lê esse arquivo sem alterá-lo e gera um
CSV novo e validado em um caminho separado.

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

# Docker

Com Docker Engine e Docker Compose v2 instalados:

```bash
mkdir -p dados
docker compose up --build -d
```

Acesse `http://localhost:8501`. Para acompanhar ou encerrar o serviço:

```bash
docker compose logs -f simulador
docker compose down
```

A CLI também está disponível no contêiner:

```bash
docker compose run --rm simulador python main.py validar
docker compose run --rm simulador python main.py projetar
```

Arquivos particulares devem ficar em `dados/`, diretório ignorado pelo Git e
montado como `/dados`. O guia completo, incluindo conversão de PDF, portas,
UID/GID e execução sem Compose, está em
[docs/desenvolvimento/docker.md](docs/desenvolvimento/docker.md).

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

Extrair e validar um CSV a partir do PDF do Banco do Brasil:

```bash
uv run python main.py extrair-pdf \
  --pdf /caminho/para/seu_extrato.pdf \
  --saida extrato_extraido.csv
```

O PDF informado é um arquivo local do usuário e não deve ser adicionado ao
repositório.

Como não existe PDF distribuído com o projeto, `--pdf` é obrigatório no comando
`extrair-pdf`.

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

# Dashboard

Inicie a interface web local com:

```bash
uv run streamlit run dashboard.py
```

Envie um único CSV ou um PDF textual fornecido localmente por você. O dashboard
processa o upload em diretório temporário, sem versionar ou alterar o PDF, e
oferece resumo, projeção, seis
gráficos, download de CSV e relatório em Markdown. Em **Simulações avançadas**
é possível testar aportes únicos, mensais ou anuais, com redução de prazo ou de
prestação, e planejar o menor aporte para uma meta de quitação ou prestação.
Para aportes recorrentes, informe também o último aporte. A tabela do
planejamento de quitação mostra as parcelas recalculadas até a data-meta.

Em **Simular e comparar**, a tabela web apresenta somente número da parcela,
data, saldo corrigido, prestação total, saldo final, economia na prestação e
redução do saldo. Os dois comparativos representam cenário-base menos simulação;
valores positivos indicam economia ou redução.

---

# Roadmap

A documentação detalhada está em [docs/index.md](docs/index.md). A versão 1.0 é
a primeira versão estável; a versão 1.2 consolida o dashboard e a 1.3 adiciona
a execução otimizada em Docker. A calibração avançada permanece como evolução
futura.

---

# Testes do conversor PDF

A suíte padrão não depende de documentos bancários reais. Ela simula a camada de
leitura do PDF a partir das 164 linhas anonimizadas de `extrato.csv` e valida o
parser, a conversão, a CLI e o upload temporário.

Para executar também o smoke test opcional com um PDF textual local:

```bash
EXTRATO_PDF_TESTE=/caminho/para/seu_extrato.pdf \
  uv run --group dev pytest testes/test_extrator_pdf.py
```

O arquivo indicado permanece fora do repositório e não é copiado pelos testes.

---

# Licença

MIT
