# Evidencia de validacao final da Etapa 2

## Execucao

- Data: 16 de julho de 2026.
- PostgreSQL: 18.4.
- Ambiente: schema isolado criado exclusivamente para o teste.
- Comando: `.\scripts\run-phase-02.ps1 all`.
- Resultado geral: **OK**.

## Resultados

### Dados minimos

- 5 pacientes: OK.
- 5 residentes: OK.
- 5 preceptores: OK.
- 3 unidades: OK.
- 10 atendimentos: OK.
- 11 procedimentos realizados: OK.

### SQL avancado

- 3 triggers criados e testados.
- Auditoria de INSERT, UPDATE e DELETE confirmada.
- Media de procedimento recalculada para 24,00 no teste.
- 3 stored procedures criadas e testadas.
- Rollback de atendimento completo confirmado.
- 3 views criadas e testadas.
- Totais mensais preservaram os 10 atendimentos.
- 9 verificacoes estruturais consolidadas com status OK.

### ORM

- 12 mappers configurados.
- CRUD e cadastros compostos executados.
- Consultas basicas e analiticas executadas.
- 3 consultas ORM avancadas validadas.
- Lazy loading e eager loading validados.
- Resultado: `ORM smoke test: OK`.

### Concorrencia

- TX-A adquiriu o lock em 0,047 segundo.
- TX-B aguardou 1,219 segundo.
- TX-A realizou COMMIT.
- TX-B realizou ROLLBACK por conflito.
- Exatamente uma escala existiu depois das transacoes.
- A escala de demonstracao foi removida.
- Resultado: `Concurrency demo: OK`.

## Isolamento

O schema de validacao foi removido com todos os seus objetos. Nenhuma tabela,
funcao, view, procedure ou dado de teste permaneceu no banco principal.
