-- =============================================================
-- Consultas analiticas - SQL puro
-- =============================================================

-- 1) Ranking dos residentes por numero de atendimentos realizados.
SELECT
    r.nome AS residente,
    COUNT(a.id_atendimento) AS total_atendimentos
FROM residente res
JOIN pessoa r ON r.id_pessoa = res.id_profissional
LEFT JOIN atendimento a ON a.id_residente = res.id_profissional
GROUP BY r.nome
ORDER BY total_atendimentos DESC, r.nome;

-- 2) Preceptores que supervisionaram mais de 5 atendimentos em determinado mes.
-- Ajuste a data inicial/final conforme o mes analisado.
SELECT
    p.nome AS preceptor,
    COUNT(a.id_atendimento) AS total_supervisionados
FROM atendimento a
JOIN pessoa p ON p.id_pessoa = a.id_preceptor
WHERE a.data_hora >= DATE '2026-07-01'
  AND a.data_hora <  DATE '2026-08-01'
GROUP BY p.nome
HAVING COUNT(a.id_atendimento) > 5
ORDER BY total_supervisionados DESC;

-- 3) Para cada unidade, quantidade de plantoes escalados por residente no mes corrente.
-- Observacao: foi adicionada data_plantao na tabela ESCALA para permitir consulta mensal.
SELECT
    u.nome AS unidade,
    r.nome AS residente,
    COUNT(e.id_escala) AS total_plantoes_mes_corrente
FROM escala e
JOIN unidade u ON u.id_unidade = e.id_unidade
JOIN pessoa r ON r.id_pessoa = e.id_residente
WHERE e.data_plantao >= date_trunc('month', CURRENT_DATE)
  AND e.data_plantao <  date_trunc('month', CURRENT_DATE) + INTERVAL '1 month'
GROUP BY u.nome, r.nome
ORDER BY u.nome, total_plantoes_mes_corrente DESC, r.nome;

-- 4) Pacientes que nunca realizaram nenhum procedimento de risco ALTO.
SELECT
    p.id_pessoa AS id_paciente,
    p.nome AS paciente
FROM paciente pac
JOIN pessoa p ON p.id_pessoa = pac.id_pessoa
WHERE NOT EXISTS (
    SELECT 1
    FROM atendimento a
    JOIN procedimento_realizado pr ON pr.id_atendimento = a.id_atendimento
    JOIN procedimento proc ON proc.id_procedimento = pr.id_procedimento
    WHERE a.id_paciente = pac.id_pessoa
      AND proc.nivel_risco = 'ALTO'
)
ORDER BY p.nome;
