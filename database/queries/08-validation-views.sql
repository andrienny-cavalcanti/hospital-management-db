-- =============================================================
-- Etapa 2 - Validacao das views
-- Os dados auxiliares sao revertidos no final.
-- =============================================================

\set ON_ERROR_STOP on

BEGIN;

-- 1) Paciente 1 possui internacao encerrada e uma mais recente ativa.
-- Paciente 2 possui apenas uma internacao encerrada.
INSERT INTO internacao (
    id_paciente,
    id_unidade,
    data_hora_entrada,
    data_hora_saida
)
VALUES
    (
        1,
        1,
        TIMESTAMP '2026-06-01 08:00',
        TIMESTAMP '2026-06-03 10:00'
    ),
    (
        1,
        2,
        TIMESTAMP '2026-07-18 14:00',
        NULL
    ),
    (
        2,
        1,
        TIMESTAMP '2026-07-10 09:00',
        TIMESTAMP '2026-07-11 12:00'
    );

DO $validation$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM vw_pacientes_internados
        WHERE id_paciente = 1
          AND id_unidade = 2
          AND data_hora_entrada = TIMESTAMP '2026-07-18 14:00'
    ) THEN
        RAISE EXCEPTION
            'FALHA: paciente com internacao ativa nao apareceu na view.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM vw_pacientes_internados
        WHERE id_paciente = 2
    ) THEN
        RAISE EXCEPTION
            'FALHA: paciente com internacao encerrada apareceu na view.';
    END IF;

    RAISE NOTICE
        'OK: vw_pacientes_internados retornou apenas a internacao atual.';
END
$validation$;

-- 2) Os preceptores mestres/especialistas devem aparecer.
-- Uma supervisao inativa deve aparecer mesmo com preceptora doutora.
UPDATE escala
SET supervisao_ativa = FALSE
WHERE id_escala = 1;

DO $validation$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM vw_residentes_sem_supervisor
        WHERE id_escala = 1
          AND motivo = 'SUPERVISAO_INATIVA'
    ) THEN
        RAISE EXCEPTION
            'FALHA: supervisao inativa nao apareceu na view.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM vw_residentes_sem_supervisor
        WHERE id_residente = 7
          AND titulacao = 'Mestre'
          AND motivo = 'PRECEPTOR_SEM_TITULACAO_DOUTOR'
    ) OR NOT EXISTS (
        SELECT 1
        FROM vw_residentes_sem_supervisor
        WHERE id_residente = 9
          AND titulacao = 'Especialista'
          AND motivo = 'PRECEPTOR_SEM_TITULACAO_DOUTOR'
    ) THEN
        RAISE EXCEPTION
            'FALHA: titulacao sem doutorado nao apareceu na view.';
    END IF;

    RAISE NOTICE
        'OK: vw_residentes_sem_supervisor identificou os dois motivos.';
END
$validation$;

-- 3) A soma mensal deve preservar o total de atendimentos.
DO $validation$
DECLARE
    v_total_view BIGINT;
    v_total_tabela BIGINT;
BEGIN
    SELECT SUM(total_atendimentos)
    INTO v_total_view
    FROM vw_estatisticas_atendimentos_mensal;

    SELECT COUNT(*)
    INTO v_total_tabela
    FROM atendimento;

    IF v_total_view IS DISTINCT FROM v_total_tabela THEN
        RAISE EXCEPTION
            'FALHA: total mensal (%) difere da tabela (%).',
            v_total_view,
            v_total_tabela;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM vw_estatisticas_atendimentos_mensal
        WHERE total_atendimentos <= 0
           OR media_duracao_minutos IS NULL
           OR JSONB_TYPEOF(procedimentos_mais_comuns) <> 'array'
           OR JSONB_ARRAY_LENGTH(procedimentos_mais_comuns) = 0
    ) THEN
        RAISE EXCEPTION
            'FALHA: estatistica mensal possui dados incompletos.';
    END IF;

    RAISE NOTICE
        'OK: estatisticas mensais preservaram % atendimentos.',
        v_total_view;
END
$validation$;

ROLLBACK;

\echo 'Validacao das views concluida com sucesso.'
