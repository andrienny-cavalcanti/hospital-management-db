# Optional FastAPI Backend

This backend provides an optional Swagger interface for Phase 01 operations.

It does not replace the official SQL delivery. The database schema, seed data,
CRUD examples and analytical queries remain in the `database/` directory.

## Requirements

- Python 3.11+
- PostgreSQL running with the Phase 01 schema loaded
- Dependencies from `backend/requirements.txt`

## Setup

From the repository root:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` or define `DATABASE_URL` in the terminal if your PostgreSQL user,
password, host or database name is different.

Default connection:

```text
postgresql://postgres:postgres@localhost:5432/hospital_management_db
```

## Run

```bash
uvicorn app.main:app --reload --env-file .env
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

OpenAPI JSON:

```text
http://127.0.0.1:8000/openapi.json
```

## Available groups

- `Pacientes`: list, create, update and list appointments by patient.
- `Atendimentos`: create appointments and manage performed procedures.
- `Cadastros auxiliares`: create/list residents, preceptors, units, procedures and schedules.
- `Consultas`: analytical queries required for Phase 01.
- `Validacao`: minimum data validation for the academic statement.

## Academic scope

This API uses SQL directly through `psycopg`. It intentionally does not use an
ORM, so the Phase 01 requirement of pure SQL remains preserved.
