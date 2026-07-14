# Backend FastAPI opcional

Este backend fornece uma interface Swagger opcional para as operacoes da Etapa 1.

Ele nao substitui a entrega oficial em SQL. O schema do banco, os dados de teste,
os exemplos de CRUD e as consultas analiticas continuam no diretorio `database/`.

## Requisitos

- Python 3.11+
- PostgreSQL em execucao com o schema da Etapa 1 carregado
- Dependencias listadas em `backend/requirements.txt`

## Configuracao

A partir da raiz do repositorio:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edite o arquivo `.env` ou defina `DATABASE_URL` no terminal caso usuario, senha,
host ou nome do banco sejam diferentes.

Conexao padrao:

```text
postgresql://postgres:postgres@localhost:5432/hospital_management_db
```

## Executar

```bash
uvicorn app.main:app --reload --env-file .env
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

JSON OpenAPI:

```text
http://127.0.0.1:8000/openapi.json
```

## Grupos disponiveis

- `Pacientes`: listar, criar, atualizar e listar atendimentos por paciente.
- `Atendimentos`: criar atendimentos e gerenciar procedimentos realizados.
- `Cadastros auxiliares`: criar/listar residentes, preceptores, unidades, procedimentos e escalas.
- `Consultas`: consultas analiticas exigidas na Etapa 1.
- `Validacao`: validacao dos dados minimos exigidos no enunciado.

## Escopo academico

Esta API usa SQL diretamente por meio do `psycopg`. Ela nao usa ORM de proposito,
preservando o requisito da Etapa 1 de trabalhar com SQL puro.
