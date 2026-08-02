# Roteiro do video da Etapa 2 - ate 8 minutos

## Preparacao

Antes de gravar:

```powershell
.\scripts\run-phase-02.ps1 all
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --env-file .env
```

Abrir:

```text
http://127.0.0.1:8000/docs
```

## 0:00-0:40 - Contexto

- Apresentar o Sistema de Gestao Hospitalar.
- Explicar que a Etapa 1 forneceu modelo, SQL puro e dados.
- Mostrar rapidamente a estrutura `database/`, `backend/` e `docs/`.

## 0:40-1:25 - Migracao estrutural

- Abrir `database/migrations/phase-02.sql`.
- Mostrar a ordem: estrutura, triggers, procedures e views.
- Citar INTERNACAO, AUDITORIA_ATENDIMENTO, unidade do atendimento e inicio do
  procedimento.

## 1:25-2:20 - Triggers

- Mostrar os tres nomes no arquivo de triggers.
- Executar `06-validation-triggers.sql`.
- Destacar auditoria em JSONB e bloqueio de sobreposicao.

## 2:20-3:25 - Stored procedures

- Mostrar o JSON recebido por `sp_registrar_atendimento_completo`.
- Executar `07-validation-procedures.sql`.
- Explicar o teste em que um procedimento invalido reverte o atendimento.

## 3:25-4:10 - Views

- Consultar as tres views.
- Destacar internacao ativa, motivo da supervisao irregular e estatisticas
  mensais.

## 4:10-5:20 - ORM

- Mostrar `backend/app/models.py` e `backend/app/db.py`.
- No Swagger, listar pacientes e criar/consultar um atendimento.
- Explicar Session, commit, rollback e ausencia de SQL textual nas rotas.
- Mostrar o endpoint lazy/eager.

## 5:20-6:25 - Consultas avancadas

Executar no Swagger:

```text
/consultas/avancadas/preceptores-pacientes-flamenguistas
/consultas/avancadas/ultimo-atendimento-pacientes
/consultas/avancadas/percentual-risco-alto-residentes
```

- Explicar rapidamente cada resultado.
- Destacar que o percentual usa a quantidade executada.

## 6:25-7:25 - Concorrencia

- Executar `backend/tests/concurrency_demo.py`.
- Mostrar TX-B aguardando o lock.
- Explicar as tres camadas: `FOR UPDATE`, trigger e constraint.
- Mostrar que uma transacao confirma e a outra reverte.

## 7:25-8:00 - Encerramento

- Mostrar `phase-02-requirements-matrix.md`.
- Informar que todos os testes passaram.
- Encerrar com o comando reproduzivel:

```powershell
.\scripts\run-phase-02.ps1 all
```
