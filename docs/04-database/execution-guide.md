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
CREATE DATABASE hospital_management;
\q
```

## Fluxos de execucao

Os scripts sao separados em tres fluxos para que a validacao dos dados minimos
nao seja confundida com as operacoes de demonstracao, que alteram registros.

### 1. Instalar a base

```powershell
.\scripts\run-phase-01.ps1 setup
```

Equivalente em Bash:

```bash
bash scripts/run-phase-01.sh setup
```

Esse fluxo executa:

```text
psql -U postgres -d hospital_management -f database/schema/01-create-tables.sql
psql -U postgres -d hospital_management -f database/seeds/02-seed-data.sql
```

### 2. Validar os dados minimos

```powershell
.\scripts\run-phase-01.ps1 validate
```

Esse fluxo executa:

```text
psql -U postgres -d hospital_management -f database/queries/05-validation-counts.sql
```

### 3. Executar as demonstracoes

```powershell
.\scripts\run-phase-01.ps1 demo
```

Esse fluxo executa:

```text
psql -U postgres -d hospital_management -f database/queries/03-crud-queries.sql
psql -U postgres -d hospital_management -f database/queries/04-analytical-queries.sql
```

Para executar os tres fluxos em sequencia:

```powershell
.\scripts\run-phase-01.ps1 all
```

O diretorio `database/` e a fonte oficial dos scripts SQL da Etapa 1. Os
executores em `scripts/` apenas organizam a chamada desses arquivos.

## Ordem recomendada

1. Criar as tabelas.
2. Inserir os dados de teste.
3. Validar os dados minimos antes de alterar os dados.
4. Executar as demonstracoes de CRUD.
5. Executar as consultas analiticas.

## Funcao de cada script

- `database/schema/01-create-tables.sql`: cria o schema com PK, FK, CHECK, NOT NULL e UNIQUE.
- `database/seeds/02-seed-data.sql`: insere os dados minimos exigidos para a Etapa 1.
- `database/queries/05-validation-counts.sql`: verifica se os registros minimos exigidos existem.
- `database/queries/03-crud-queries.sql`: demonstra CRUD e consultas basicas usando apenas SQL.
- `database/queries/04-analytical-queries.sql`: demonstra consultas analiticas com joins, agregacoes e filtros.
