# Implementacao com SQLAlchemy

## Tecnologia

O backend usa SQLAlchemy 2.x de forma sincrona com o driver psycopg 3. A URL
`postgresql://` fornecida pelo ambiente e normalizada para o dialeto
`postgresql+psycopg://`.

## Mapeamento

As 12 classes em `backend/app/models.py` representam:

- Pessoa, Paciente e Profissional;
- Residente e Preceptor;
- Unidade;
- Atendimento;
- Procedimento e ProcedimentoRealizado;
- Escala;
- Internacao;
- AuditoriaAtendimento.

As especializacoes foram mapeadas como relacionamentos um-para-um com chave
primaria compartilhada. Essa abordagem preserva o modelo relacional existente
sem adicionar uma coluna discriminadora.

## Sessoes e transacoes

`backend/app/db.py` cria um `Engine` com verificacao de conexao e uma fabrica
`SessionLocal`. Cada requisicao recebe sua propria `Session`.

Operacoes de escrita:

1. adicionam ou alteram entidades na sessao;
2. executam `commit()` somente depois que toda a operacao termina;
3. executam `rollback()` ao capturar falhas de integridade;
4. deixam o fechamento da sessao para a dependencia FastAPI.

Cadastros compostos, como Pessoa + Profissional + Residente, sao persistidos
em uma unica transacao pelo mecanismo de cascata da ORM.

## Consultas sem SQL textual

As rotas usam:

- `select()` para consultas;
- `join()` e `outerjoin()` para relacionamentos;
- `func.count()` e `func.avg()` para agregacoes;
- `exists()` para subconsultas;
- `group_by()` e `having()` para consultas analiticas;
- `Session.get()` para busca por chave primaria.

Nao ha chamadas `cursor.execute()` nem consultas SQL textuais em
`backend/app/routes/`.

## Lazy loading e eager loading

O endpoint
`/consultas/demonstracao-carregamento/{id_atendimento}` aceita:

- `estrategia=lazy`: os procedimentos sao carregados quando a propriedade do
  relacionamento e acessada;
- `estrategia=eager`: `selectinload()` carrega os procedimentos em lote e
  `joinedload()` carrega o cadastro do procedimento.

As listagens regulares usam eager loading quando os relacionamentos sempre
fazem parte da resposta, evitando o problema de uma consulta adicional para
cada registro.

## Validacao

`backend/tests/orm_smoke.py` executa:

- configuracao dos 12 mappers;
- listagens dos dados iniciais;
- validacao das quantidades minimas;
- criacao e atualizacao de paciente;
- criacao transacional de residente e preceptor;
- criacao de unidade, procedimento e escala;
- criacao de atendimento e procedimento realizado;
- consultas analiticas;
- consultas avancadas exigidas na Etapa 2;
- lazy loading e eager loading;
- exclusao de procedimento nao faturado.

O teste foi executado em um schema PostgreSQL isolado com migrations, triggers,
procedures e views ativos.

O controle de concorrencia da criacao de escalas e descrito separadamente em
`docs/06-orm/concurrency.md`.
