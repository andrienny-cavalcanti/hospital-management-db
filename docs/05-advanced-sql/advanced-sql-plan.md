# Plano da Etapa 2 - SQL avancado

Esta etapa evolui a base entregue na Etapa 1 com recursos avancados de banco de
dados, mantendo o PostgreSQL como tecnologia principal e o banco oficial com o
nome `hospital_management`.

## Objetivos

- Criar views para consultas frequentes e relatorios.
- Criar functions e procedures para regras de negocio.
- Criar triggers para automatizar validacoes e auditoria.
- Demonstrar transacoes com `BEGIN`, `COMMIT` e `ROLLBACK`.
- Integrar parte dos recursos avancados ao Swagger opcional.
- Documentar a execucao da Etapa 2.

## Estrutura oficial

```text
database/views/          views da Etapa 2
database/procedures/     functions e procedures
database/triggers/       triggers e estruturas de auditoria
database/queries/        consultas avancadas e exemplos de transacao
database/migrations/     script integrador da Etapa 2
docs/05-advanced-sql/    documentacao da Etapa 2
docs/06-orm/             planejamento e implementacao ORM
```

## Ordem recomendada de implementacao

1. Migracao estrutural e backfill dos dados existentes.
2. Triggers e estruturas de auditoria.
3. Functions e procedures.
4. Views.
5. Exemplos de transacao e concorrencia.
6. Validacoes avancadas.
7. Integracao opcional com Swagger.
8. ORM com SQLAlchemy.

## Observacao sobre a Etapa 1

Os scripts da Etapa 1 continuam sendo a base do projeto. A Etapa 2 deve ser
executada depois de:

```bash
psql -U postgres -d hospital_management -f database/schema/01-create-tables.sql
psql -U postgres -d hospital_management -f database/seeds/02-seed-data.sql
```
