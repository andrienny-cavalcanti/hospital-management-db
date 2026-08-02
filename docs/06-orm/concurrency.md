# Concorrencia e transacoes com ORM

## Cenario

Duas transacoes tentam escalar o residente 6 na mesma data e turno, usando
unidades diferentes:

```text
TX-A -> unidade 1, residente 6, 2030-01-05, manha
TX-B -> unidade 2, residente 6, 2030-01-05, manha
```

Sem sincronizacao, as duas transacoes poderiam consultar a tabela `escala`
antes de qualquer uma confirmar e concluir que o horario estava livre.

## Lock pessimista

`backend/app/services/scheduling.py` executa uma consulta SQLAlchemy com
`with_for_update()` sobre a linha do residente:

```python
select(Residente).where(
    Residente.id_profissional == schedule.id_residente
).with_for_update()
```

A linha do residente e usada como ponto estavel de sincronizacao. Nao e
suficiente tentar bloquear a escala conflitante, pois essa linha ainda nao
existe quando as duas transacoes iniciam.

Depois de adquirir o lock, o servico:

1. verifica se ja existe escala na mesma data e turno;
2. adiciona a nova entidade;
3. executa `flush()` dentro da transacao;
4. deixa o chamador confirmar ou reverter.

O endpoint `POST /escalas` usa esse mesmo servico.

## Protecoes em camadas

O controle possui tres camadas:

1. `SELECT ... FOR UPDATE` serializa operacoes do mesmo residente.
2. `trg_check_sobreposicao_escala` expressa a regra de negocio no banco.
3. `uq_escala_residente_data_turno` impede inconsistencias mesmo se outro
   cliente ignorar o servico ORM.

O lock evita a corrida no fluxo normal da aplicacao; a constraint continua
sendo a garantia final de integridade.

## Demonstracao

`backend/tests/concurrency_demo.py` usa duas threads e duas instancias
independentes de `Session`. A primeira transacao segura o lock por 1,2 segundo,
permitindo observar a espera da segunda.

```powershell
$env:PYTHONPATH = "backend"
.\backend\.venv\Scripts\python.exe backend\tests\concurrency_demo.py
```

O script:

- recusa executar se a data de teste ja estiver ocupada;
- exige um `COMMIT` e um conflito;
- confirma que existe exatamente uma escala;
- remove somente a escala criada pela demonstracao.

## Resultado observado

Na execucao registrada:

- TX-A adquiriu o lock em 0,063 segundo;
- TX-B aguardou 1,218 segundo;
- TX-A confirmou a escala;
- TX-B encontrou o conflito depois do lock e executou rollback;
- o banco terminou com uma unica escala;
- a escala de teste foi removida.

O log completo esta em
`reports/phase-02/concurrency-demo.log`.
