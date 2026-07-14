# DER - Justificativas de Cardinalidades e Especializacoes

Este documento complementa o Diagrama Entidade-Relacionamento da Etapa 1 e explicita as decisoes de modelagem conceitual usadas no projeto.

## Escopo da Etapa 1

O modelo cobre o nucleo solicitado para a primeira entrega:

- cadastro de pessoas, pacientes e profissionais;
- classificacao de profissionais como residentes ou preceptores;
- registro de atendimentos com paciente, residente e preceptor;
- registro dos procedimentos executados em cada atendimento;
- cadastro de unidades hospitalares;
- organizacao das escalas de plantao por unidade, dia, turno, residente e preceptor.

## Especializacoes

### PESSOA -> PACIENTE

Uma pessoa pode ser cadastrada como paciente quando possui dados assistenciais especificos, como numero de convenio, alergias e grupo sanguineo.

Cardinalidade adotada:

- Uma `PESSOA` pode estar associada a zero ou um registro em `PACIENTE`.
- Cada `PACIENTE` deve corresponder obrigatoriamente a uma unica `PESSOA`.

Justificativa:

Os atributos comuns ficam em `PESSOA`, evitando repeticao de nome, CPF, data de nascimento, indicador `is_flamengo` e telefone. Os atributos que so fazem sentido para pacientes ficam separados em `PACIENTE`.

### PESSOA -> PROFISSIONAL

Uma pessoa pode ser cadastrada como profissional quando possui informacoes ligadas ao exercicio medico, como CRM, data de admissao e especialidade.

Cardinalidade adotada:

- Uma `PESSOA` pode estar associada a zero ou um registro em `PROFISSIONAL`.
- Cada `PROFISSIONAL` deve corresponder obrigatoriamente a uma unica `PESSOA`.

Justificativa:

O enunciado permite que uma pessoa seja paciente ou profissional. Separar `PROFISSIONAL` de `PESSOA` preserva os dados comuns em uma unica tabela e isola os atributos profissionais.

### PROFISSIONAL -> RESIDENTE

Um profissional pode atuar como residente quando e um medico em formacao.

Cardinalidade adotada:

- Um `PROFISSIONAL` pode estar associado a zero ou um registro em `RESIDENTE`.
- Cada `RESIDENTE` deve corresponder obrigatoriamente a um unico `PROFISSIONAL`.

Justificativa:

O atributo `ano_residencia` e especifico de residentes e por isso fica na entidade especializada `RESIDENTE`.

### PROFISSIONAL -> PRECEPTOR

Um profissional pode atuar como preceptor quando e responsavel pela supervisao de residentes.

Cardinalidade adotada:

- Um `PROFISSIONAL` pode estar associado a zero ou um registro em `PRECEPTOR`.
- Cada `PRECEPTOR` deve corresponder obrigatoriamente a um unico `PROFISSIONAL`.

Justificativa:

O atributo `titulacao` e especifico de preceptores e por isso fica na entidade especializada `PRECEPTOR`.

## Cardinalidades dos Relacionamentos

### PACIENTE - ATENDIMENTO

Cardinalidade:

- Um `PACIENTE` pode possuir zero ou muitos `ATENDIMENTO`.
- Cada `ATENDIMENTO` possui exatamente um `PACIENTE`.

Justificativa:

Um paciente pode ainda nao ter sido atendido ou pode ter varios atendimentos ao longo do tempo. Por outro lado, cada atendimento precisa identificar o paciente atendido.

### RESIDENTE - ATENDIMENTO

Cardinalidade:

- Um `RESIDENTE` pode realizar zero ou muitos `ATENDIMENTO`.
- Cada `ATENDIMENTO` possui exatamente um `RESIDENTE`.

Justificativa:

O enunciado define que o atendimento e realizado por um residente sob supervisao. Um residente pode nao ter atendimentos registrados ou pode realizar varios.

### PRECEPTOR - ATENDIMENTO

Cardinalidade:

- Um `PRECEPTOR` pode supervisionar zero ou muitos `ATENDIMENTO`.
- Cada `ATENDIMENTO` possui exatamente um `PRECEPTOR`.

Justificativa:

Todo atendimento deve ter um preceptor responsavel pela supervisao. Um mesmo preceptor pode supervisionar varios atendimentos.

