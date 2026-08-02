# Migracao estrutural da Etapa 2

O arquivo `database/migrations/01-phase-02-structural.sql` evolui a base da
Etapa 1 sem modificar o seu script historico de criacao.

## Alteracoes

### Atendimento

Foi adicionado `id_unidade`, obrigatorio e referenciado por chave estrangeira.
Nos registros existentes, a unidade e obtida da escala com data mais proxima
para o residente do atendimento. Se o residente nao possuir escala, e usada a
primeira unidade cadastrada.

### Procedimento realizado

Foi adicionado `data_hora_inicio`, necessario para calcular o tempo entre a
chegada do paciente e o primeiro procedimento. No backfill, os procedimentos
existentes sao posicionados em intervalos de cinco minutos, preservando uma
ordem deterministica.

### Procedimento

Foi adicionada `media_tempo_procedimento`. O valor inicial e calculado a partir
de todos os procedimentos realizados existentes. Posteriormente, a coluna sera
mantida pelo trigger `trg_atualiza_media_procedimentos`.

### Internacao

A tabela `internacao` registra paciente, unidade, entrada e saida. Uma constraint
parcial permite apenas uma internacao aberta por paciente.

### Auditoria de atendimento

A tabela `auditoria_atendimento` armazena operacao, usuario, data e os estados
antigo e novo em JSONB. `id_atendimento` nao possui chave estrangeira para que o
historico continue existindo depois da exclusao do atendimento.

### Escala

Foi adicionada `supervisao_ativa`. A constraint
`uq_escala_residente_data_turno` impede que o mesmo residente seja escalado na
mesma data e turno, inclusive em unidades diferentes. Essa constraint tambem
funciona como protecao final para o futuro teste de concorrencia.

## Atomicidade e reaplicacao

A migracao e executada dentro de `BEGIN` e `COMMIT`. Qualquer falha reverte
todas as alteracoes. Colunas, tabelas, indices e constraints sao verificados
antes da criacao, permitindo reaplicar o arquivo sobre uma base ja migrada.
