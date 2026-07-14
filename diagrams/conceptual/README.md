# DER Conceitual - Etapa 1

Arquivo principal:

- `diagrams/conceptual/er-diagram.mmd`

O DER apresenta:

- entidades da Etapa 1 com atributos principais;
- marcacao de `PK`, `FK` e `UK`;
- cardinalidades dos relacionamentos;
- especializacoes de `PESSOA` e `PROFISSIONAL`;
- entidade associativa `PROCEDIMENTO_REALIZADO` para o relacionamento entre atendimentos e procedimentos.

## Exportacao sugerida

Para gerar PNG com Mermaid CLI:

```bash
mmdc -i diagrams/conceptual/er-diagram.mmd -o diagrams/exports/er-diagram-phase-01.png
```

Para gerar PDF com Mermaid CLI:

```bash
mmdc -i diagrams/conceptual/er-diagram.mmd -o diagrams/exports/er-diagram-phase-01.pdf
```

Alternativa com Graphviz, usando o arquivo DOT em `modelagem/DER.dot`:

```bash
dot -Tpng modelagem/DER.dot -o modelagem/DER.png
dot -Tpdf modelagem/DER.dot -o modelagem/DER.pdf
```

## Documentos relacionados

- `docs/03-modeling/er-justification.md`
- `docs/03-modeling/relational-model.md`
- `docs/03-modeling/normalization-3nf.md`
