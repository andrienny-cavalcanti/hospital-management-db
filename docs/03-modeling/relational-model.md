# Modelo Relacional - Etapa 1

Documento complementar: [DER - Justificativas de Cardinalidades e Especializacoes](er-justification.md).

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
**ESCALA**(`id_escala` PK, id_unidade FK -> UNIDADE, data_plantao, dia_semana, turno, id_residente FK -> RESIDENTE, id_preceptor FK -> PRECEPTOR)

Restricoes de unicidade:

- `uq_escala_regra_enunciado`: `UNIQUE(id_unidade, dia_semana, turno, id_residente)`.
- `uq_escala_data_plantao`: `UNIQUE(id_unidade, data_plantao, turno, id_residente)`.

Observacao: a primeira restricao reproduz a regra solicitada no enunciado da Etapa 1. A segunda usa `data_plantao`, atributo complementar, para permitir consultas mensais sem perder controle sobre repeticoes na mesma unidade, data, turno e residente.

## Atributos complementares da Etapa 1

Alguns atributos foram mantidos no modelo fisico porque sao necessarios para executar requisitos especificos de CRUD e consultas da Etapa 1:

- `PACIENTE.endereco`: atende ao requisito de atualizar dados de paciente, permitindo alterar endereco ou convenio.
- `PROCEDIMENTO.nivel_risco`: atende a consulta analitica que lista pacientes que nunca realizaram procedimento de risco `ALTO`.
- `PROCEDIMENTO_REALIZADO.faturado`: atende a regra de remover procedimento realizado apenas quando ainda nao houver faturamento associado.
- `ESCALA.data_plantao`: atende a consulta de quantidade de plantoes por residente no mes corrente.

Esses campos complementam o enunciado sem alterar as entidades principais nem as cardinalidades do modelo.

## Cardinalidades principais

- Uma pessoa pode ser paciente e/ou profissional, conforme o enunciado.
- Um paciente pode ter zero ou muitos atendimentos; cada atendimento possui exatamente um paciente.
- Um residente pode realizar zero ou muitos atendimentos; cada atendimento possui exatamente um residente.
- Um preceptor pode supervisionar zero ou muitos atendimentos; cada atendimento possui exatamente um preceptor.
- Um atendimento possui um ou mais procedimentos realizados.
- Um procedimento pode aparecer em muitos atendimentos.
- Uma unidade pode possuir muitas escalas de plantao.
- Cada escala relaciona uma unidade, um residente, um preceptor, um dia e um turno.
- O atributo `data_plantao` foi mantido como extensao pratica ao modelo do enunciado para viabilizar a consulta de plantoes no mes corrente.
