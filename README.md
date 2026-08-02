# Banco de Dados de Gestao Hospitalar

Projeto academico de banco de dados para um Sistema de Gestao Hospitalar, desenvolvido para a disciplina de Banco de Dados.

O projeto foi organizado para apoiar duas etapas academicas:

- **Etapa 1 - Fundamentos:** modelagem relacional, schema SQL, dados de teste, consultas CRUD e consultas analiticas.
- **Etapa 2 - Recursos avancados:** stored procedures, triggers, views, ORM e controle de transacoes.

## Identidade do projeto

- **Contexto institucional:** Hospital Universitario Dra. Yuska Maritan Brito
- **Nome do repositorio:** `hospital-management-db`
- **Banco principal:** PostgreSQL
- **Status atual:** Etapas 1 e 2 concluidas e validadas

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
|   |-- 05-advanced-sql
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

## Implementacao atual da Etapa 2

- Migracao estrutural transacional e reaplicavel.
- Relacao entre atendimento e unidade.
- Registro do inicio dos procedimentos realizados.
- Estruturas de internacao e auditoria de atendimento.
- Media de tempo dos procedimentos preparada para atualizacao por trigger.
- Protecao estrutural contra conflito de escala por residente, data e turno.
- Triggers de sobreposicao de escala, auditoria e media implementados.
- Stored procedures de atendimento completo, espera e reajuste implementadas.
- Views de internacao, supervisao e estatisticas mensais implementadas.
- ORM SQLAlchemy com mapeamentos, CRUD, consultas e lazy/eager loading.
- Consultas ORM avancadas de supervisao, ultimo atendimento e risco.
- Concorrencia de escalas com lock pessimista, constraint e logs.

Guias e evidencias:

- `docs/05-advanced-sql/execution-guide.md`
- `docs/02-analysis/phase-02-requirements-matrix.md`
- `reports/phase-02/phase-02-report.pdf`
- `reports/phase-02/final-validation.md`

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
CREATE DATABASE hospital_management;
\q
```

Se o banco ja existir e voce quiser recriar o schema, o script de criacao pode ser executado novamente, pois ele inicia removendo as tabelas do projeto com `CASCADE`.

### 2. Executar os scripts da Etapa 1

A partir da raiz do repositorio, o fluxo completo pode ser executado no
PowerShell:

```powershell
.\scripts\run-phase-01.ps1 all
```

Ou em Bash:

```bash
bash scripts/run-phase-01.sh all
```

Os modos `setup`, `validate` e `demo` permitem executar separadamente a
instalacao, a validacao e as demonstracoes. Consulte `scripts/README.md` para
os parametros de banco e usuario.

O diretorio `database/` e a fonte oficial dos scripts SQL da Etapa 1. Os
executores apenas organizam a ordem de execucao.

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

## Executar e validar a Etapa 2

O executor completo aplica os recursos avancados e executa validacoes SQL,
ORM e concorrencia:

```powershell
.\scripts\run-phase-02.ps1 all
```

Atencao: o modo `all` recria as tabelas. Para validar uma base ja preparada:

```powershell
.\scripts\run-phase-02.ps1 validate
```

Modos adicionais: `setup`, `sql`, `orm` e `concurrency`.

## API Swagger com ORM

O backend FastAPI em `backend/` implementa a camada ORM exigida na Etapa 2 com
SQLAlchemy. As rotas de CRUD e consultas nao usam SQL textual.

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

## Interface web

O diretório `frontend/` contém um painel Next.js responsivo para operar as
funcionalidades do projeto: CRUD, atendimentos e procedimentos, equipe,
unidades, escalas, internações, stored procedures, views, relatórios e
auditoria.

Com a API em execução, abra um segundo terminal:

```powershell
cd frontend
npm install
npm run dev
```

Acesse:

```text
http://localhost:3000
```

A interface usa `http://127.0.0.1:8000` como API padrão. Esse endereço também
pode ser alterado e salvo no cabeçalho do painel.

## Objetivo academico

Este repositorio demonstra modelagem conceitual, logica e fisica, normalizacao,
SQL puro e avancado, triggers, stored procedures, views, ORM, transacoes e
controle de concorrencia.
