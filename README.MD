# Simulador de Financiamento BB

Projeto para reconstrução e simulação de financiamentos imobiliários do Banco do Brasil.

O objetivo é criar um modelo matemático do contrato capaz de reproduzir o comportamento do financiamento e projetar as parcelas futuras.

---

# Funcionalidades

- Leitura do extrato em CSV
- Reconstrução do contrato
- Cálculo da TR histórica
- Cálculo da taxa efetiva mensal
- Projeção das parcelas restantes
- Simulação de amortizações extraordinárias
- Comparação entre redução de prazo e redução de prestação
- Exportação para CSV
- Geração de gráficos
- Relatórios financeiros

---

# Estrutura

```
financiamento_bb/

dados/
extrato.csv

simulador/

graficos/

testes/

main.py

README.md

AGENT.md
```

---

# Instalação

```bash
git clone <repositorio>

cd financiamento_bb

python -m venv .venv

source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\activate
```

Instale as dependências

```bash
pip install -r requirements.txt
```

---

# Executando

Projetar financiamento

```bash
python main.py projetar
```

Gerar relatório

```bash
python main.py relatorio
```

Gerar gráficos

```bash
python main.py graficos
```

Simular amortização

```bash
python main.py amortizar --valor 10000
```

Redução de prazo

```bash
python main.py amortizar --valor 10000 --reduzir-prazo
```

Redução da prestação

```bash
python main.py amortizar --valor 10000 --reduzir-parcela
```

---

# Arquivos gerados

```
dados/projecao.csv

graficos/

saldo_devedor.png

prestacoes.png

juros.png

tr.png

relatorio.txt
```

---

# Roadmap

## Fase 1

- Conversão PDF → CSV

## Fase 2

- Reconstrução do contrato

## Fase 3

- Projeção das parcelas

## Fase 4

- Simulação de amortizações

## Fase 5

- Dashboard Streamlit

## Fase 6

- Comparação entre contratos

## Fase 7

- Suporte a outros bancos

---

# Licença

MIT
