# Migrations

Diretorio usado para scripts integradores de evolucao do banco.

Na Etapa 1, a criacao do schema continua sendo feita pelo script
`database/schema/01-create-tables.sql`.

Na Etapa 2, o arquivo `phase-02.sql` sera o ponto unico para executar os
recursos avancados, como views, functions, procedures, triggers e exemplos de
transacao.

## Arquivos atuais

- `phase-02.sql`: ponto de entrada executado pelo `psql`.
- `01-phase-02-structural.sql`: evolucao estrutural aplicada sobre a Etapa 1.

O script estrutural e transacional e pode ser reaplicado. Ele cria ou completa
as estruturas necessarias para as procedures, triggers e views da Etapa 2.