### ATENDIMENTO - PROCEDIMENTO_REALIZADO - PROCEDIMENTO

Cardinalidade:

- Um `ATENDIMENTO` possui um ou muitos registros em `PROCEDIMENTO_REALIZADO`.
- Cada `PROCEDIMENTO_REALIZADO` pertence a exatamente um `ATENDIMENTO`.
- Um `PROCEDIMENTO` pode aparecer em zero ou muitos registros de `PROCEDIMENTO_REALIZADO`.
- Cada `PROCEDIMENTO_REALIZADO` referencia exatamente um `PROCEDIMENTO`.

Justificativa:

O enunciado informa que durante um atendimento podem ser realizados um ou mais procedimentos. Como um procedimento tambem pode ocorrer em muitos atendimentos, a entidade associativa `PROCEDIMENTO_REALIZADO` resolve o relacionamento muitos-para-muitos e armazena atributos proprios da execucao, como quantidade, tempo real, observacao e flag de faturamento.

### UNIDADE - ESCALA

Cardinalidade:

- Uma `UNIDADE` pode possuir zero ou muitas `ESCALA`.
- Cada `ESCALA` pertence a exatamente uma `UNIDADE`.

Justificativa:

As escalas sao organizadas por unidade hospitalar. Uma unidade pode ainda nao ter escala cadastrada, mas toda escala precisa indicar onde o plantao ocorre.

### RESIDENTE - ESCALA

Cardinalidade:

- Um `RESIDENTE` pode estar em zero ou muitas `ESCALA`.
- Cada `ESCALA` possui exatamente um `RESIDENTE`.

Justificativa:

Um residente pode aparecer em varios plantoes. Cada registro de escala representa um plantao especifico para um residente.

### PRECEPTOR - ESCALA

Cardinalidade:

- Um `PRECEPTOR` pode supervisionar zero ou muitas `ESCALA`.
- Cada `ESCALA` possui exatamente um `PRECEPTOR`.

Justificativa:

O preceptor e o supervisor associado ao residente naquele plantao. O mesmo preceptor pode supervisionar diferentes escalas, respeitando as regras de unicidade definidas no modelo relacional.

## Regras Relevantes Representadas no Modelo

- `PESSOA.cpf` e unico, evitando duplicidade cadastral.
- `PROFISSIONAL.crm` e unico, garantindo identificacao profissional.
- `PACIENTE.num_convenio` e unico no modelo da Etapa 1.
- `ATENDIMENTO` exige paciente, residente e preceptor obrigatorios.
- `PROCEDIMENTO_REALIZADO` usa chave primaria composta por atendimento e procedimento.
- `ESCALA` usa `uq_escala_regra_enunciado` para impedir repeticao do mesmo residente na mesma unidade, dia da semana e turno, conforme a regra solicitada na Etapa 1.
- `ESCALA` tambem usa `uq_escala_data_plantao` para impedir repeticao do mesmo residente na mesma unidade, data de plantao e turno.

## Atributos Complementares da Etapa 1

Alguns atributos aparecem no modelo fisico porque sao necessarios para os requisitos de CRUD e consultas. Eles foram mantidos, e nao removidos, porque cada um tem uso direto em um item solicitado na Etapa 1:

- `PACIENTE.endereco`: permite executar a atualizacao de dados do paciente solicitada no CRUD. O enunciado cita atualizar endereco ou convenio; como convenio ja existe em `num_convenio`, `endereco` foi incluido para cobrir a outra possibilidade.
- `PROCEDIMENTO.nivel_risco`: permite listar pacientes que nunca realizaram procedimento de risco `ALTO`. Sem esse campo, nao haveria como classificar o risco dos procedimentos na Etapa 1.
- `PROCEDIMENTO_REALIZADO.faturado`: permite remover procedimento realizado apenas quando nao houver faturamento associado. A flag representa a regra pedida sem introduzir uma entidade de faturamento fora do escopo da Etapa 1.
- `ESCALA.data_plantao`: permite calcular plantoes por residente no mes corrente. Esse atributo complementa o modelo do enunciado, que define a escala por dia da semana, e foi mantido para atender a consulta analitica mensal solicitada.

Esses atributos complementam o modelo base do enunciado sem alterar as entidades principais, especializacoes ou cardinalidades da Etapa 1.
