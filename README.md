# Banco de Dados de Gestao Hospitalar

Projeto academico de banco de dados para um Sistema de Gestao Hospitalar, desenvolvido para a disciplina de Banco de Dados.

O projeto foi organizado para apoiar duas etapas academicas:

- **Etapa 1 - Fundamentos:** modelagem relacional, schema SQL, dados de teste, consultas CRUD e consultas analiticas.
- **Etapa 2 - Recursos avancados:** stored procedures, triggers, views, ORM e controle de transacoes.

## Identidade do projeto

- **Contexto institucional:** Hospital Universitario Dra. Yuska Maritan Brito
- **Nome do repositorio:** `hospital-management-db`
- **Banco principal:** PostgreSQL
- **Status atual:** Etapa 1 concluida, com Swagger opcional para demonstracao

## Estrutura do repositorio

```text
Hospital-Management-System-DB
|-- .github
|   |-- ISSUE_TEMPLATE
|   `-- workflows
|-- database
|   |-- schema
|   |-- seeds
|   |-- queries
|   |-- migrations
|   |-- procedures
|   |-- triggers
|   |-- views
|   `-- backups
|-- diagrams
|   |-- conceptual
|   |-- exports
|   |-- logical
|   `-- physical
|-- docs
|   |-- 01-project
|   |-- 02-analysis
|   |-- 03-modeling
|   |-- 04-database
|   `-- 06-orm
|-- reports
|   |-- phase-01
|   `-- phase-02
|-- scripts
|-- sql
|-- backend
|-- frontend
|-- modelagem
|-- presentations
`-- README.md
```

## Entregaveis da Etapa 1

- Schema relacional completo do banco.
- Insercao de dados de teste.
- Operacoes CRUD usando SQL puro.
- Consultas basicas e analiticas.
- Documentacao do modelo relacional.
- Justificativa do DER com cardinalidades e especializacoes.
- Evidencia de normalizacao ate 3FN.
- Relatorio da Etapa 1.
- Exportacao do DER.

## Instalacao e execucao

A Etapa 1 usa **SQL puro**. Nenhum backend, frontend ou ORM e necessario para executar a entrega principal.

### Pre-requisitos

- PostgreSQL instalado e em execucao.
- `psql` disponivel no terminal.
- Usuario PostgreSQL com permissao para criar bancos e executar scripts.

### 1. Criar o banco de dados

Acesse o PostgreSQL:

```bash
psql -U postgres
```

Crie o banco:

```sql
CREATE DATABASE hospital_management_db;
\q
```

Se o banco ja existir e voce quiser recriar o schema, o script de criacao pode ser executado novamente, pois ele inicia removendo as tabelas do projeto com `CASCADE`.

### 2. Executar os scripts da Etapa 1

A partir da raiz do repositorio, execute os scripts nesta ordem:

```bash
psql -U postgres -d hospital_management_db -f database/schema/01-create-tables.sql
psql -U postgres -d hospital_management_db -f database/seeds/02-seed-data.sql
psql -U postgres -d hospital_management_db -f database/queries/05-validation-counts.sql
psql -U postgres -d hospital_management_db -f database/queries/03-crud-queries.sql
psql -U postgres -d hospital_management_db -f database/queries/04-analytical-queries.sql
```

O diretorio `database/` e a fonte oficial dos scripts SQL da Etapa 1. O diretorio `sql/` foi mantido apenas como ponteiro para evitar duplicacao de scripts.

### 3. Funcao de cada script

- `database/schema/01-create-tables.sql`: cria tabelas, chaves primarias, chaves estrangeiras, checks, constraints unicas e indices.
- `database/seeds/02-seed-data.sql`: insere os dados de teste exigidos no enunciado.
- `database/queries/05-validation-counts.sql`: valida se os dados minimos da Etapa 1 foram inseridos.
- `database/queries/03-crud-queries.sql`: demonstra CRUD e consultas basicas usando apenas SQL.
- `database/queries/04-analytical-queries.sql`: executa as consultas analiticas exigidas na Etapa 1.

### 4. Documentacao para avaliacao

- DER conceitual: `diagrams/conceptual/er-diagram.mmd`
- Guia de exportacao do DER: `diagrams/conceptual/README.md`
- Justificativa do DER: `docs/03-modeling/er-justification.md`
- Modelo relacional: `docs/03-modeling/relational-model.md`
- Evidencia de normalizacao: `docs/03-modeling/normalization-3nf.md`
- Guia de execucao: `docs/04-database/execution-guide.md`

## API Swagger opcional

O projeto tambem inclui um backend opcional com FastAPI em `backend/`, criado para facilitar a manipulacao dos dados pelo Swagger UI.

Essa API e apenas uma interface de apoio. A entrega oficial da Etapa 1 continua sendo formada pelos scripts SQL puros em `database/`.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --env-file .env
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Objetivo academico

Este repositorio demonstra projeto e implementacao de banco de dados por meio de modelagem conceitual, logica e fisica, normalizacao, operacoes SQL, consultas analiticas e preparacao para recursos avancados de banco de dados.
