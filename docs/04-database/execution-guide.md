# Guia de execucao do banco

A Etapa 1 usa apenas SQL puro. Nenhum ORM, backend ou frontend e necessario para este fluxo de execucao.

## Pre-requisitos

- PostgreSQL instalado e em execucao.
- `psql` disponivel no terminal.
- Usuario PostgreSQL com permissao para criar bancos e executar scripts.

## Criar o banco

```bash
psql -U postgres
```

```sql
CREATE DATABASE hospital_management_db;
\q
```

## Executar os scripts

Execute os comandos a partir da raiz do repositorio:

```bash
psql -U postgres -d hospital_management_db -f database/schema/01-create-tables.sql
psql -U postgres -d hospital_management_db -f database/seeds/02-seed-data.sql
psql -U postgres -d hospital_management_db -f database/queries/05-validation-counts.sql
psql -U postgres -d hospital_management_db -f database/queries/03-crud-queries.sql
psql -U postgres -d hospital_management_db -f database/queries/04-analytical-queries.sql
```

O diretorio `database/` e a fonte oficial dos scripts SQL da Etapa 1. O diretorio `sql/` foi mantido apenas como ponteiro para essa estrutura.

## Ordem recomendada

1. Criar as tabelas.
2. Inserir os dados de teste.
3. Validar os dados minimos.
4. Executar as consultas CRUD.
5. Executar as consultas analiticas.

## Funcao de cada script

- `database/schema/01-create-tables.sql`: cria o schema com PK, FK, CHECK, NOT NULL e UNIQUE.
- `database/seeds/02-seed-data.sql`: insere os dados minimos exigidos para a Etapa 1.
- `database/queries/05-validation-counts.sql`: verifica se os registros minimos exigidos existem.
- `database/queries/03-crud-queries.sql`: demonstra CRUD e consultas basicas usando apenas SQL.
- `database/queries/04-analytical-queries.sql`: demonstra consultas analiticas com joins, agregacoes e filtros.
