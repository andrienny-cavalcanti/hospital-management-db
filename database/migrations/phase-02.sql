-- =============================================================
-- Etapa 2 - Script integrador
-- Banco oficial: hospital_management
-- =============================================================
--
-- Execute a partir da raiz do projeto:
--
-- psql -U postgres -d hospital_management -f database/migrations/phase-02.sql
--
-- Os caminhos abaixo sao relativos a este arquivo por meio de \ir.

\set ON_ERROR_STOP on

\echo 'Etapa 2: aplicando migracao estrutural...'
\ir 01-phase-02-structural.sql
\echo 'Etapa 2: migracao estrutural aplicada com sucesso.'

\echo 'Etapa 2: criando funcoes e triggers...'
\ir ../triggers/01-create-triggers.sql
\echo 'Etapa 2: funcoes e triggers criados com sucesso.'

\echo 'Etapa 2: criando stored procedures...'
\ir ../procedures/01-create-procedures.sql
\echo 'Etapa 2: stored procedures criadas com sucesso.'

\echo 'Etapa 2: criando views...'
\ir ../views/01-create-views.sql
\echo 'Etapa 2: views criadas com sucesso.'
