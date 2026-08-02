# Stored procedures da Etapa 2

As procedures estao implementadas em
`database/procedures/01-create-procedures.sql`.

## Registrar atendimento completo

`sp_registrar_atendimento_completo` recebe os dados do atendimento e um array
JSONB de procedimentos. Cada item deve informar:

- `id_procedimento`;
- `quantidade`;
- `tempo_real_minutos`;
- `data_hora_inicio`;
- `observacao`, opcional;
- `faturado`, opcional e falso por padrao.

Exemplo:

```sql
CALL sp_registrar_atendimento_completo(
    TIMESTAMP '2026-07-20 08:00',
    60,
    1,
    6,
    11,
    1,
    '[
        {
            "id_procedimento": 1,
            "quantidade": 1,
            "tempo_real_minutos": 30,
            "data_hora_inicio": "2026-07-20T08:10:00"
        }
    ]'::JSONB,
    NULL
);
```

O ultimo parametro retorna `id_atendimento`.

A procedure nao executa `COMMIT` internamente. O `CALL` e atomico: se um item
violar uma FK, CHECK ou chave unica, o atendimento, os procedimentos, a
auditoria e as medias produzidas naquele `CALL` sao revertidos.

## Calcular tempo medio de espera

```sql
CALL sp_calcular_tempo_medio_espera(NULL);
```

O parametro de saida e um array JSONB com uma entrada por unidade, incluindo
unidades sem atendimentos. O tempo e medido entre `atendimento.data_hora` e o
primeiro `procedimento_realizado.data_hora_inicio`.

## Reajustar escala

```sql
CALL sp_reajustar_escala(
    10,
    DATE '2026-07-14',
    'noite',
    DATE '2026-07-15',
    'tarde',
    0
);
```

O ultimo parametro retorna a quantidade de escalas alteradas. A procedure:

- bloqueia as linhas de origem com `FOR UPDATE`;
- verifica se o destino ja esta ocupado pelo residente;
- atualiza a data, o turno e o dia da semana;
- depende das constraints e do trigger de escala como protecao final.
