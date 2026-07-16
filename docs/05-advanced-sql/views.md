# Views da Etapa 2

As views estao implementadas em `database/views/01-create-views.sql`.

## Pacientes internados

`vw_pacientes_internados` seleciona a internacao mais recente de cada paciente
e retorna somente aquelas sem `data_hora_saida`.

```sql
SELECT *
FROM vw_pacientes_internados
ORDER BY data_hora_entrada;
```

A view apresenta identificacao do paciente, convenio, grupo sanguineo, unidade
e data de entrada.

## Residentes sem supervisor

`vw_residentes_sem_supervisor` considera uma escala irregular quando:

- `supervisao_ativa` e falsa; ou
- a titulacao do preceptor nao comeca com `doutor`.

Cada linha representa uma escala que exige revisao e inclui a coluna `motivo`.

```sql
SELECT residente, preceptor, titulacao, motivo
FROM vw_residentes_sem_supervisor
ORDER BY data_plantao, turno;
```

## Estatisticas mensais

`vw_estatisticas_atendimentos_mensal` agrupa por mes e unidade, retornando:

- total de atendimentos;
- media de duracao em minutos;
- array JSONB dos procedimentos mais comuns.

Quando ha empate, todos os procedimentos na primeira posicao sao preservados.
A frequencia usa a soma de `procedimento_realizado.quantidade`.

```sql
SELECT *
FROM vw_estatisticas_atendimentos_mensal
ORDER BY mes, unidade;
```
