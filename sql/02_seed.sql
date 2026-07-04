-- =============================================================
-- Dados de teste - Etapa 1
-- Execute apos 01_schema.sql
-- =============================================================

-- Pacientes
INSERT INTO pessoa (id_pessoa, nome, cpf, data_nascimento, is_flamengo, telefone) VALUES
(1, 'Ana Beatriz Lima', '11111111111', '1990-02-10', TRUE,  '83990000001'),
(2, 'Carlos Eduardo Silva', '22222222222', '1985-07-22', FALSE, '83990000002'),
(3, 'Marina Costa', '33333333333', '2001-11-04', TRUE,  '83990000003'),
(4, 'Joao Pedro Almeida', '44444444444', '1978-03-18', FALSE, '83990000004'),
(5, 'Luciana Rocha', '55555555555', '1995-09-30', FALSE, '83990000005');

INSERT INTO paciente (id_pessoa, num_convenio, alergias, grupo_sanguineo, endereco) VALUES
(1, 'CONV-1001', 'Dipirona', 'O+', 'Rua A, 100'),
(2, 'CONV-1002', 'Nenhuma', 'A+', 'Rua B, 200'),
(3, 'CONV-1003', 'Penicilina', 'B-', 'Rua C, 300'),
(4, 'CONV-1004', 'Lactose', 'AB+', 'Rua D, 400'),
(5, 'CONV-1005', 'Nenhuma', 'O-', 'Rua E, 500');

-- Residentes
INSERT INTO pessoa (id_pessoa, nome, cpf, data_nascimento, is_flamengo, telefone) VALUES
(6, 'Rafael Menezes', '66666666666', '1996-01-15', TRUE,  '83990000006'),
(7, 'Bianca Torres', '77777777777', '1997-05-12', FALSE, '83990000007'),
(8, 'Felipe Nogueira', '88888888888', '1995-12-01', TRUE,  '83990000008'),
(9, 'Camila Farias', '99999999999', '1998-06-19', FALSE, '83990000009'),
(10,'Thiago Barros', '10101010101', '1994-04-08', FALSE, '83990000010');

INSERT INTO profissional (id_pessoa, crm, data_admissao, especialidade) VALUES
(6, 'CRM-R001', '2025-03-01', 'Clinica Medica'),
(7, 'CRM-R002', '2025-03-01', 'Pediatria'),
(8, 'CRM-R003', '2024-03-01', 'Cirurgia Geral'),
(9, 'CRM-R004', '2026-03-01', 'Cardiologia'),
(10,'CRM-R005', '2024-03-01', 'Ortopedia');

INSERT INTO residente (id_profissional, ano_residencia) VALUES
(6, 'R2'), (7, 'R2'), (8, 'R3'), (9, 'R1'), (10, 'R3');

-- Preceptores
INSERT INTO pessoa (id_pessoa, nome, cpf, data_nascimento, is_flamengo, telefone) VALUES
(11, 'Dra. Helena Duarte', '12121212121', '1975-08-21', FALSE, '83990000011'),
(12, 'Dr. Marcos Vinicius', '13131313131', '1970-10-11', TRUE,  '83990000012'),
(13, 'Dra. Patricia Gomes', '14141414141', '1980-02-26', FALSE, '83990000013'),
(14, 'Dr. Sergio Matos', '15151515151', '1968-12-03', FALSE, '83990000014'),
(15, 'Dra. Natalia Freire', '16161616161', '1982-07-14', TRUE,  '83990000015');

INSERT INTO profissional (id_pessoa, crm, data_admissao, especialidade) VALUES
(11, 'CRM-P001', '2010-01-10', 'Clinica Medica'),
(12, 'CRM-P002', '2008-04-20', 'Pediatria'),
(13, 'CRM-P003', '2012-09-15', 'Cirurgia Geral'),
(14, 'CRM-P004', '2005-05-30', 'Cardiologia'),
(15, 'CRM-P005', '2015-11-12', 'Ortopedia');

INSERT INTO preceptor (id_profissional, titulacao) VALUES
(11, 'Doutora'), (12, 'Mestre'), (13, 'Doutora'), (14, 'Especialista'), (15, 'Doutora');

