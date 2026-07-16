import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import (
    appointments,
    database_features,
    patients,
    queries,
    references,
    validation,
)

app = FastAPI(
    title="Hospital Management DB - Phase 02 ORM API",
    description=(
        "Swagger interface for the Phase 02 PostgreSQL database. CRUD, "
        "relationships and analytical queries are implemented with "
        "SQLAlchemy 2.x ORM."
    ),
    version="2.0.0",
)

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "docs": "/docs",
        "data_access": "SQLAlchemy ORM",
        "database_scripts": "database/",
    }


app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(references.router)
app.include_router(queries.router)
app.include_router(validation.router)
app.include_router(database_features.router)
