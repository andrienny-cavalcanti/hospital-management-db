param(
    [ValidateSet("setup", "sql", "orm", "concurrency", "validate", "all")]
    [string]$Mode = "all"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

function Resolve-Psql {
    $command = Get-Command psql -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $installations = Get-ChildItem "C:\Program Files\PostgreSQL" `
        -Directory -ErrorAction SilentlyContinue |
        Sort-Object Name -Descending
    foreach ($installation in $installations) {
        $candidate = Join-Path $installation.FullName "bin\psql.exe"
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    throw "psql nao foi encontrado no PATH nem em C:\Program Files\PostgreSQL."
}

function Resolve-DatabaseUrl {
    if ($env:DATABASE_URL) {
        return $env:DATABASE_URL
    }

    $envFile = Join-Path $ProjectRoot "backend\.env"
    if (Test-Path $envFile) {
        $entry = Get-Content -LiteralPath $envFile |
            Where-Object { $_ -match "^DATABASE_URL=" } |
            Select-Object -First 1
        if ($entry) {
            return $entry.Substring("DATABASE_URL=".Length)
        }
    }

    return "postgresql://postgres:postgres@localhost:5432/hospital_management"
}

$Psql = Resolve-Psql
$DatabaseUrl = Resolve-DatabaseUrl
$PsqlDatabaseUrl = $DatabaseUrl -replace "^postgresql\+psycopg://", "postgresql://"
$Python = Join-Path $ProjectRoot "backend\.venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "Ambiente virtual ausente. Crie backend\.venv e instale requirements.txt."
}

function Invoke-SqlFile {
    param([string]$RelativePath)

    $path = Join-Path $ProjectRoot $RelativePath
    & $Psql -X $PsqlDatabaseUrl -v ON_ERROR_STOP=1 -f $path
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao executar $RelativePath."
    }
}

function Invoke-Setup {
    Write-Host "Preparando schema, seeds e recursos da Etapa 2..."
    Invoke-SqlFile "database\schema\01-create-tables.sql"
    Invoke-SqlFile "database\seeds\02-seed-data.sql"
    Invoke-SqlFile "database\migrations\phase-02.sql"
}

function Invoke-SqlValidation {
    Write-Host "Executando validacoes SQL..."
    Invoke-SqlFile "database\queries\05-validation-counts.sql"
    Invoke-SqlFile "database\queries\06-validation-triggers.sql"
    Invoke-SqlFile "database\queries\07-validation-procedures.sql"
    Invoke-SqlFile "database\queries\08-validation-views.sql"
    Invoke-SqlFile "database\queries\09-validation-phase-02-summary.sql"
}

function Invoke-PythonTest {
    param([string]$RelativePath)

    $previousPythonPath = $env:PYTHONPATH
    $previousDatabaseUrl = $env:DATABASE_URL
    try {
        $env:PYTHONPATH = Join-Path $ProjectRoot "backend"
        $env:DATABASE_URL = $DatabaseUrl
        & $Python (Join-Path $ProjectRoot $RelativePath)
        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao executar $RelativePath."
        }
    }
    finally {
        $env:PYTHONPATH = $previousPythonPath
        $env:DATABASE_URL = $previousDatabaseUrl
    }
}

function Invoke-OrmValidation {
    Write-Host "Executando smoke test ORM..."
    Invoke-PythonTest "backend\tests\orm_smoke.py"
}

function Invoke-ConcurrencyValidation {
    Write-Host "Executando demonstracao de concorrencia..."
    Invoke-PythonTest "backend\tests\concurrency_demo.py"
}

switch ($Mode) {
    "setup" { Invoke-Setup }
    "sql" { Invoke-SqlValidation }
    "orm" { Invoke-OrmValidation }
    "concurrency" { Invoke-ConcurrencyValidation }
    "validate" {
        Invoke-SqlValidation
        Invoke-OrmValidation
        Invoke-ConcurrencyValidation
    }
    "all" {
        Invoke-Setup
        Invoke-SqlValidation
        Invoke-OrmValidation
        Invoke-ConcurrencyValidation
    }
}

Write-Host "Etapa 2 - modo $Mode concluido com sucesso."
