# Arquitetura do Projeto

Projeto:

Simulador de Financiamento Imobiliário Banco do Brasil

Versão:

1.2

---

# Objetivo da Arquitetura

O objetivo desta arquitetura é manter o código:

- modular
- desacoplado
- testável
- extensível
- reutilizável

Cada módulo deverá possuir responsabilidade única.

---

# Estrutura atual do Projeto

A estrutura abaixo representa a organização entregue até a versão 1.2. Os
arquivos de referência `extrato.csv` e `extrato319405086.pdf` permanecem na
raiz e não são modificados pela aplicação.

calcular_financiamento_apartamento/

```
├── main.py
├── dashboard.py
├── pyproject.toml
├── uv.lock
├── README.MD
├── AGENT.MD
├── CLAUDE.md
├── CHANGELOG.MD
│
├── simulador/
│   ├── __init__.py
│   ├── leitor.py
│   ├── entrada.py
│   ├── analise.py
│   ├── reconstrucao.py
│   ├── parcelas.py
│   ├── calibracao.py
│   ├── projecao.py
│   ├── amortizacao.py
│   ├── comparacao.py
│   ├── planejamento.py
│   ├── relatorio.py
│   ├── exportacao.py
│   ├── graficos.py
│   ├── calculos.py
│   ├── excecoes.py
│   └── logging.py
│
├── modelos/
│   ├── evento_historico.py
│   ├── projecao.py
│   ├── amortizacao.py
│   ├── comparacao.py
│   ├── planejamento.py
│   ├── calibracao.py
│   └── relatorio.py
│
├── testes/
│
└── docs/
    ├── index.md
    ├── produto/
    │   ├── spec.md
    │   └── roadmap.md
    ├── arquitetura/
    │   ├── arquitetura.md
    │   └── decisoes.md
    └── desenvolvimento/
        └── tarefas.md
```

---

# Fluxo Principal

```
main.py

↓

CLI

↓

Leitor CSV

↓

Validação

↓

Reconstrução

↓

Calibração

↓

Projeção

↓

Relatórios

↓

Gráficos

↓

Exportação
```

Nenhuma etapa deve acessar diretamente outra camada.

Sempre utilizar as interfaces definidas.

---

# Dependências

```
CLI

↓

Services

↓

Domain

↓

Models

↓

Utils
```

Nunca inverter dependências.

---

# Camadas

## CLI

Responsável apenas por:

- receber comandos
- interpretar argumentos
- chamar serviços

Nunca realizar cálculos.

---

## Leitor

Responsável por:

- importar CSV
- validar colunas
- converter tipos
- retornar DataFrame

Nunca calcular juros.

---

## Contrato

Representa o contrato financeiro.

Deve conter:

- taxa anual
- taxa mensal
- prazo
- parcelas
- saldo atual

Nenhum código de exportação.

---

## Price

Responsável apenas pelas fórmulas do Sistema PRICE.

Funções puras.

Sem acesso a arquivos.

---

## TR

Responsável pelos cálculos da TR.

Funções:

- calcular histórica
- calcular média
- calcular personalizada

---

## Projetor

Responsável por gerar parcelas futuras.

Recebe:

Contrato

↓

TR

↓

Configuração

↓

Retorna DataFrame

---

## Amortização

Responsável por:

- reduzir prazo
- reduzir prestação
- calcular economia

Não deve gerar gráficos.

---

## Relatório

Responsável apenas por produzir:

DataFrames

TXT

Markdown

Nunca imprimir diretamente.

---

## Exportador

Responsável por:

CSV

Excel

JSON

Parquet

Nunca calcular valores.

---

## Gráficos

Responsável apenas pela visualização.

Utilizar matplotlib.

Nunca modificar dados.

---

# Modelos

Utilizar dataclasses.

Exemplo:

Parcela

Contrato

Simulação

Resultado

Todos os modelos devem possuir type hints.

---

# Princípios

Toda regra de negócio deve ficar no domínio.

Nenhuma regra financeira pode existir na CLI.

Nenhuma regra financeira pode existir nos gráficos.

---

# DataFrames

Nunca modificar o DataFrame original.

Fluxo esperado:

CSV

↓

DataFrame Original

↓

DataFrame Limpo

↓

DataFrame Reconstruído

↓

DataFrame Projetado

↓

Exportação

Sempre utilizar cópias.

---

# Logging

Criar logger único.

Exemplo:

```
INFO

CSV carregado

125 parcelas encontradas

TR média calculada

Reconstrução iniciada

Reconstrução concluída

Projeção iniciada

Projeção concluída
```

---

# Configuração

Criar config.py

Centralizar:

Taxa anual

Prazo

Tolerâncias

Pastas

Arquivos

Nunca espalhar constantes pelo projeto.

---

# Estratégia

Utilizar Strategy Pattern para:

TR

Amortização

Projeção

No futuro poderão existir:

TR Histórica

TR Média

TR Zero

TR Manual

Sem alterar o restante do sistema.

---

# Factory

Criar Factory para:

Leitor

Exportador

Relatórios

Permitirá adicionar novos formatos.

---

# Dependency Injection

Sempre injetar dependências.

Exemplo:

Projetor

recebe

Contrato

TR Strategy

Logger

Nunca instanciar internamente.

---

# Testes

Cada módulo deverá possuir testes independentes.

Nunca testar múltiplos módulos simultaneamente.

Cobertura mínima:

90%

---

# Nomenclatura

Classes:

PascalCase

Funções:

snake_case

Constantes:

UPPER_CASE

Arquivos:

snake_case

---

# Type Hints

Obrigatórios.

Exemplo:

```
def calcular_prestacao(
    saldo: float,
    taxa: float,
    parcelas: int
) -> float:
```

---

# Docstrings

Utilizar padrão Google.

Exemplo:

```
def calcular_juros(...):
    """
    Calcula os juros da parcela.

    Args:
        saldo:
            Saldo corrigido.

        taxa:
            Taxa mensal.

    Returns:
        Valor dos juros.
    """
```

---

# Erros

Criar exceções específicas.

Exemplo:

CSVInvalidoError

ContratoInvalidoError

TRInvalidaError

ProjecaoError

Nunca utilizar Exception genérica.

---

# Evolução

Arquitetura preparada para:

PDF

↓

OCR

↓

Banco de Dados

↓

API REST

↓

Dashboard Streamlit

↓

FastAPI

↓

Suporte a outros bancos

↓

Múltiplos contratos

↓

Comparador de financiamentos

Sem necessidade de refatoração.

---

# Objetivo Final

O projeto deve evoluir para uma biblioteca reutilizável.

Exemplo:

```python
from financiamento_bb import Simulador

sim = Simulador("dados/extrato.csv")

sim.projetar()

sim.relatorio()

sim.graficos()

sim.amortizar(
    valor=10000,
    reduzir_prazo=True
)
```

A CLI será apenas uma interface dessa biblioteca.

Toda a lógica deverá permanecer reutilizável.
