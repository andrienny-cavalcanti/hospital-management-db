-- =============================================================
-- Etapa 2 - Funcoes e triggers
-- Pre-requisito: database/migrations/01-phase-02-structural.sql
-- =============================================================

BEGIN;

-- -------------------------------------------------------------
-- Impede o mesmo residente na mesma data e turno em outra unidade.
-- A constraint uq_escala_residente_data_turno permanece como
-- protecao contra condicoes de corrida entre transacoes.
-- -------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_check_sobreposicao_escala()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $function$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM escala e
        WHERE e.id_residente = NEW.id_residente
          AND e.data_plantao = NEW.data_plantao
          AND e.turno = NEW.turno
          AND e.id_unidade <> NEW.id_unidade
          AND e.id_escala IS DISTINCT FROM NEW.id_escala
    ) THEN
        RAISE EXCEPTION
            'Residente % ja possui escala em outra unidade em % no turno %.',
            NEW.id_residente,
            NEW.data_plantao,
            NEW.turno
            USING
                ERRCODE = '23505',
                CONSTRAINT = 'trg_check_sobreposicao_escala';
    END IF;

    RETURN NEW;
END;
$function$;

DROP TRIGGER IF EXISTS trg_check_sobreposicao_escala ON escala;

CREATE TRIGGER trg_check_sobreposicao_escala
BEFORE INSERT OR UPDATE OF id_unidade, data_plantao, turno, id_residente
ON escala
FOR EACH ROW
EXECUTE FUNCTION fn_check_sobreposicao_escala();

-- -------------------------------------------------------------
-- Registra o estado anterior e/ou novo de cada atendimento.
-- A tabela de auditoria nao possui FK para preservar DELETEs.
-- -------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_audita_atendimento()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $function$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO auditoria_atendimento (
            id_atendimento,
            operacao,
            usuario,
            dados_antigos,
            dados_novos
        )
        VALUES (
            NEW.id_atendimento,
            TG_OP,
            SESSION_USER,
            NULL,
            TO_JSONB(NEW)
        );

        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO auditoria_atendimento (
            id_atendimento,
            operacao,
            usuario,
            dados_antigos,
            dados_novos
        )
        VALUES (
            NEW.id_atendimento,
            TG_OP,
            SESSION_USER,
            TO_JSONB(OLD),
            TO_JSONB(NEW)
        );

        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO auditoria_atendimento (
            id_atendimento,
            operacao,
            usuario,
            dados_antigos,
            dados_novos
        )
        VALUES (
            OLD.id_atendimento,
            TG_OP,
            SESSION_USER,
            TO_JSONB(OLD),
            NULL
        );

        RETURN OLD;
    END IF;

    RAISE EXCEPTION 'Operacao de auditoria nao suportada: %.', TG_OP;
END;
$function$;

DROP TRIGGER IF EXISTS trg_audita_atendimento ON atendimento;

CREATE TRIGGER trg_audita_atendimento
AFTER INSERT OR UPDATE OR DELETE
ON atendimento
FOR EACH ROW
EXECUTE FUNCTION fn_audita_atendimento();

-- -------------------------------------------------------------
-- Recalcula a media do procedimento depois de uma nova execucao.
-- -------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_atualiza_media_procedimentos()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $function$
BEGIN
    UPDATE procedimento p
    SET media_tempo_procedimento = (
        SELECT COALESCE(
            ROUND(AVG(pr.tempo_real_minutos)::NUMERIC, 2),
            0
        )
        FROM procedimento_realizado pr
        WHERE pr.id_procedimento = NEW.id_procedimento
    )
    WHERE p.id_procedimento = NEW.id_procedimento;

    RETURN NEW;
END;
$function$;

DROP TRIGGER IF EXISTS trg_atualiza_media_procedimentos
    ON procedimento_realizado;

CREATE TRIGGER trg_atualiza_media_procedimentos
AFTER INSERT
ON procedimento_realizado
FOR EACH ROW
EXECUTE FUNCTION fn_atualiza_media_procedimentos();

COMMIT;
