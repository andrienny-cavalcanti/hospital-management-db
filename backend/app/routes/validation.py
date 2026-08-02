from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import (
    Atendimento,
    Paciente,
    Preceptor,
    ProcedimentoRealizado,
    Residente,
    Unidade,
)

router = APIRouter(prefix="/validacao", tags=["Validacao"])


@router.get("/dados-minimos")
def validate_minimum_data(session: Session = Depends(get_session)):
    rules = (
        ("Pacientes cadastrados", 5, Paciente),
        ("Residentes cadastrados", 5, Residente),
        ("Preceptores cadastrados", 5, Preceptor),
        ("Unidades cadastradas", 3, Unidade),
        ("Atendimentos cadastrados", 10, Atendimento),
        ("Procedimentos realizados cadastrados", 10, ProcedimentoRealizado),
    )
    checks = []
    for requirement, minimum, model in rules:
        total = session.scalar(select(func.count()).select_from(model))
        checks.append(
            {
                "requisito": requirement,
                "minimo_esperado": minimum,
                "total_encontrado": total,
                "status": "OK" if total >= minimum else "FALHA",
            }
        )

    return {
        "status_geral_etapa_1": (
            "OK" if all(item["status"] == "OK" for item in checks) else "FALHA"
        ),
        "checks": sorted(checks, key=lambda item: item["requisito"]),
    }
