-- =============================================================
-- Etapa 2 - Migracao estrutural
-- Pre-requisito: schema e seeds da Etapa 1
-- =============================================================

BEGIN;

-- -------------------------------------------------------------
-- ATENDIMENTO passa a identificar a unidade onde ocorreu.
-- O backfill usa a unidade da escala mais proxima do residente.
-- -------------------------------------------------------------

ALTER TABLE atendimento
    ADD COLUMN IF NOT EXISTS id_unidade INTEGER;

UPDATE atendimento a
SET id_unidade = COALESCE(
    (
        SELECT e.id_unidade
        FROM escala e
        WHERE e.id_residente = a.id_residente
        ORDER BY
            ABS(e.data_plantao - a.data_hora::date),
            e.data_plantao,
            e.id_escala
        LIMIT 1
    ),
    (
        SELECT MIN(u.id_unidade)
        FROM unidade u
    )
)
WHERE a.id_unidade IS NULL;

DO $migration$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM atendimento
        WHERE id_unidade IS NULL
    ) THEN
        RAISE EXCEPTION
            'Nao foi possivel preencher atendimento.id_unidade. Cadastre ao menos uma unidade.';
    END IF;
END
$migration$;

ALTER TABLE atendimento
    ALTER COLUMN id_unidade SET NOT NULL;

DO $migration$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'fk_atendimento_unidade'
          AND conrelid = 'atendimento'::regclass
    ) THEN
        ALTER TABLE atendimento
            ADD CONSTRAINT fk_atendimento_unidade
            FOREIGN KEY (id_unidade)
            REFERENCES unidade(id_unidade);
    END IF;
END
$migration$;

CREATE INDEX IF NOT EXISTS idx_atendimento_unidade_data
    ON atendimento(id_unidade, data_hora);

-- -------------------------------------------------------------
-- PROCEDIMENTO_REALIZADO passa a registrar o inicio da execucao.
-- Para o legado, os procedimentos sao espacados em cinco minutos.
-- -------------------------------------------------------------

ALTER TABLE procedimento_realizado
    ADD COLUMN IF NOT EXISTS data_hora_inicio TIMESTAMP;

UPDATE procedimento_realizado pr
SET data_hora_inicio =
    a.data_hora
    + (
        SELECT COUNT(*)
        FROM procedimento_realizado anterior
        WHERE anterior.id_atendimento = pr.id_atendimento
          AND anterior.id_procedimento <= pr.id_procedimento
    ) * INTERVAL '5 minutes'
FROM atendimento a
WHERE a.id_atendimento = pr.id_atendimento
  AND pr.data_hora_inicio IS NULL;

DO $migration$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM procedimento_realizado
        WHERE data_hora_inicio IS NULL
    ) THEN
        RAISE EXCEPTION
            'Nao foi possivel preencher procedimento_realizado.data_hora_inicio.';
    END IF;
END
$migration$;

ALTER TABLE procedimento_realizado
    ALTER COLUMN data_hora_inicio SET NOT NULL;

CREATE INDEX IF NOT EXISTS idx_procedimento_realizado_inicio
    ON procedimento_realizado(id_atendimento, data_hora_inicio);

-- -------------------------------------------------------------
-- PROCEDIMENTO armazena a media atualizada pelo trigger da Etapa 2.
-- -------------------------------------------------------------

ALTER TABLE procedimento
    ADD COLUMN IF NOT EXISTS media_tempo_procedimento NUMERIC(10, 2)
        NOT NULL DEFAULT 0;

UPDATE procedimento p
SET media_tempo_procedimento = COALESCE(
    (
        SELECT ROUND(AVG(pr.tempo_real_minutos)::NUMERIC, 2)
        FROM procedimento_realizado pr
        WHERE pr.id_procedimento = p.id_procedimento
    ),
    0
);

DO $migration$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'chk_procedimento_media_tempo_nao_negativa'
          AND conrelid = 'procedimento'::regclass
    ) THEN
        ALTER TABLE procedimento
            ADD CONSTRAINT chk_procedimento_media_tempo_nao_negativa
            CHECK (media_tempo_procedimento >= 0);
    END IF;
END
$migration$;

