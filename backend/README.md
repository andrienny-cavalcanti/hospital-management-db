# Backend FastAPI com SQLAlchemy

Este backend fornece uma interface Swagger para a implementacao ORM da Etapa 2.

As operacoes CRUD e as consultas da Etapa 1 foram reimplementadas com
SQLAlchemy 2.x, sem SQL textual nas rotas. Os scripts SQL continuam sendo a
fonte oficial para criar e evoluir o banco.

## Requisitos

- Python 3.11+
- PostgreSQL em execucao
- Schema, seeds e migracao da Etapa 2 aplicados
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

Prepare o banco antes de iniciar a API:

```bash
psql -U postgres -d hospital_management -f database/schema/01-create-tables.sql
psql -U postgres -d hospital_management -f database/seeds/02-seed-data.sql
psql -U postgres -d hospital_management -f database/migrations/phase-02.sql
```

Edite o arquivo `.env` ou defina `DATABASE_URL` no terminal caso usuario, senha,
host ou nome do banco sejam diferentes.

Conexao padrao:

```text
postgresql://postgres:postgres@localhost:5432/hospital_management
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
- `Consultas`: consultas analiticas e demonstracao de lazy/eager loading.
- `Validacao`: validacao dos dados minimos exigidos no enunciado.
- `Recursos avancados`: internacoes, views, auditoria e stored procedures
  consumidas pela interface web.

## Arquitetura ORM

- `app/models.py`: 12 classes mapeadas e seus relacionamentos.
- `app/db.py`: engine, fabrica de sessoes e dependencia transacional.
- `app/serializers.py`: conversao das entidades para respostas da API.
- `app/routes/`: CRUD e consultas usando `select()`, `Session` e a DSL ORM.

O endpoint abaixo demonstra as duas estrategias de carregamento:

```text
GET /consultas/demonstracao-carregamento/{id_atendimento}?estrategia=eager
GET /consultas/demonstracao-carregamento/{id_atendimento}?estrategia=lazy
```

Consultas avancadas:

```text
GET /consultas/avancadas/preceptores-pacientes-flamenguistas
GET /consultas/avancadas/ultimo-atendimento-pacientes
GET /consultas/avancadas/percentual-risco-alto-residentes
```

## Validacao

O smoke test usa a base completa da Etapa 2:

```powershell
$env:PYTHONPATH = "backend"
.\backend\.venv\Scripts\python.exe backend\tests\orm_smoke.py
```

O teste cobre mapeamento, relacionamentos, transacoes, CRUD, consultas
analiticas, consultas avancadas e lazy/eager loading.

## Concorrencia

O endpoint de criacao de escala usa lock pessimista no residente antes de
verificar conflitos. A demonstracao com duas transacoes pode ser executada com:

```powershell
$env:PYTHONPATH = "backend"
.\backend\.venv\Scripts\python.exe backend\tests\concurrency_demo.py
```

O resultado e a explicacao do mecanismo estao em
`docs/06-orm/concurrency.md`.
