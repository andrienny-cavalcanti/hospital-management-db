# Relatorios da Etapa 2

Arquivos da entrega:

- `phase-02-report.md`: fonte textual do relatorio breve.
- `phase-02-report.pdf`: relatorio final em duas paginas.
- `final-validation.md`: evidencia da validacao ponta a ponta.
- `concurrency-demo.log`: log real das duas transacoes.
- `requirements.txt`: dependencia usada somente para gerar o PDF.

O relatorio da Etapa 1 permanece em `reports/phase-01/`.

Para regenerar o PDF:

```powershell
.\backend\.venv\Scripts\python.exe -m pip install -r reports\phase-02\requirements.txt
.\backend\.venv\Scripts\python.exe scripts\generate-phase-02-report.py
```
