-- =============================================================
-- Projeto de Banco de Dados - Etapa 1
-- Sistema de Gestao Hospitalar Dra. Yuska Maritan Brito
-- Banco sugerido: PostgreSQL
-- Arquivo oficial: database/schema/01-create-tables.sql
-- =============================================================

DROP TABLE IF EXISTS procedimento_realizado CASCADE;
DROP TABLE IF EXISTS escala CASCADE;
DROP TABLE IF EXISTS atendimento CASCADE;
DROP TABLE IF EXISTS procedimento CASCADE;
DROP TABLE IF EXISTS unidade CASCADE;
DROP TABLE IF EXISTS residente CASCADE;
DROP TABLE IF EXISTS preceptor CASCADE;
DROP TABLE IF EXISTS profissional CASCADE;
DROP TABLE IF EXISTS paciente CASCADE;
DROP TABLE IF EXISTS pessoa CASCADE;

CREATE TABLE pessoa (
    id_pessoa SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    cpf CHAR(11) NOT NULL UNIQUE,
    data_nascimento DATE NOT NULL,
    is_flamengo BOOLEAN NOT NULL DEFAULT FALSE,
    telefone VARCHAR(20) NOT NULL,
    CHECK (cpf ~ '^[0-9]{11}$')
);

CREATE TABLE paciente (
    id_pessoa INTEGER PRIMARY KEY REFERENCES pessoa(id_pessoa) ON DELETE CASCADE,
    num_convenio VARCHAR(40) NOT NULL UNIQUE,
    alergias TEXT,
    grupo_sanguineo VARCHAR(3) NOT NULL,
    -- Campo complementar ao enunciado: usado no CRUD de atualizacao do paciente.
    endereco VARCHAR(160),
    CHECK (grupo_sanguineo IN ('A+','A-','B+','B-','AB+','AB-','O+','O-'))
);

CREATE TABLE profissional (
    id_pessoa INTEGER PRIMARY KEY REFERENCES pessoa(id_pessoa) ON DELETE CASCADE,
    crm VARCHAR(20) NOT NULL UNIQUE,
    data_admissao DATE NOT NULL,
    especialidade VARCHAR(80) NOT NULL
);

CREATE TABLE preceptor (
    id_profissional INTEGER PRIMARY KEY REFERENCES profissional(id_pessoa) ON DELETE CASCADE,
    titulacao VARCHAR(60) NOT NULL
);

CREATE TABLE residente (
    id_profissional INTEGER PRIMARY KEY REFERENCES profissional(id_pessoa) ON DELETE CASCADE,
    ano_residencia VARCHAR(2) NOT NULL,
    CHECK (ano_residencia IN ('R1','R2','R3'))
);

CREATE TABLE unidade (
    id_unidade SERIAL PRIMARY KEY,
    nome VARCHAR(80) NOT NULL UNIQUE,
    tipo VARCHAR(40) NOT NULL,
    capacidade_leitos INTEGER NOT NULL,
    CHECK (capacidade_leitos >= 0),
    CHECK (tipo IN ('Enfermaria','UTI','Pronto-Socorro','Ambulatorio'))
);

CREATE TABLE procedimento (
    id_procedimento SERIAL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    tempo_medio_minutos INTEGER NOT NULL,
    -- Campo complementar ao enunciado: usado na consulta analitica de risco ALTO.
    nivel_risco VARCHAR(10) NOT NULL DEFAULT 'BAIXO',
    CHECK (tempo_medio_minutos > 0),
    CHECK (nivel_risco IN ('BAIXO','MEDIO','ALTO'))
);

CREATE TABLE atendimento (
    id_atendimento SERIAL PRIMARY KEY,
    data_hora TIMESTAMP NOT NULL,
    duracao_minutos INTEGER NOT NULL,
    id_paciente INTEGER NOT NULL REFERENCES paciente(id_pessoa),
    id_residente INTEGER NOT NULL REFERENCES residente(id_profissional),
    id_preceptor INTEGER NOT NULL REFERENCES preceptor(id_profissional),
    CHECK (duracao_minutos > 0),
    CHECK (id_residente <> id_preceptor)
);

CREATE TABLE procedimento_realizado (
    id_atendimento INTEGER NOT NULL REFERENCES atendimento(id_atendimento) ON DELETE CASCADE,
    id_procedimento INTEGER NOT NULL REFERENCES procedimento(id_procedimento),
    quantidade INTEGER NOT NULL,
    tempo_real_minutos INTEGER NOT NULL,
    observacao TEXT,
    -- Campo complementar ao enunciado: permite remover apenas procedimentos nao faturados.
    faturado BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (id_atendimento, id_procedimento),
    CHECK (quantidade > 0),
    CHECK (tempo_real_minutos > 0)
);

CREATE TABLE escala (
    id_escala SERIAL PRIMARY KEY,
    id_unidade INTEGER NOT NULL REFERENCES unidade(id_unidade),
    -- Campo complementar ao enunciado: permite consultas de escala por mes.
    data_plantao DATE NOT NULL,
    dia_semana VARCHAR(15) NOT NULL,
    turno VARCHAR(10) NOT NULL,
    id_residente INTEGER NOT NULL REFERENCES residente(id_profissional),
    id_preceptor INTEGER NOT NULL REFERENCES preceptor(id_profissional),
    CONSTRAINT uq_escala_regra_enunciado UNIQUE (id_unidade, dia_semana, turno, id_residente),
    CONSTRAINT uq_escala_data_plantao UNIQUE (id_unidade, data_plantao, turno, id_residente),
    CHECK (dia_semana IN ('segunda','terca','quarta','quinta','sexta','sabado','domingo')),
    CHECK (turno IN ('manha','tarde','noite')),
    CHECK (id_residente <> id_preceptor)
);

CREATE INDEX idx_atendimento_paciente_data ON atendimento(id_paciente, data_hora);
CREATE INDEX idx_atendimento_residente ON atendimento(id_residente);
CREATE INDEX idx_atendimento_preceptor_data ON atendimento(id_preceptor, data_hora);
CREATE INDEX idx_escala_mes ON escala(data_plantao, id_unidade, id_residente);
