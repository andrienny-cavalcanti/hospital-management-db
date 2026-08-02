-- =============================================================
-- Etapa 2 - Stored procedures
-- Pre-requisitos: migracao estrutural e triggers da Etapa 2
-- =============================================================

BEGIN;

-- -------------------------------------------------------------
-- Registra um atendimento e todos os procedimentos de uma vez.
--
-- Formato de p_procedimentos:
-- [
--   {
--     "id_procedimento": 1,
--     "quantidade": 1,
--     "tempo_real_minutos": 30,
--     "observacao": "Opcional",
--     "faturado": false,
--     "data_hora_inicio": "2026-07-20T08:10:00"
--   }
-- ]
--
-- A procedure nao confirma a transacao internamente. Se qualquer
-- INSERT falhar, o CALL e revertido pelo PostgreSQL.
-- -------------------------------------------------------------

CREATE OR REPLACE PROCEDURE sp_registrar_atendimento_completo(
    IN p_data_hora TIMESTAMP,
    IN p_duracao_minutos INTEGER,
    IN p_id_paciente INTEGER,
    IN p_id_residente INTEGER,
    IN p_id_preceptor INTEGER,
    IN p_id_unidade INTEGER,
    IN p_procedimentos JSONB,
    INOUT p_id_atendimento INTEGER DEFAULT NULL
)
LANGUAGE plpgsql
AS $procedure$
BEGIN
    IF p_procedimentos IS NULL
       OR JSONB_TYPEOF(p_procedimentos) <> 'array' THEN
        RAISE EXCEPTION
            'Procedimentos devem ser informados em um array JSON.'
            USING ERRCODE = '22023';
    END IF;

    IF JSONB_ARRAY_LENGTH(p_procedimentos) = 0 THEN
        RAISE EXCEPTION
            'Informe ao menos um procedimento em um array JSON.'
            USING ERRCODE = '22023';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM JSONB_TO_RECORDSET(p_procedimentos) AS item (
            id_procedimento INTEGER,
            quantidade INTEGER,
            tempo_real_minutos INTEGER,
            observacao TEXT,
            faturado BOOLEAN,
            data_hora_inicio TIMESTAMP
        )
        WHERE item.id_procedimento IS NULL
           OR item.quantidade IS NULL
           OR item.tempo_real_minutos IS NULL
           OR item.data_hora_inicio IS NULL
    ) THEN
        RAISE EXCEPTION
            'Cada procedimento deve informar id_procedimento, quantidade, tempo_real_minutos e data_hora_inicio.'
            USING ERRCODE = '22023';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM JSONB_TO_RECORDSET(p_procedimentos) AS item (
            id_procedimento INTEGER,
            quantidade INTEGER,
            tempo_real_minutos INTEGER,
            observacao TEXT,
            faturado BOOLEAN,
            data_hora_inicio TIMESTAMP
        )
        WHERE item.data_hora_inicio < p_data_hora
    ) THEN
        RAISE EXCEPTION
            'O inicio de um procedimento nao pode ser anterior ao atendimento.'
            USING ERRCODE = '22023';
    END IF;

    INSERT INTO atendimento (
        data_hora,
        duracao_minutos,
        id_paciente,
        id_residente,
        id_preceptor,
        id_unidade
    )
    VALUES (
        p_data_hora,
        p_duracao_minutos,
        p_id_paciente,
        p_id_residente,
        p_id_preceptor,
        p_id_unidade
    )
    RETURNING id_atendimento
    INTO p_id_atendimento;

    INSERT INTO procedimento_realizado (
        id_atendimento,
        id_procedimento,
        quantidade,
        tempo_real_minutos,
        observacao,
        faturado,
        data_hora_inicio
    )
    SELECT
        p_id_atendimento,
        item.id_procedimento,
        item.quantidade,
        item.tempo_real_minutos,
        item.observacao,
        COALESCE(item.faturado, FALSE),
        item.data_hora_inicio
    FROM JSONB_TO_RECORDSET(p_procedimentos) AS item (
        id_procedimento INTEGER,
        quantidade INTEGER,
        tempo_real_minutos INTEGER,
        observacao TEXT,
        faturado BOOLEAN,
        data_hora_inicio TIMESTAMP
    );
