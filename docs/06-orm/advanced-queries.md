# Consultas avancadas com ORM

As consultas estao implementadas em `backend/app/routes/queries.py` usando
exclusivamente a DSL do SQLAlchemy.

## Preceptores de pacientes flamenguistas

Endpoint:

```text
GET /consultas/avancadas/preceptores-pacientes-flamenguistas
```

A consulta percorre os relacionamentos:

```text
Preceptor -> Atendimento -> Paciente -> Pessoa
```

O filtro usa `Pessoa.is_flamengo IS TRUE` e `DISTINCT` evita repetir um
preceptor que supervisionou mais de um atendimento elegivel.

## Ultimo atendimento de cada paciente

Endpoint:

```text
GET /consultas/avancadas/ultimo-atendimento-pacientes
```

Uma subconsulta usa `row_number()` particionado por paciente e ordenado por
data e identificador decrescentes. A linha de posicao 1 representa o ultimo
atendimento.

A resposta inclui:

- paciente;
- data, duracao e unidade;
- residente;
- preceptor;
- lista ordenada de procedimentos.

Todos os pacientes sao retornados. Quando um paciente ainda nao possui
atendimento, `ultimo_atendimento` e nulo. Os relacionamentos do atendimento
sao carregados com `joinedload()` e `selectinload()`.

## Percentual de alto risco por residente

Endpoint:

```text
GET /consultas/avancadas/percentual-risco-alto-residentes
```

Uma subconsulta agrega, por residente:

- total de procedimentos executados;
- total de procedimentos com `nivel_risco = 'ALTO'`.

Os totais usam `procedimento_realizado.quantidade`, representando o numero de
execucoes e nao somente o numero de linhas. O percentual e:

```text
procedimentos_alto_risco * 100 / total_procedimentos
```

Residentes sem procedimentos tambem aparecem, com totais e percentual iguais
a zero.

## Validacao

O arquivo `backend/tests/orm_smoke.py` verifica os resultados conhecidos dos
seeds:

- preceptores 11, 12 e 13 ligados a pacientes flamenguistas;
- ultimo atendimento correto para cada paciente;
- procedimentos presentes na resposta do ultimo atendimento;
- percentual de 50% para os residentes 7 e 9;
- percentual de 0% para o residente 6.
