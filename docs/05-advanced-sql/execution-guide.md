# Guia de execucao da Etapa 2

Os recursos avancados da Etapa 2 estao implementados e validados.

## Banco oficial

```text
hospital_management
```

## Pre-requisitos

- PostgreSQL instalado e em execucao.
- Banco `hospital_management` criado.
- Scripts da Etapa 1 executados.

## Preparar a base

A partir da raiz do projeto:

```bash
psql -U postgres -d hospital_management -f database/schema/01-create-tables.sql
psql -U postgres -d hospital_management -f database/seeds/02-seed-data.sql
psql -U postgres -d hospital_management -f database/queries/05-validation-counts.sql
```

## Executar recursos da Etapa 2

Execute:

```bash
psql -U postgres -d hospital_management -f database/migrations/phase-02.sql
```

O integrador usa `ON_ERROR_STOP`, portanto qualquer erro interrompe a execucao.
A migracao estrutural tambem usa uma transacao: em caso de falha, nenhuma
alteracao parcial e mantida.

## Ordem interna

O arquivo `database/migrations/phase-02.sql` sera responsavel por chamar, nesta
ordem:

1. Migracao estrutural.
2. Triggers.
3. Functions e procedures.
4. Views.
5. Consultas de transacao e validacao avancada.

Todos os itens estao implementados. O cenario concorrente usa duas sessoes
SQLAlchemy e esta documentado em `docs/06-orm/concurrency.md`.

## Validar a estrutura

Apos executar o integrador, verifique:

```sql
SELECT id_atendimento, id_unidade
FROM atendimento
ORDER BY id_atendimento;

SELECT
    id_atendimento,
    id_procedimento,
    data_hora_inicio
FROM procedimento_realizado
ORDER BY id_atendimento, data_hora_inicio;

SELECT id_procedimento, media_tempo_procedimento
FROM procedimento
ORDER BY id_procedimento;

\d internacao
\d auditoria_atendimento
```

## Validar os triggers

Execute:

```bash
psql -U postgres -d hospital_management \
  -f database/queries/06-validation-triggers.sql
```

O teste verifica:

1. Bloqueio de sobreposicao de escala entre unidades.
2. Auditoria de `INSERT`, `UPDATE` e `DELETE` em atendimento.
3. Atualizacao da media depois de inserir um procedimento realizado.

Todos os dados criados pelo teste sao revertidos com `ROLLBACK`.

## Validar as stored procedures

Execute:

```bash
psql -U postgres -d hospital_management \
  -f database/queries/07-validation-procedures.sql
```

O teste cobre:

1. Cadastro atomico de atendimento com dois procedimentos.
2. Rollback completo quando um procedimento e invalido.
3. Calculo do tempo medio de espera de todas as unidades.
4. Reajuste valido de escala.
5. Bloqueio de reajuste conflitante.

Os dados criados pela validacao tambem sao revertidos no final.

## Validar as views

Execute:

```bash
psql -U postgres -d hospital_management \
  -f database/queries/08-validation-views.sql
```

O teste cobre:

1. Internacao mais recente ainda ativa.
2. Supervisao inativa e preceptor sem titulacao de doutor.
3. Totais, medias e procedimentos mais comuns por mes e unidade.

Os dados auxiliares sao revertidos ao final.

## Swagger opcional

O Swagger continua opcional. Ele pode ser usado para demonstrar endpoints que
consomem views, procedures ou consultas avancadas, mas a entrega principal da
Etapa 2 deve continuar documentada em SQL.
