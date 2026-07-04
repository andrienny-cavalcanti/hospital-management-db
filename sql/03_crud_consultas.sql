-- =============================================================
-- CRUD e consultas basicas - SQL puro
-- =============================================================

-- 1) Inserir novo atendimento verificando se paciente, residente e preceptor existem.
-- Troque os valores do CTE params quando necessario.
WITH params AS (
    SELECT
        TIMESTAMP '2026-07-15 10:30' AS data_hora,
        45 AS duracao_minutos,
        1 AS id_paciente,
        6 AS id_residente,
        11 AS id_preceptor
)
INSERT INTO atendimento (data_hora, duracao_minutos, id_paciente, id_residente, id_preceptor)
SELECT p.data_hora, p.duracao_minutos, p.id_paciente, p.id_residente, p.id_preceptor
FROM params p
WHERE EXISTS (SELECT 1 FROM paciente WHERE id_pessoa = p.id_paciente)
  AND EXISTS (SELECT 1 FROM residente WHERE id_profissional = p.id_residente)
  AND EXISTS (SELECT 1 FROM preceptor WHERE id_profissional = p.id_preceptor)
RETURNING *;

-- 2) Listar todos os atendimentos de um paciente especifico ordenados por data.
SELECT
    a.id_atendimento,
    a.data_hora,
    a.duracao_minutos,
    p.nome AS paciente,
    r.nome AS residente,
    pr.nome AS preceptor
FROM atendimento a
JOIN pessoa p ON p.id_pessoa = a.id_paciente
JOIN pessoa r ON r.id_pessoa = a.id_residente
JOIN pessoa pr ON pr.id_pessoa = a.id_preceptor
WHERE a.id_paciente = 1
ORDER BY a.data_hora;

-- 3) Listar procedimentos realizados em um atendimento.
SELECT
    a.id_atendimento,
    proc.nome AS procedimento,
    pr.quantidade,
    pr.tempo_real_minutos,
    pr.observacao
FROM procedimento_realizado pr
JOIN procedimento proc ON proc.id_procedimento = pr.id_procedimento
JOIN atendimento a ON a.id_atendimento = pr.id_atendimento
WHERE a.id_atendimento = 1
ORDER BY proc.nome;

-- 4) Atualizar dados de um paciente: endereco e convenio.
UPDATE paciente
SET endereco = 'Av. Hospitalar, 777',
    num_convenio = 'CONV-1001-ATUALIZADO'
WHERE id_pessoa = 1
RETURNING *;

-- 5) Remover procedimento realizado somente se nao houver faturamento associado.
DELETE FROM procedimento_realizado
WHERE id_atendimento = 2
  AND id_procedimento = 2
  AND faturado = FALSE
RETURNING *;

-- 6) Calcular tempo medio de duracao dos atendimentos por residente.
SELECT
    r.id_pessoa AS id_residente,
    r.nome AS residente,
    ROUND(AVG(a.duracao_minutos)::numeric, 2) AS tempo_medio_duracao
FROM atendimento a
JOIN pessoa r ON r.id_pessoa = a.id_residente
GROUP BY r.id_pessoa, r.nome
ORDER BY tempo_medio_duracao DESC;
