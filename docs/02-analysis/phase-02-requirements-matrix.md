# Matriz de requisitos da Etapa 2

| Requisito | Estado | Evidencia principal |
|---|---|---|
| `sp_registrar_atendimento_completo` com JSON e rollback | Concluido | `database/procedures/01-create-procedures.sql` |
| `sp_calcular_tempo_medio_espera` por unidade | Concluido | `database/procedures/01-create-procedures.sql` |
| `sp_reajustar_escala` com verificacao de conflito | Concluido | `database/procedures/01-create-procedures.sql` |
| Trigger de sobreposicao de escala | Concluido | `database/triggers/01-create-triggers.sql` |
| Auditoria de INSERT, UPDATE e DELETE | Concluido | `database/triggers/01-create-triggers.sql` |
| Atualizacao da media de procedimentos | Concluido | `database/triggers/01-create-triggers.sql` |
| View de pacientes internados | Concluido | `database/views/01-create-views.sql` |
| View de residentes sem supervisor valido | Concluido | `database/views/01-create-views.sql` |
| View de estatisticas mensais | Concluido | `database/views/01-create-views.sql` |
| Mapeamento objeto-relacional | Concluido | `backend/app/models.py` |
| Sessoes e transacoes ORM | Concluido | `backend/app/db.py` e `backend/app/routes/` |
| CRUD da Etapa 1 com ORM | Concluido | `backend/app/routes/` |
| Consultas da Etapa 1 com DSL ORM | Concluido | `backend/app/routes/queries.py` |
| Lazy loading e eager loading | Concluido | endpoint de demonstracao e `docs/06-orm/implementation.md` |
| Preceptores ligados a pacientes flamenguistas | Concluido | endpoint ORM avancado |
| Ultimo atendimento de cada paciente | Concluido | endpoint ORM avancado |
| Percentual de alto risco por residente | Concluido | endpoint ORM avancado |
| Duas transacoes concorrentes | Concluido | `backend/tests/concurrency_demo.py` |
| Lock pessimista pela ORM | Concluido | `backend/app/services/scheduling.py` |
| Codigo e logs de concorrencia | Concluido | `reports/phase-02/concurrency-demo.log` |
| Relatorio breve | Concluido | `reports/phase-02/phase-02-report.pdf` |
| Roteiro para video de ate 8 minutos | Concluido | `presentations/phase-02-video-script.md` |
| Video gravado de ate 8 minutos | Pendente de gravacao | Roteiro concluido |
| Commits e publicacao no GitHub | Pendente de organizacao/publicacao | Alteracoes locais preservadas |

## Validacoes

- `database/queries/06-validation-triggers.sql`
- `database/queries/07-validation-procedures.sql`
- `database/queries/08-validation-views.sql`
- `database/queries/09-validation-phase-02-summary.sql`
- `backend/tests/orm_smoke.py`
- `backend/tests/concurrency_demo.py`

O comando consolidado e:

```powershell
.\scripts\run-phase-02.ps1 all
```
