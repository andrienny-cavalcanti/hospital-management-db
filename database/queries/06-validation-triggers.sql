-- =============================================================
-- Etapa 2 - Validacao dos triggers
-- Todas as alteracoes deste arquivo sao revertidas no final.
-- =============================================================

\set ON_ERROR_STOP on

BEGIN;

-- 1) A tentativa de escalar o residente 6 em outra unidade,
-- na mesma data e turno, deve produzir unique_violation.
DO $validation$
BEGIN
    BEGIN
        INSERT INTO escala (
            id_unidade,
            data_plantao,
            dia_semana,
            turno,
            id_residente,
            id_preceptor,
            supervisao_ativa
        )
        VALUES (
            2,
            DATE '2026-07-06',
            'segunda',
            'manha',
            6,
            11,
            TRUE
        );

        RAISE EXCEPTION
            'FALHA: trg_check_sobreposicao_escala permitiu a sobreposicao.';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE
                'OK: trg_check_sobreposicao_escala bloqueou a sobreposicao.';
    END;
END
$validation$;

-- 2) INSERT e UPDATE devem produzir dois registros de auditoria.
INSERT INTO atendimento (
    id_atendimento,
    data_hora,
    duracao_minutos,
    id_paciente,
    id_residente,
    id_preceptor,
    id_unidade
)
VALUES (
    2000000000,
    TIMESTAMP '2026-07-20 08:00',
    30,
    1,
    6,
    11,
    1
);

UPDATE atendimento
SET duracao_minutos = 40
WHERE id_atendimento = 2000000000;

DO $validation$
BEGIN
    IF (
        SELECT COUNT(*)
        FROM auditoria_atendimento
        WHERE id_atendimento = 2000000000
          AND operacao IN ('INSERT', 'UPDATE')
    ) <> 2 THEN
        RAISE EXCEPTION
            'FALHA: auditoria de INSERT/UPDATE nao gerou dois registros.';
    END IF;

    RAISE NOTICE 'OK: auditoria de INSERT e UPDATE registrada.';
END
$validation$;

-- 3) A inclusao deve atualizar a media para o valor calculado na origem.
INSERT INTO procedimento_realizado (
    id_atendimento,
    id_procedimento,
    quantidade,
    tempo_real_minutos,
    observacao,
    faturado,
    data_hora_inicio
)
VALUES (
    2000000000,
    6,
    1,
    30,
    'Registro temporario para validar o trigger de media',
    FALSE,
    TIMESTAMP '2026-07-20 08:10'
);

DO $validation$
DECLARE
    media_armazenada NUMERIC(10, 2);
    media_calculada NUMERIC(10, 2);
BEGIN
    SELECT p.media_tempo_procedimento
    INTO media_armazenada
    FROM procedimento p
    WHERE p.id_procedimento = 6;

    SELECT ROUND(AVG(pr.tempo_real_minutos)::NUMERIC, 2)
    INTO media_calculada
    FROM procedimento_realizado pr
    WHERE pr.id_procedimento = 6;

    IF media_armazenada IS DISTINCT FROM media_calculada THEN
        RAISE EXCEPTION
            'FALHA: media armazenada (%) difere da calculada (%).',
            media_armazenada,
            media_calculada;
    END IF;

    RAISE NOTICE
        'OK: media do procedimento atualizada para %.',
        media_armazenada;
END
$validation$;

-- 4) DELETE deve preservar o terceiro evento na tabela de auditoria.
DELETE FROM atendimento
WHERE id_atendimento = 2000000000;

DO $validation$
BEGIN
    IF (
        SELECT COUNT(*)
        FROM auditoria_atendimento
        WHERE id_atendimento = 2000000000
          AND operacao IN ('INSERT', 'UPDATE', 'DELETE')
    ) <> 3 THEN
        RAISE EXCEPTION
            'FALHA: auditoria completa nao gerou tres registros.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM auditoria_atendimento
        WHERE id_atendimento = 2000000000
          AND operacao = 'DELETE'
          AND dados_antigos IS NOT NULL
          AND dados_novos IS NULL
    ) THEN
        RAISE EXCEPTION
            'FALHA: auditoria de DELETE nao preservou os dados antigos.';
    END IF;

    RAISE NOTICE 'OK: auditoria de DELETE registrada com os dados antigos.';
END
$validation$;

ROLLBACK;

\echo 'Validacao dos triggers concluida com sucesso.'