END;
$procedure$;

-- -------------------------------------------------------------
-- Retorna um array JSON com o tempo medio de espera por unidade.
-- Unidades sem atendimento/procedimento aparecem com media NULL.
-- -------------------------------------------------------------

CREATE OR REPLACE PROCEDURE sp_calcular_tempo_medio_espera(
    INOUT p_resultado JSONB DEFAULT NULL
)
LANGUAGE plpgsql
AS $procedure$
BEGIN
    SELECT COALESCE(
        JSONB_AGG(TO_JSONB(estatistica) ORDER BY estatistica.id_unidade),
        '[]'::JSONB
    )
    INTO p_resultado
    FROM (
        SELECT
            u.id_unidade,
            u.nome AS unidade,
            COUNT(primeiro.data_hora_inicio) AS atendimentos_com_procedimento,
            ROUND(
                AVG(
                    EXTRACT(
                        EPOCH FROM (
                            primeiro.data_hora_inicio - a.data_hora
                        )
                    ) / 60
                )::NUMERIC,
                2
            ) AS tempo_medio_espera_minutos
        FROM unidade u
        LEFT JOIN atendimento a
            ON a.id_unidade = u.id_unidade
        LEFT JOIN LATERAL (
            SELECT MIN(pr.data_hora_inicio) AS data_hora_inicio
            FROM procedimento_realizado pr
            WHERE pr.id_atendimento = a.id_atendimento
        ) primeiro ON TRUE
        GROUP BY u.id_unidade, u.nome
    ) estatistica;
END;
$procedure$;

-- -------------------------------------------------------------
-- Move as escalas de um residente entre datas e turnos.
-- As linhas de origem sao bloqueadas ate o fim da transacao.
-- -------------------------------------------------------------

CREATE OR REPLACE PROCEDURE sp_reajustar_escala(
    IN p_id_residente INTEGER,
    IN p_data_origem DATE,
    IN p_turno_origem VARCHAR,
    IN p_data_destino DATE,
    IN p_turno_destino VARCHAR,
    INOUT p_total_ajustado INTEGER DEFAULT 0
)
LANGUAGE plpgsql
AS $procedure$
DECLARE
    v_dia_semana_destino VARCHAR(15);
BEGIN
    IF p_turno_origem NOT IN ('manha', 'tarde', 'noite')
       OR p_turno_destino NOT IN ('manha', 'tarde', 'noite') THEN
        RAISE EXCEPTION
            'Turno invalido. Use manha, tarde ou noite.'
            USING ERRCODE = '22023';
    END IF;

    PERFORM 1
    FROM escala e
    WHERE e.id_residente = p_id_residente
      AND e.data_plantao = p_data_origem
      AND e.turno = p_turno_origem
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Nenhuma escala de origem encontrada para o residente %.',
            p_id_residente
            USING ERRCODE = 'P0002';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM escala e
        WHERE e.id_residente = p_id_residente
          AND e.data_plantao = p_data_destino
          AND e.turno = p_turno_destino
          AND NOT (
              e.data_plantao = p_data_origem
              AND e.turno = p_turno_origem
          )
    ) THEN
        RAISE EXCEPTION
            'O residente % ja possui escala em % no turno %.',
            p_id_residente,
            p_data_destino,
            p_turno_destino
            USING
                ERRCODE = '23505',
                CONSTRAINT = 'uq_escala_residente_data_turno';
    END IF;

    v_dia_semana_destino := CASE EXTRACT(ISODOW FROM p_data_destino)
        WHEN 1 THEN 'segunda'
        WHEN 2 THEN 'terca'
        WHEN 3 THEN 'quarta'
        WHEN 4 THEN 'quinta'
        WHEN 5 THEN 'sexta'
        WHEN 6 THEN 'sabado'
        WHEN 7 THEN 'domingo'
    END;

    UPDATE escala
    SET data_plantao = p_data_destino,
        dia_semana = v_dia_semana_destino,
        turno = p_turno_destino
    WHERE id_residente = p_id_residente
      AND data_plantao = p_data_origem
      AND turno = p_turno_origem;

    GET DIAGNOSTICS p_total_ajustado = ROW_COUNT;
END;
$procedure$;

COMMIT;
