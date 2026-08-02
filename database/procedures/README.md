# Stored Procedures

Diretorio oficial das stored procedures da Etapa 2.

## Arquivos

- `01-create-procedures.sql`: cria as tres procedures exigidas no enunciado.

## Procedures implementadas

- `sp_registrar_atendimento_completo`: recebe atendimento e procedimentos em
  JSONB e grava tudo atomicamente.
- `sp_calcular_tempo_medio_espera`: retorna, em JSONB, a media de espera por
  unidade.
- `sp_reajustar_escala`: move as escalas de um residente entre datas e turnos,
  com bloqueio das linhas e verificacao de conflito.

## Validacao

Depois de executar `database/migrations/phase-02.sql`:

```bash
psql -U postgres -d hospital_management \
  -f database/queries/07-validation-procedures.sql
```

O teste demonstra cadastro completo, rollback por procedimento invalido,
calculo de espera, reajuste valido e rejeicao de conflito. Todas as alteracoes
de teste terminam com `ROLLBACK`.
