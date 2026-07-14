from fastapi import FastAPI

from app.routes import appointments, patients, queries, references, validation

app = FastAPI(
    title="Hospital Management DB - Phase 01 API",
    description=(
        "Optional Swagger interface for manipulating the Phase 01 PostgreSQL "
        "database using pure SQL. The official academic delivery remains the "
        "SQL scripts in the database/ directory."
    ),
    version="1.0.0",
)


@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "docs": "/docs",
        "database_scripts": "database/",
    }


app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(references.router)
app.include_router(queries.router)
app.include_router(validation.router)
