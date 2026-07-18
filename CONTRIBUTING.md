# CONTRIBUTING.md

# Guia de Contribuição

Obrigado por contribuir com o projeto!

O objetivo deste projeto é construir um simulador de financiamentos do Banco do Brasil com foco em precisão matemática, qualidade de código e facilidade de manutenção.

---

# Filosofia

Prioridades do projeto:

1. Correção matemática
2. Clareza do código
3. Testabilidade
4. Performance
5. Extensibilidade

Nunca sacrificar a precisão dos cálculos por otimizações prematuras.

---

# Ambiente

Versão oficial do Python:

3.13

O ambiente e as dependências são gerenciados exclusivamente pelo `uv`:

```bash
uv sync --all-groups
```

---

# Ferramentas

Utilizamos:

- pandas
- numpy
- matplotlib
- typer
- rich
- pytest
- mypy
- ruff
- black

---

# Estrutura

Nunca adicionar lógica financeira em:

- CLI
- Exportadores
- Gráficos

Toda regra de negócio deve permanecer na camada de domínio.

---

# Padrão de Código

Seguir:

PEP8

Black

Ruff

MyPy

---

# Type Hints

Obrigatórios.

Exemplo:

```python
def calcular_juros(
    saldo: float,
    taxa: float
) -> float:
```

---

# Docstrings

Obrigatórias.

Utilizar padrão Google.

---

# Commits

Utilizar Conventional Commits.

Exemplos:

```
feat: adiciona cálculo da TR histórica

fix: corrige cálculo da amortização

test: adiciona testes do projetor

docs: atualiza README

refactor: simplifica cálculo dos juros
```

---

# Branches

main

↓

develop

↓

feature/nome

↓

Pull Request

---

# Pull Requests

Cada PR deverá:

- possuir descrição
- explicar motivação
- possuir testes
- atualizar documentação quando necessário

---

# Testes

Antes de enviar qualquer alteração execute:

```bash
uv run --group dev pytest
```

```bash
uv run --group dev ruff check .
```

```bash
uv run --group dev black --check .
```

```bash
uv run --group dev mypy .
```

Todos devem passar sem erros.

---

# Novos Recursos

Sempre abrir uma Issue antes de implementar grandes funcionalidades.

---

# Bugs

Ao reportar bugs informe:

- versão
- sistema operacional
- Python
- CSV utilizado
- mensagem de erro
- passos para reproduzir

---

# Performance

Evitar loops desnecessários.

Preferir operações vetorizadas do pandas quando possível.

---

# Logging

Utilizar logging.

Nunca utilizar print para depuração.

---

# Tratamento de Erros

Criar exceções específicas.

Evitar Exception genérica.

---

# Testes Automatizados

Todo cálculo financeiro deverá possuir testes.

Cobertura mínima:

90%

---

# Segurança

Nunca armazenar:

- dados bancários
- senhas
- tokens
- informações pessoais

Os arquivos de exemplo deverão ser anonimizados.

---

# Documentação

Toda funcionalidade nova deve atualizar:

- README
- SPEC
- ARCHITECTURE
- CHANGELOG (quando aplicável)

---

# Checklist antes do Merge

- [ ] Código compilando
- [ ] Testes aprovados
- [ ] Ruff sem erros
- [ ] Black executado
- [ ] MyPy aprovado
- [ ] Documentação atualizada
- [ ] PR revisado

---

# Visão de Longo Prazo

Este projeto deverá evoluir para uma biblioteca reutilizável para análise de financiamentos imobiliários, acompanhada de uma CLI, uma aplicação Streamlit e uma API REST.

Toda contribuição deve considerar essa visão para evitar soluções que dificultem a evolução futura.
