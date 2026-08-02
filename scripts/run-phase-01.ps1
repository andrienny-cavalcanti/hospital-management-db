param(
    [ValidateSet("setup", "validate", "demo", "all")]
    [string]$Mode = "all",
    [string]$Database = "hospital_management",
    [string]$User = "postgres"
)

$ErrorActionPreference = "Stop"

function Invoke-SqlFile {
    param([string]$Path)

    & psql -v ON_ERROR_STOP=1 -U $User -d $Database -f $Path
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao executar $Path (codigo $LASTEXITCODE)."
    }
}

function Invoke-Setup {
    Invoke-SqlFile "database/schema/01-create-tables.sql"
    Invoke-SqlFile "database/seeds/02-seed-data.sql"
}

function Invoke-Validation {
    Invoke-SqlFile "database/queries/05-validation-counts.sql"
}

function Invoke-Demo {
    Invoke-SqlFile "database/queries/03-crud-queries.sql"
    Invoke-SqlFile "database/queries/04-analytical-queries.sql"
}

switch ($Mode) {
    "setup" {
        Invoke-Setup
    }
    "validate" {
        Invoke-Validation
    }
    "demo" {
        Invoke-Demo
    }
    "all" {
        Invoke-Setup
        Invoke-Validation
        Invoke-Demo
    }
}
