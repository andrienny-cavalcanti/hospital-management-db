# Triggers da Etapa 2

Os triggers estao implementados em
`database/triggers/01-create-triggers.sql`.

## Sobreposicao de escala

`trg_check_sobreposicao_escala` e executado antes de inserir uma escala ou
alterar unidade, data, turno ou residente. A funcao procura outra escala do
mesmo residente, na mesma data e turno, em unidade diferente.

A constraint `uq_escala_residente_data_turno` continua sendo necessaria. O
trigger fornece uma mensagem ligada a regra de negocio, enquanto a constraint
garante a integridade mesmo quando duas transacoes concorrentes verificam a
regra ao mesmo tempo.

## Auditoria de atendimento

`trg_audita_atendimento` e executado depois de `INSERT`, `UPDATE` e `DELETE`.
Ele registra:

- identificador do atendimento;
- tipo da operacao;
- usuario da sessao;
- data e hora;
- dados antigos em JSONB;
- dados novos em JSONB.

A auditoria nao referencia `atendimento` por chave estrangeira, permitindo que
o evento de exclusao permaneça armazenado.

## Media dos procedimentos

`trg_atualiza_media_procedimentos` e executado depois de um `INSERT` em
`procedimento_realizado`. A media e recalculada usando todos os tempos reais do
procedimento inserido.

O comportamento segue o requisito do enunciado, que solicita o trigger
especificamente depois de insercoes.
