# Execução com Docker

O contêiner executa o dashboard Streamlit por padrão e também disponibiliza a
CLI. A imagem usa Python 3.13, instala somente dependências de produção a partir
do `uv.lock` e executa como usuário sem privilégios.

## Requisitos

- Docker Engine 24 ou superior;
- Docker Compose v2, acessível pelo comando `docker compose`.

## Dashboard

Crie o diretório local reservado aos dados privados e suba o serviço:

```bash
mkdir -p dados
docker compose up --build -d
```

Acesse `http://localhost:8501`. O PDF ou CSV é enviado pelo navegador,
processado em `/tmp` e descartado ao final da operação. PDFs são excluídos do
contexto de build e ignorados pelo Git.

Comandos operacionais:

```bash
docker compose ps
docker compose logs -f simulador
docker compose down
```

Para publicar outra porta:

```bash
APP_PORT=8080 docker compose up -d
```

## CLI

O CSV de referência já está presente na imagem:

```bash
docker compose run --rm simulador python main.py validar
docker compose run --rm simulador python main.py projetar
```

Para trabalhar com arquivos particulares, coloque-os em `dados/`, que é
ignorado pelo Git e montado no contêiner como `/dados`:

```bash
cp /caminho/para/seu_extrato.pdf dados/extrato.pdf
docker compose run --rm simulador python main.py extrair-pdf \
  --pdf /dados/extrato.pdf \
  --saida /dados/extrato_extraido.csv
```

O argumento `--pdf` é obrigatório porque nenhuma imagem Docker inclui um PDF de
referência.

Outros exemplos:

```bash
docker compose run --rm simulador python main.py projetar \
  --csv /dados/extrato_extraido.csv \
  --saida /dados/projecao.csv

docker compose run --rm simulador python main.py relatorio \
  --csv /dados/extrato_extraido.csv
```

Em Linux, se o usuário local não possuir UID/GID 1000, informe os valores para
que os arquivos gerados em `dados/` mantenham a propriedade correta:

```bash
CONTAINER_UID=$(id -u) CONTAINER_GID=$(id -g) \
  docker compose run --rm simulador python main.py projetar \
  --saida /dados/projecao.csv
```

Também é possível copiar `.env.example` para `.env` e ajustar esses valores. O
arquivo `.env` é ignorado pelo Git.

## Imagem sem Compose

```bash
docker build -t financiamento-bb:1.3.0 .
docker run --rm -p 8501:8501 \
  --read-only \
  --tmpfs /tmp:size=128m \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  financiamento-bb:1.3.0
```

## Decisões de otimização e segurança

- build em múltiplos estágios, com cache de downloads do `uv` somente no estágio
  de build e sem `uv`, bytecode pré-compilado ou ferramentas de desenvolvimento
  na imagem final;
- base `python:3.13-slim-bookworm` e ambiente virtual copiado do estágio de build;
- somente código e `extrato.csv` entram na imagem; testes, documentação, Git,
  PDFs e dados locais ficam fora do contexto;
- sistema de arquivos raiz somente leitura e `/tmp` efêmero limitado a 128 MiB;
- processo sem root, capabilities removidas e `no-new-privileges` habilitado;
- healthcheck no endpoint interno do Streamlit;
- limite padrão de upload de 20 MiB, configurável em `compose.yaml`.

## Atualização da imagem

Após alterar dependências ou código:

```bash
uv lock
docker compose build --pull
docker compose up -d
```

Use `docker compose build --no-cache` somente para diagnosticar problemas de
cache, pois ele torna builds recorrentes mais lentos.
