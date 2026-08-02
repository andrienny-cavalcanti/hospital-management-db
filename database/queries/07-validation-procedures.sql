-- =============================================================
-- Etapa 2 - Validacao das stored procedures
-- Todas as alteracoes deste arquivo sao revertidas no final.
-- =============================================================

\set ON_ERROR_STOP on

BEGIN;

-- 1) Cadastro completo com dois procedimentos.
DO $validation$
DECLARE
    v_id_atendimento INTEGER;
BEGIN
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
                "tempo_real_minutos": 32,
                "observacao": "Sutura de validacao",
                "faturado": false,
                "data_hora_inicio": "2026-07-20T08:10:00"
            },
            {
                "id_procedimento": 2,
                "quantidade": 1,
                "tempo_real_minutos": 11,
                "observacao": "Coleta de validacao",
                "faturado": false,
                "data_hora_inicio": "2026-07-20T08:45:00"
            }
        ]'::JSONB,
        v_id_atendimento
    );

    IF (
        SELECT COUNT(*)
        FROM procedimento_realizado
        WHERE id_atendimento = v_id_atendimento
    ) <> 2 THEN
        RAISE EXCEPTION
            'FALHA: atendimento completo nao registrou dois procedimentos.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM auditoria_atendimento
        WHERE id_atendimento = v_id_atendimento
          AND operacao = 'INSERT'
    ) THEN
        RAISE EXCEPTION
            'FALHA: atendimento completo nao gerou auditoria.';
    END IF;

    RAISE NOTICE
        'OK: atendimento completo % registrado com dois procedimentos.',
        v_id_atendimento;
END
$validation$;

-- 2) Um procedimento inexistente deve reverter todo o bloco do CALL.
DO $validation$
DECLARE
    v_id_atendimento INTEGER;
BEGIN
    BEGIN
        CALL sp_registrar_atendimento_completo(
            TIMESTAMP '2026-07-21 09:00',
            45,
            2,
            7,
            12,
            1,
            '[
                {
                    "id_procedimento": 2,
                    "quantidade": 1,
                    "tempo_real_minutos": 10,
                    "data_hora_inicio": "2026-07-21T09:05:00"
                },
                {
                    "id_procedimento": 999999,
                    "quantidade": 1,
                    "tempo_real_minutos": 20,
                    "data_hora_inicio": "2026-07-21T09:20:00"
                }
            ]'::JSONB,
            v_id_atendimento
        );

        RAISE EXCEPTION
            'FALHA: procedimento inexistente nao interrompeu o CALL.';
    EXCEPTION
        WHEN foreign_key_violation THEN
            NULL;
    END;

    IF EXISTS (
        SELECT 1
        FROM atendimento
        WHERE data_hora = TIMESTAMP '2026-07-21 09:00'
          AND id_paciente = 2
    ) THEN
        RAISE EXCEPTION
            'FALHA: atendimento permaneceu gravado apos erro no procedimento.';
    END IF;

    RAISE NOTICE
        'OK: falha em procedimento reverteu o atendimento completo.';
END
$validation$;

-- 3) A procedure de espera deve retornar todas as unidades.
DO $validation$
DECLARE
    v_resultado JSONB;
BEGIN
    CALL sp_calcular_tempo_medio_espera(v_resultado);

    IF JSONB_TYPEOF(v_resultado) <> 'array'
       OR JSONB_ARRAY_LENGTH(v_resultado) <> (
           SELECT COUNT(*) FROM unidade
       ) THEN
        RAISE EXCEPTION
            'FALHA: resultado de espera nao contem todas as unidades.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM JSONB_ARRAY_ELEMENTS(v_resultado) item
        WHERE NOT (
            item ? 'id_unidade'
            AND item ? 'unidade'
            AND item ? 'atendimentos_com_procedimento'
            AND item ? 'tempo_medio_espera_minutos'
        )
    ) THEN
        RAISE EXCEPTION
            'FALHA: resultado de espera possui estrutura incompleta.';
    END IF;

    RAISE NOTICE
        'OK: tempo medio de espera calculado para % unidades.',
        JSONB_ARRAY_LENGTH(v_resultado);
END
$validation$;

-- 4) Reajuste valido com atualizacao automatica do dia da semana.
DO $validation$
DECLARE
    v_total INTEGER := 0;
BEGIN
    CALL sp_reajustar_escala(
        10,
        DATE '2026-07-14',
        'noite',
        DATE '2026-07-15',
        'tarde',
        v_total
    );

    IF v_total <> 1 OR NOT EXISTS (
        SELECT 1
        FROM escala
        WHERE id_residente = 10
          AND data_plantao = DATE '2026-07-15'
          AND dia_semana = 'quarta'
          AND turno = 'tarde'
    ) THEN
        RAISE EXCEPTION
            'FALHA: reajuste valido nao atualizou a escala corretamente.';
    END IF;

    RAISE NOTICE 'OK: uma escala foi reajustada com sucesso.';
END
$validation$;

-- 5) Reajuste para uma data/turno ja ocupado deve falhar sem alterar a origem.
DO $validation$
DECLARE
    v_total INTEGER := 0;
BEGIN
    BEGIN
        CALL sp_reajustar_escala(
            6,
            DATE '2026-07-10',
            'manha',
            DATE '2026-07-06',
            'manha',
            v_total
        );

        RAISE EXCEPTION
            'FALHA: reajuste conflitante nao foi bloqueado.';
    EXCEPTION
        WHEN unique_violation THEN
            NULL;
    END;

    IF NOT EXISTS (
        SELECT 1
        FROM escala
        WHERE id_residente = 6
          AND data_plantao = DATE '2026-07-10'
          AND turno = 'manha'
    ) THEN
        RAISE EXCEPTION
            'FALHA: escala de origem foi alterada durante conflito.';
    END IF;

    RAISE NOTICE
        'OK: conflito de reajuste foi bloqueado e a origem preservada.';
END
$validation$;

ROLLBACK;

\echo 'Validacao das stored procedures concluida com sucesso.'
