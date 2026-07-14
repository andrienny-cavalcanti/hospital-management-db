-- =============================================================
-- Validacao dos dados minimos - Etapa 1
-- Execute apos database/seeds/02-seed-data.sql
-- =============================================================

WITH validation_rules AS (
    SELECT
        'Pacientes cadastrados' AS requisito,
        5 AS minimo_esperado,
        (SELECT COUNT(*) FROM paciente) AS total_encontrado
    UNION ALL
    SELECT
        'Residentes cadastrados' AS requisito,
        5 AS minimo_esperado,
        (SELECT COUNT(*) FROM residente) AS total_encontrado
    UNION ALL
    SELECT
        'Preceptores cadastrados' AS requisito,
        5 AS minimo_esperado,
        (SELECT COUNT(*) FROM preceptor) AS total_encontrado
    UNION ALL
    SELECT
        'Unidades cadastradas' AS requisito,
        3 AS minimo_esperado,
        (SELECT COUNT(*) FROM unidade) AS total_encontrado
    UNION ALL
    SELECT
        'Atendimentos cadastrados' AS requisito,
        10 AS minimo_esperado,
        (SELECT COUNT(*) FROM atendimento) AS total_encontrado
    UNION ALL
    SELECT
        'Procedimentos realizados cadastrados' AS requisito,
        10 AS minimo_esperado,
        (SELECT COUNT(*) FROM procedimento_realizado) AS total_encontrado
)
SELECT
    requisito,
    minimo_esperado,
    total_encontrado,
    CASE
        WHEN total_encontrado >= minimo_esperado THEN 'OK'
        ELSE 'FALHA'
    END AS status
FROM validation_rules
ORDER BY requisito;

-- Resumo geral: deve retornar OK quando todos os minimos da Etapa 1 forem atendidos.
WITH validation_rules AS (
    SELECT 5 AS minimo_esperado, (SELECT COUNT(*) FROM paciente) AS total_encontrado
    UNION ALL SELECT 5, (SELECT COUNT(*) FROM residente)
    UNION ALL SELECT 5, (SELECT COUNT(*) FROM preceptor)
    UNION ALL SELECT 3, (SELECT COUNT(*) FROM unidade)
    UNION ALL SELECT 10, (SELECT COUNT(*) FROM atendimento)
    UNION ALL SELECT 10, (SELECT COUNT(*) FROM procedimento_realizado)
)
SELECT
    CASE
        WHEN bool_and(total_encontrado >= minimo_esperado) THEN 'OK'
        ELSE 'FALHA'
    END AS status_geral_etapa_1
FROM validation_rules;
