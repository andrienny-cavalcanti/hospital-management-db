# Views

Diretorio oficial das views da Etapa 2.

## Arquivos

- `01-create-views.sql`: cria as tres views exigidas no enunciado.

## Views implementadas

- `vw_pacientes_internados`: internacoes mais recentes ainda sem saida.
- `vw_residentes_sem_supervisor`: escalas com supervisao inativa ou preceptor
  sem titulacao de doutor.
- `vw_estatisticas_atendimentos_mensal`: totais, duracao media e procedimentos
  mais comuns por mes e unidade.

## Validacao

Depois de executar `database/migrations/phase-02.sql`:

```bash
psql -U postgres -d hospital_management \
  -f database/queries/08-validation-views.sql
```

O teste cria internacoes auxiliares, altera temporariamente uma supervisao e
valida as agregacoes mensais. Todas as mudancas terminam com `ROLLBACK`.
