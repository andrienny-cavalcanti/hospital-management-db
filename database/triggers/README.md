# Triggers

Diretorio oficial das funcoes de trigger e triggers da Etapa 2.

## Arquivos

- `01-create-triggers.sql`: cria os tres triggers exigidos no enunciado.

## Triggers implementados

- `trg_check_sobreposicao_escala`: bloqueia o mesmo residente na mesma data e
  turno em unidades diferentes.
- `trg_audita_atendimento`: registra `INSERT`, `UPDATE` e `DELETE` em
  `auditoria_atendimento`.
- `trg_atualiza_media_procedimentos`: recalcula a media depois de cada
  `INSERT` em `procedimento_realizado`.

O script pode ser reaplicado: as funcoes sao substituidas e os triggers sao
recriados com os mesmos nomes.

## Validacao

Depois de executar `database/migrations/phase-02.sql`:

```bash
psql -U postgres -d hospital_management \
  -f database/queries/06-validation-triggers.sql
```

O arquivo de validacao executa todos os cenarios dentro de uma transacao e
finaliza com `ROLLBACK`.
