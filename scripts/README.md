# Scripts

Este diretorio armazena scripts auxiliares para executar ou validar o projeto.

## Scripts disponiveis

- `run-phase-01.sh`: executor para Bash.
- `run-phase-01.ps1`: executor para PowerShell no Windows.
- `run-phase-02.sh`: executor completo da Etapa 2 para Bash.
- `run-phase-02.ps1`: executor completo da Etapa 2 para PowerShell.

Os executores separam o fluxo da Etapa 1 em quatro modos:

- `setup`: recria as tabelas e carrega os seeds.
- `validate`: verifica apenas os dados minimos.
- `demo`: executa CRUD e consultas analiticas, alterando os dados de demonstracao.
- `all`: executa setup, validacao e demonstracao, nessa ordem.

## PowerShell

```powershell
.\scripts\run-phase-01.ps1 setup
.\scripts\run-phase-01.ps1 validate
.\scripts\run-phase-01.ps1 demo
```

Para executar o fluxo completo:

```powershell
.\scripts\run-phase-01.ps1 all
```

Banco e usuario podem ser informados depois do modo:

```powershell
.\scripts\run-phase-01.ps1 setup hospital_management postgres
```

## Bash

```bash
bash scripts/run-phase-01.sh setup
bash scripts/run-phase-01.sh validate
bash scripts/run-phase-01.sh demo
```

Para executar o fluxo completo:

```bash
bash scripts/run-phase-01.sh all
```

Banco e usuario podem ser informados depois do modo:

```bash
bash scripts/run-phase-01.sh setup hospital_management postgres
```

## Etapa 2

Modos disponiveis:

- `setup`: recria a base e aplica migracao, triggers, procedures e views.
- `sql`: executa todas as validacoes SQL.
- `orm`: executa o smoke test SQLAlchemy.
- `concurrency`: executa as duas transacoes concorrentes.
- `validate`: executa SQL, ORM e concorrencia sem recriar a base.
- `all`: recria a base e executa todas as validacoes.

PowerShell:

```powershell
.\scripts\run-phase-02.ps1 all
```

Bash:

```bash
bash scripts/run-phase-02.sh all
```

O modo `all` recria as tabelas do projeto. Use `validate` para testar uma base
ja preparada sem executar novamente o schema e os seeds.