-- Unidades
INSERT INTO unidade (id_unidade, nome, tipo, capacidade_leitos) VALUES
(1, 'Enfermaria Central', 'Enfermaria', 40),
(2, 'UTI Adulto', 'UTI', 12),
(3, 'Pronto-Socorro Geral', 'Pronto-Socorro', 20);

-- Procedimentos
INSERT INTO procedimento (id_procedimento, codigo, nome, tempo_medio_minutos, nivel_risco) VALUES
(1, 'PROC-001', 'Sutura simples', 30, 'MEDIO'),
(2, 'PROC-002', 'Coleta de sangue', 10, 'BAIXO'),
(3, 'PROC-003', 'Aplicacao de medicacao', 15, 'BAIXO'),
(4, 'PROC-004', 'Intubacao orotraqueal', 45, 'ALTO'),
(5, 'PROC-005', 'Curativo complexo', 25, 'MEDIO'),
(6, 'PROC-006', 'Eletrocardiograma', 20, 'BAIXO');

-- Atendimentos
INSERT INTO atendimento (id_atendimento, data_hora, duracao_minutos, id_paciente, id_residente, id_preceptor) VALUES
(1, '2026-07-01 08:30', 50, 1, 6, 11),
(2, '2026-07-01 09:40', 35, 2, 7, 12),
(3, '2026-07-02 10:10', 60, 3, 8, 13),
(4, '2026-07-02 14:00', 45, 4, 9, 14),
(5, '2026-07-03 15:20', 30, 5, 10, 15),
(6, '2026-07-04 08:00', 70, 1, 6, 11),
(7, '2026-07-04 11:00', 40, 2, 6, 11),
(8, '2026-07-05 13:30', 55, 3, 7, 12),
(9, '2026-07-06 16:10', 25, 4, 8, 13),
(10,'2026-07-07 19:00', 80, 5, 9, 14);

-- Procedimentos realizados
INSERT INTO procedimento_realizado (id_atendimento, id_procedimento, quantidade, tempo_real_minutos, observacao, faturado) VALUES
(1, 2, 1, 12, 'Coleta sem intercorrencias', FALSE),
(1, 3, 1, 14, 'Medicacao administrada', TRUE),
(2, 2, 1, 10, 'Paciente cooperativo', FALSE),
(3, 1, 1, 35, 'Sutura com anestesia local', TRUE),
(4, 4, 1, 50, 'Procedimento de alto risco', TRUE),
(5, 6, 1, 18, 'ECG normal', FALSE),
(6, 5, 2, 40, 'Curativo em lesao extensa', FALSE),
(7, 3, 1, 15, 'Sem intercorrencias', FALSE),
(8, 4, 1, 48, 'Intercorrencia controlada', TRUE),
(9, 2, 1, 9, 'Coleta rapida', FALSE),
(10,5, 1, 27, 'Curativo trocado', FALSE);

-- Escalas de plantao
INSERT INTO escala (id_unidade, data_plantao, dia_semana, turno, id_residente, id_preceptor) VALUES
(1, '2026-07-06', 'segunda', 'manha', 6, 11),
(1, '2026-07-06', 'segunda', 'tarde', 7, 12),
(2, '2026-07-07', 'terca', 'noite', 8, 13),
(3, '2026-07-08', 'quarta', 'manha', 9, 14),
(1, '2026-07-09', 'quinta', 'tarde', 10, 15),
(2, '2026-07-10', 'sexta', 'manha', 6, 11),
(3, '2026-07-11', 'sabado', 'noite', 7, 12),
(1, '2026-07-12', 'domingo', 'manha', 8, 13),
(2, '2026-07-13', 'segunda', 'tarde', 9, 14),
(3, '2026-07-14', 'terca', 'noite', 10, 15);

SELECT setval('pessoa_id_pessoa_seq', 15, true);
SELECT setval('unidade_id_unidade_seq', 3, true);
SELECT setval('procedimento_id_procedimento_seq', 6, true);
SELECT setval('atendimento_id_atendimento_seq', 10, true);
