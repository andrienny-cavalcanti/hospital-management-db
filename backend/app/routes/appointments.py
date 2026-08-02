from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.db import get_session
from app.models import (
    Atendimento,
    Paciente,
    Preceptor,
    Procedimento,
    ProcedimentoRealizado,
    Residente,
    Unidade,
)
from app.schemas import AppointmentCreate, PerformedProcedureCreate
from app.serializers import appointment_dict, performed_procedure_dict

router = APIRouter(prefix="/atendimentos", tags=["Atendimentos"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_appointment(
    payload: AppointmentCreate,
    session: Session = Depends(get_session),
):
    if payload.id_residente == payload.id_preceptor:
        raise HTTPException(status_code=400, detail="Residente e preceptor devem ser diferentes.")

    references = (
        session.get(Paciente, payload.id_paciente),
        session.get(Residente, payload.id_residente),
        session.get(Preceptor, payload.id_preceptor),
        session.get(Unidade, payload.id_unidade),
    )
    if any(reference is None for reference in references):
        raise HTTPException(
            status_code=400,
            detail="Paciente, residente, preceptor ou unidade inexistente.",
        )

    appointment = Atendimento(**payload.model_dump())
    try:
        session.add(appointment)
        session.commit()
        return appointment_dict(appointment)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail="Atendimento viola uma regra de integridade.",
        ) from exc


@router.get("/{id_atendimento}/procedimentos")
def list_appointment_procedures(
    id_atendimento: int,
    session: Session = Depends(get_session),
):
    statement = (
        select(ProcedimentoRealizado)
        .join(ProcedimentoRealizado.procedimento)
        .where(ProcedimentoRealizado.id_atendimento == id_atendimento)
        .options(joinedload(ProcedimentoRealizado.procedimento))
        .order_by(Procedimento.nome)
    )
    return [
        performed_procedure_dict(item)
        for item in session.scalars(statement)
    ]


@router.post("/{id_atendimento}/procedimentos", status_code=status.HTTP_201_CREATED)
def add_appointment_procedure(
    id_atendimento: int,
    payload: PerformedProcedureCreate,
    session: Session = Depends(get_session),
):
    if session.get(Atendimento, id_atendimento) is None:
        raise HTTPException(status_code=400, detail="Atendimento inexistente.")
    if session.get(Procedimento, payload.id_procedimento) is None:
        raise HTTPException(status_code=400, detail="Procedimento inexistente.")

    item = ProcedimentoRealizado(
        id_atendimento=id_atendimento,
        **payload.model_dump(),
    )
    try:
        session.add(item)
        session.commit()
        session.refresh(item, attribute_names=["procedimento"])
        return performed_procedure_dict(item)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Procedimento ja registrado para este atendimento.",
        ) from exc


@router.delete("/{id_atendimento}/procedimentos/{id_procedimento}")
def delete_appointment_procedure(
    id_atendimento: int,
    id_procedimento: int,
    session: Session = Depends(get_session),
):
    item = session.get(
        ProcedimentoRealizado,
        (id_atendimento, id_procedimento),
        options=[joinedload(ProcedimentoRealizado.procedimento)],
    )
    if item is None or item.faturado:
        raise HTTPException(
            status_code=404,
            detail="Procedimento nao encontrado ou ja faturado.",
        )

    deleted = performed_procedure_dict(item)
    session.delete(item)
    session.commit()
    return {"deleted": deleted}
