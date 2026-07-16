-- =============================================================
-- Etapa 2 - Views
-- Pre-requisitos: migracao estrutural da Etapa 2
-- =============================================================

BEGIN;

-- -------------------------------------------------------------
-- Pacientes cuja internacao mais recente continua sem saida.
-- -------------------------------------------------------------

CREATE OR REPLACE VIEW vw_pacientes_internados AS
WITH ultima_internacao AS (
    SELECT DISTINCT ON (i.id_paciente)
        i.id_internacao,
        i.id_paciente,
        i.id_unidade,
        i.data_hora_entrada,
        i.data_hora_saida
    FROM internacao i
    ORDER BY
        i.id_paciente,
        i.data_hora_entrada DESC,
        i.id_internacao DESC
)
SELECT
    ui.id_internacao,
    p.id_pessoa AS id_paciente,
    p.nome AS paciente,
    pac.num_convenio,
    pac.grupo_sanguineo,
    u.id_unidade,
    u.nome AS unidade,
    ui.data_hora_entrada
FROM ultima_internacao ui
JOIN paciente pac
    ON pac.id_pessoa = ui.id_paciente
JOIN pessoa p
    ON p.id_pessoa = pac.id_pessoa
JOIN unidade u
    ON u.id_unidade = ui.id_unidade
WHERE ui.data_hora_saida IS NULL;

-- -------------------------------------------------------------
-- Escalas com supervisao inativa ou preceptor sem doutorado.
-- Uma linha representa uma escala que exige revisao.
-- -------------------------------------------------------------

CREATE OR REPLACE VIEW vw_residentes_sem_supervisor AS
SELECT
    e.id_escala,
    e.data_plantao,
    e.dia_semana,
    e.turno,
    u.id_unidade,
    u.nome AS unidade,
    r.id_pessoa AS id_residente,
    r.nome AS residente,
    pr.id_pessoa AS id_preceptor,
    pr.nome AS preceptor,
    prep.titulacao,
    e.supervisao_ativa,
    CASE
        WHEN NOT e.supervisao_ativa THEN 'SUPERVISAO_INATIVA'
        ELSE 'PRECEPTOR_SEM_TITULACAO_DOUTOR'
    END AS motivo
FROM escala e
JOIN unidade u
    ON u.id_unidade = e.id_unidade
JOIN pessoa r
    ON r.id_pessoa = e.id_residente
JOIN preceptor prep
    ON prep.id_profissional = e.id_preceptor
JOIN pessoa pr
    ON pr.id_pessoa = prep.id_profissional
WHERE NOT e.supervisao_ativa
   OR LOWER(TRIM(prep.titulacao)) NOT LIKE 'doutor%';

-- -------------------------------------------------------------
-- Estatisticas mensais por unidade.
-- Os procedimentos empatados na maior frequencia sao preservados.
-- -------------------------------------------------------------

CREATE OR REPLACE VIEW vw_estatisticas_atendimentos_mensal AS
WITH estatisticas_atendimento AS (
    SELECT
        DATE_TRUNC('month', a.data_hora)::DATE AS mes,
        a.id_unidade,
        COUNT(*) AS total_atendimentos,
        ROUND(AVG(a.duracao_minutos)::NUMERIC, 2)
            AS media_duracao_minutos
    FROM atendimento a
    GROUP BY
        DATE_TRUNC('month', a.data_hora)::DATE,
        a.id_unidade
),
frequencia_procedimento AS (
    SELECT
        DATE_TRUNC('month', a.data_hora)::DATE AS mes,
        a.id_unidade,
        p.id_procedimento,
        p.codigo,
        p.nome AS procedimento,
        SUM(pr.quantidade) AS total_executado
    FROM atendimento a
    JOIN procedimento_realizado pr
        ON pr.id_atendimento = a.id_atendimento
    JOIN procedimento p
        ON p.id_procedimento = pr.id_procedimento
    GROUP BY
        DATE_TRUNC('month', a.data_hora)::DATE,
        a.id_unidade,
        p.id_procedimento,
        p.codigo,
        p.nome
),
procedimentos_ranqueados AS (
    SELECT
        fp.*,
        DENSE_RANK() OVER (
            PARTITION BY fp.mes, fp.id_unidade
            ORDER BY fp.total_executado DESC
        ) AS posicao
    FROM frequencia_procedimento fp
),
procedimentos_mais_comuns AS (
    SELECT
        pr.mes,
        pr.id_unidade,
        JSONB_AGG(
            JSONB_BUILD_OBJECT(
                'id_procedimento', pr.id_procedimento,
                'codigo', pr.codigo,
                'nome', pr.procedimento,
                'total_executado', pr.total_executado
            )
            ORDER BY pr.procedimento
        ) AS procedimentos
    FROM procedimentos_ranqueados pr
    WHERE pr.posicao = 1
    GROUP BY pr.mes, pr.id_unidade
)
SELECT
    ea.mes,
    u.id_unidade,
    u.nome AS unidade,
    ea.total_atendimentos,
    ea.media_duracao_minutos,
    COALESCE(pmc.procedimentos, '[]'::JSONB)
        AS procedimentos_mais_comuns
FROM estatisticas_atendimento ea
JOIN unidade u
    ON u.id_unidade = ea.id_unidade
LEFT JOIN procedimentos_mais_comuns pmc
    ON pmc.mes = ea.mes
   AND pmc.id_unidade = ea.id_unidade;

COMMENT ON VIEW vw_pacientes_internados IS
    'Pacientes cuja internacao mais recente nao possui data de saida.';
COMMENT ON VIEW vw_residentes_sem_supervisor IS
    'Escalas com supervisao inativa ou preceptor sem titulacao de doutor.';
COMMENT ON VIEW vw_estatisticas_atendimentos_mensal IS
    'Totais, duracao media e procedimentos mais comuns por mes e unidade.';

COMMIT;
