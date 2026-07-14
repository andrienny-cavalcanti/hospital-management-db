# Evidencia de Normalizacao ate 3FN

Este documento registra as dependencias funcionais e a justificativa de normalizacao do modelo relacional da Etapa 1.

## Relacoes analisadas

- `PESSOA(id_pessoa, nome, cpf, data_nascimento, is_flamengo, telefone)`
- `PACIENTE(id_pessoa, num_convenio, alergias, grupo_sanguineo, endereco)`
- `PROFISSIONAL(id_pessoa, crm, data_admissao, especialidade)`
- `RESIDENTE(id_profissional, ano_residencia)`
- `PRECEPTOR(id_profissional, titulacao)`
- `UNIDADE(id_unidade, nome, tipo, capacidade_leitos)`
- `ATENDIMENTO(id_atendimento, data_hora, duracao_minutos, id_paciente, id_residente, id_preceptor)`
- `PROCEDIMENTO(id_procedimento, codigo, nome, tempo_medio_minutos, nivel_risco)`
- `PROCEDIMENTO_REALIZADO(id_atendimento, id_procedimento, quantidade, tempo_real_minutos, observacao, faturado)`
- `ESCALA(id_escala, id_unidade, data_plantao, dia_semana, turno, id_residente, id_preceptor)`

## Dependencias funcionais principais

### PESSOA

- `id_pessoa -> nome, cpf, data_nascimento, is_flamengo, telefone`
- `cpf -> id_pessoa, nome, data_nascimento, is_flamengo, telefone`

Chaves candidatas:

- `id_pessoa`
- `cpf`

### PACIENTE

- `id_pessoa -> num_convenio, alergias, grupo_sanguineo, endereco`
- `num_convenio -> id_pessoa, alergias, grupo_sanguineo, endereco`

Chaves candidatas:

- `id_pessoa`
- `num_convenio`

### PROFISSIONAL

- `id_pessoa -> crm, data_admissao, especialidade`
- `crm -> id_pessoa, data_admissao, especialidade`

Chaves candidatas:

- `id_pessoa`
- `crm`

### RESIDENTE

- `id_profissional -> ano_residencia`

Chave candidata:

- `id_profissional`

### PRECEPTOR

- `id_profissional -> titulacao`

Chave candidata:

- `id_profissional`

### UNIDADE

- `id_unidade -> nome, tipo, capacidade_leitos`
- `nome -> id_unidade, tipo, capacidade_leitos`

Chaves candidatas:

- `id_unidade`
- `nome`

### ATENDIMENTO

- `id_atendimento -> data_hora, duracao_minutos, id_paciente, id_residente, id_preceptor`

Chave candidata:

- `id_atendimento`

### PROCEDIMENTO

- `id_procedimento -> codigo, nome, tempo_medio_minutos, nivel_risco`
- `codigo -> id_procedimento, nome, tempo_medio_minutos, nivel_risco`

Chaves candidatas:

- `id_procedimento`
- `codigo`

### PROCEDIMENTO_REALIZADO

- `(id_atendimento, id_procedimento) -> quantidade, tempo_real_minutos, observacao, faturado`

Chave candidata:

- `(id_atendimento, id_procedimento)`

### ESCALA

- `id_escala -> id_unidade, data_plantao, dia_semana, turno, id_residente, id_preceptor`
- `(id_unidade, dia_semana, turno, id_residente) -> id_escala, data_plantao, id_preceptor`
- `(id_unidade, data_plantao, turno, id_residente) -> id_escala, dia_semana, id_preceptor`

Chaves candidatas:

- `id_escala`
- `(id_unidade, dia_semana, turno, id_residente)`
- `(id_unidade, data_plantao, turno, id_residente)`

Observacao: a segunda chave composta reproduz a regra do enunciado. A terceira chave composta usa `data_plantao`, atributo complementar usado para consultas mensais.

## Justificativa da 1FN

Todas as relacoes possuem atributos atomicos, sem listas ou grupos repetidos.

Exemplos:

- Procedimentos de um atendimento nao ficam armazenados como lista em `ATENDIMENTO`.
- A execucao de procedimentos fica em `PROCEDIMENTO_REALIZADO`, uma relacao propria com quantidade, tempo real, observacao e faturamento.
- Telefones, CPF, CRM, convenio, turno e tipo de unidade sao armazenados em campos simples.

Assim, todos os atributos possuem valores indivisiveis para o modelo adotado.

## Justificativa da 2FN

A 2FN exige que atributos nao-chave dependam da chave primaria completa, especialmente em relacoes com chave composta.

No modelo, quase todas as tabelas possuem chave primaria simples. Nesses casos, nao ha dependencia parcial possivel.

A principal tabela com chave composta e `PROCEDIMENTO_REALIZADO`:

- Chave: `(id_atendimento, id_procedimento)`
- Atributos dependentes: `quantidade`, `tempo_real_minutos`, `observacao`, `faturado`

Esses atributos dependem da combinacao completa entre atendimento e procedimento. Por exemplo, `tempo_real_minutos` nao depende apenas do atendimento, pois um atendimento pode ter varios procedimentos. Tambem nao depende apenas do procedimento, pois o mesmo procedimento pode ter tempos reais diferentes em atendimentos distintos.

Portanto, nao ha dependencia parcial nessa relacao.

## Justificativa da 3FN

A 3FN exige que atributos nao-chave nao dependam de outros atributos nao-chave.

O modelo separa dados por assunto para evitar dependencias transitivas:

- Dados comuns ficam em `PESSOA`.
- Dados assistenciais ficam em `PACIENTE`.
- Dados profissionais ficam em `PROFISSIONAL`.
- Dados especificos de residente ficam em `RESIDENTE`.
- Dados especificos de preceptor ficam em `PRECEPTOR`.
- Dados do procedimento ficam em `PROCEDIMENTO`.
- Dados da execucao do procedimento ficam em `PROCEDIMENTO_REALIZADO`.

Exemplos de dependencias transitivas evitadas:

- `ATENDIMENTO` nao armazena nome do paciente, nome do residente ou nome do preceptor; armazena apenas as FKs.
- `PROCEDIMENTO_REALIZADO` nao armazena nome ou codigo do procedimento; armazena apenas a FK.
- `ESCALA` nao armazena nome da unidade, nome do residente ou nome do preceptor; armazena apenas as FKs.

Com isso, cada atributo nao-chave depende diretamente da chave de sua propria relacao, e nao de outro atributo descritivo.

## Observacao sobre BCNF

As principais dependencias funcionais possuem determinantes que sao chaves candidatas.

Exemplos:

- `cpf` e chave candidata em `PESSOA`.
- `num_convenio` e chave candidata em `PACIENTE`.
- `crm` e chave candidata em `PROFISSIONAL`.
- `codigo` e chave candidata em `PROCEDIMENTO`.
- As combinacoes unicas de `ESCALA` sao tratadas como chaves candidatas documentadas.

Assim, o modelo tambem se aproxima da BCNF nas relacoes principais, pois os determinantes relevantes sao superchaves.

## Conclusao

O modelo atende a 1FN, 2FN e 3FN porque:

- elimina grupos repetidos;
- separa relacionamentos muitos-para-muitos em tabela associativa;
- evita dependencias parciais;
- evita dependencias transitivas;
- usa chaves primarias, estrangeiras e candidatas para preservar integridade e reduzir redundancia.
