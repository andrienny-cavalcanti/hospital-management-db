-- =============================================================
-- Etapa 2 - Validacao estrutural consolidada
-- =============================================================

\set ON_ERROR_STOP on

BEGIN;

CREATE TEMP TABLE validation_phase_02 (
    requisito TEXT PRIMARY KEY,
    status BOOLEAN NOT NULL
) ON COMMIT DROP;

INSERT INTO validation_phase_02 (requisito, status) VALUES
(
    'Tabela internacao',
    TO_REGCLASS('internacao') IS NOT NULL
),
(
    'Tabela auditoria_atendimento',
    TO_REGCLASS('auditoria_atendimento') IS NOT NULL
),
(
    'Coluna atendimento.id_unidade',
    EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = CURRENT_SCHEMA()
          AND table_name = 'atendimento'
          AND column_name = 'id_unidade'
          AND is_nullable = 'NO'
    )
),
(
    'Coluna procedimento_realizado.data_hora_inicio',
    EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = CURRENT_SCHEMA()
          AND table_name = 'procedimento_realizado'
          AND column_name = 'data_hora_inicio'
          AND is_nullable = 'NO'
    )
),
(
    'Coluna procedimento.media_tempo_procedimento',
    EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = CURRENT_SCHEMA()
          AND table_name = 'procedimento'
          AND column_name = 'media_tempo_procedimento'
    )
),
(
    'Constraint de concorrencia da escala',
    EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'escala'::REGCLASS
          AND conname = 'uq_escala_residente_data_turno'
    )
),
(
    'Tres triggers da Etapa 2',
    (
        SELECT COUNT(*) = 3
        FROM pg_trigger
        WHERE NOT tgisinternal
          AND tgname IN (
              'trg_check_sobreposicao_escala',
              'trg_audita_atendimento',
              'trg_atualiza_media_procedimentos'
          )
    )
),
(
    'Tres stored procedures da Etapa 2',
    (
        SELECT COUNT(*) = 3
        FROM pg_proc p
        JOIN pg_namespace n
            ON n.oid = p.pronamespace
        WHERE n.nspname = CURRENT_SCHEMA()
          AND p.prokind = 'p'
          AND p.proname IN (
              'sp_registrar_atendimento_completo',
              'sp_calcular_tempo_medio_espera',
              'sp_reajustar_escala'
          )
    )
),
(
    'Tres views da Etapa 2',
    (
        SELECT COUNT(*) = 3
        FROM pg_class c
        JOIN pg_namespace n
            ON n.oid = c.relnamespace
        WHERE n.nspname = CURRENT_SCHEMA()
          AND c.relkind = 'v'
          AND c.relname IN (
              'vw_pacientes_internados',
              'vw_residentes_sem_supervisor',
              'vw_estatisticas_atendimentos_mensal'
          )
    )
);

SELECT
    requisito,
    CASE WHEN status THEN 'OK' ELSE 'FALHA' END AS status
FROM validation_phase_02
ORDER BY requisito;

DO $validation$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM validation_phase_02
        WHERE NOT status
    ) THEN
        RAISE EXCEPTION
            'A validacao estrutural consolidada da Etapa 2 falhou.';
    END IF;
END
$validation$;

ROLLBACK;

\echo 'Validacao estrutural consolidada da Etapa 2: OK'