-- -------------------------------------------------------------
-- INTERNACAO sustenta a view de pacientes atualmente internados.
-- -------------------------------------------------------------

CREATE TABLE IF NOT EXISTS internacao (
    id_internacao BIGSERIAL PRIMARY KEY,
    id_paciente INTEGER NOT NULL,
    id_unidade INTEGER NOT NULL,
    data_hora_entrada TIMESTAMP NOT NULL,
    data_hora_saida TIMESTAMP,
    CONSTRAINT fk_internacao_paciente
        FOREIGN KEY (id_paciente)
        REFERENCES paciente(id_pessoa),
    CONSTRAINT fk_internacao_unidade
        FOREIGN KEY (id_unidade)
        REFERENCES unidade(id_unidade),
    CONSTRAINT chk_internacao_periodo
        CHECK (
            data_hora_saida IS NULL
            OR data_hora_saida > data_hora_entrada
        )
);

DO $migration$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'fk_internacao_paciente'
          AND conrelid = 'internacao'::regclass
    ) THEN
        ALTER TABLE internacao
            ADD CONSTRAINT fk_internacao_paciente
            FOREIGN KEY (id_paciente)
            REFERENCES paciente(id_pessoa);
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'fk_internacao_unidade'
          AND conrelid = 'internacao'::regclass
    ) THEN
        ALTER TABLE internacao
            ADD CONSTRAINT fk_internacao_unidade
            FOREIGN KEY (id_unidade)
            REFERENCES unidade(id_unidade);
    END IF;
END
$migration$;

CREATE UNIQUE INDEX IF NOT EXISTS uq_internacao_paciente_ativa
    ON internacao(id_paciente)
    WHERE data_hora_saida IS NULL;

CREATE INDEX IF NOT EXISTS idx_internacao_unidade_periodo
    ON internacao(id_unidade, data_hora_entrada, data_hora_saida);

-- -------------------------------------------------------------
-- AUDITORIA_ATENDIMENTO recebera os eventos do trigger de auditoria.
-- id_atendimento nao possui FK para preservar o log apos uma exclusao.
-- -------------------------------------------------------------

CREATE TABLE IF NOT EXISTS auditoria_atendimento (
    id_auditoria BIGSERIAL PRIMARY KEY,
    id_atendimento INTEGER NOT NULL,
    operacao VARCHAR(10) NOT NULL,
    usuario VARCHAR(120) NOT NULL,
    data_hora TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dados_antigos JSONB,
    dados_novos JSONB,
    CONSTRAINT chk_auditoria_atendimento_operacao
        CHECK (operacao IN ('INSERT', 'UPDATE', 'DELETE'))
);

CREATE INDEX IF NOT EXISTS idx_auditoria_atendimento_data
    ON auditoria_atendimento(id_atendimento, data_hora DESC);

-- -------------------------------------------------------------
-- ESCALA ganha estado de supervisao e protecao concorrente.
-- A UNIQUE abaixo tambem impede conflito entre unidades diferentes.
-- -------------------------------------------------------------

ALTER TABLE escala
    ADD COLUMN IF NOT EXISTS supervisao_ativa BOOLEAN NOT NULL DEFAULT TRUE;

DO $migration$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'uq_escala_residente_data_turno'
          AND conrelid = 'escala'::regclass
    ) THEN
        ALTER TABLE escala
            ADD CONSTRAINT uq_escala_residente_data_turno
            UNIQUE (data_plantao, turno, id_residente);
    END IF;
END
$migration$;

COMMENT ON COLUMN atendimento.id_unidade IS
    'Unidade hospitalar onde o atendimento ocorreu.';
COMMENT ON COLUMN procedimento_realizado.data_hora_inicio IS
    'Instante de inicio do procedimento para calculo do tempo de espera.';
COMMENT ON COLUMN procedimento.media_tempo_procedimento IS
    'Media do tempo real, mantida pelo trigger da Etapa 2.';
COMMENT ON COLUMN escala.supervisao_ativa IS
    'Indica se a supervisao do preceptor esta ativa naquele plantao.';
COMMENT ON TABLE internacao IS
    'Historico de internacoes dos pacientes por unidade.';
COMMENT ON TABLE auditoria_atendimento IS
    'Log imutavel das operacoes realizadas em atendimento.';

COMMIT;
