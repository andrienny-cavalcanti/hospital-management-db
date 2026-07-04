# Modelo Relacional - Etapa 1

## Tabelas

### PESSOA
**PESSOA**(`id_pessoa` PK, nome, cpf UNIQUE, data_nascimento, is_flamengo, telefone)

### PACIENTE
**PACIENTE**(`id_pessoa` PK/FK -> PESSOA.id_pessoa, num_convenio UNIQUE, alergias, grupo_sanguineo, endereco)

### PROFISSIONAL
**PROFISSIONAL**(`id_pessoa` PK/FK -> PESSOA.id_pessoa, crm UNIQUE, data_admissao, especialidade)

### RESIDENTE
**RESIDENTE**(`id_profissional` PK/FK -> PROFISSIONAL.id_pessoa, ano_residencia)

### PRECEPTOR
**PRECEPTOR**(`id_profissional` PK/FK -> PROFISSIONAL.id_pessoa, titulacao)

### UNIDADE
**UNIDADE**(`id_unidade` PK, nome UNIQUE, tipo, capacidade_leitos)

### ATENDIMENTO
**ATENDIMENTO**(`id_atendimento` PK, data_hora, duracao_minutos, id_paciente FK -> PACIENTE, id_residente FK -> RESIDENTE, id_preceptor FK -> PRECEPTOR)

### PROCEDIMENTO
**PROCEDIMENTO**(`id_procedimento` PK, codigo UNIQUE, nome, tempo_medio_minutos, nivel_risco)

### PROCEDIMENTO_REALIZADO
**PROCEDIMENTO_REALIZADO**(`id_atendimento` PK/FK -> ATENDIMENTO, `id_procedimento` PK/FK -> PROCEDIMENTO, quantidade, tempo_real_minutos, observacao, faturado)

### ESCALA
**ESCALA**(`id_escala` PK, id_unidade FK -> UNIDADE, data_plantao, dia_semana, turno, id_residente FK -> RESIDENTE, id_preceptor FK -> PRECEPTOR, UNIQUE(id_unidade, dia_semana, turno, id_residente), UNIQUE(id_unidade, data_plantao, turno, id_residente))

## Cardinalidades principais

- Uma pessoa pode ser paciente e/ou profissional, conforme o enunciado.
- Um paciente pode ter zero ou muitos atendimentos; cada atendimento possui exatamente um paciente.
- Um residente pode realizar zero ou muitos atendimentos; cada atendimento possui exatamente um residente.
- Um preceptor pode supervisionar zero ou muitos atendimentos; cada atendimento possui exatamente um preceptor.
- Um atendimento possui um ou mais procedimentos realizados.
- Um procedimento pode aparecer em muitos atendimentos.
- Uma unidade pode possuir muitas escalas de plantao.
- Cada escala relaciona uma unidade, um residente, um preceptor, um dia e um turno.
