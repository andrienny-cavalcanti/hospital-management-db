from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.db import get_session
from app.models import (
    Escala,
    Pessoa,
    Preceptor,
    Procedimento,
    Profissional,
    Residente,
    Unidade,
)
from app.schemas import PreceptorCreate, ProcedureCreate, ResidentCreate, ScheduleCreate, UnitCreate
from app.services.scheduling import (
    ResidentNotFoundError,
    ScheduleConflictError,
    create_schedule_with_lock,
)
from app.serializers import (
    preceptor_dict,
    procedure_dict,
    resident_dict,
    schedule_dict,
    unit_dict,
)

router = APIRouter(tags=["Cadastros auxiliares"])


def _person_from_payload(payload: ResidentCreate | PreceptorCreate) -> Pessoa:
    return Pessoa(
        nome=payload.nome,
        cpf=payload.cpf,
        data_nascimento=payload.data_nascimento,
        is_flamengo=payload.is_flamengo,
        telefone=payload.telefone,
    )


def _professional_from_payload(
    payload: ResidentCreate | PreceptorCreate,
    person: Pessoa,
) -> Profissional:
    return Profissional(
        pessoa=person,
        crm=payload.crm,
        data_admissao=payload.data_admissao,
        especialidade=payload.especialidade,
    )


@router.get("/residentes")
def list_residents(session: Session = Depends(get_session)):
    statement = (
        select(Residente)
        .join(Residente.profissional)
        .join(Profissional.pessoa)
        .options(
            joinedload(Residente.profissional).joinedload(Profissional.pessoa)
        )
        .order_by(Pessoa.nome)
    )
    return [resident_dict(resident) for resident in session.scalars(statement)]


@router.post("/residentes", status_code=status.HTTP_201_CREATED)
def create_resident(
    payload: ResidentCreate,
    session: Session = Depends(get_session),
):
    person = _person_from_payload(payload)
    professional = _professional_from_payload(payload, person)
    resident = Residente(
        profissional=professional,
        ano_residencia=payload.ano_residencia,
    )

    try:
        session.add(resident)
        session.commit()
        return resident_dict(resident)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="CPF ou CRM ja cadastrado.") from exc


@router.get("/preceptores")
def list_preceptors(session: Session = Depends(get_session)):
    statement = (
        select(Preceptor)
        .join(Preceptor.profissional)
        .join(Profissional.pessoa)
        .options(
            joinedload(Preceptor.profissional).joinedload(Profissional.pessoa)
        )
        .order_by(Pessoa.nome)
    )
    return [
        preceptor_dict(preceptor)
        for preceptor in session.scalars(statement)
    ]


@router.post("/preceptores", status_code=status.HTTP_201_CREATED)
def create_preceptor(
    payload: PreceptorCreate,
    session: Session = Depends(get_session),
):
    person = _person_from_payload(payload)
    professional = _professional_from_payload(payload, person)
    preceptor = Preceptor(
        profissional=professional,
        titulacao=payload.titulacao,
    )

    try:
        session.add(preceptor)
        session.commit()
        return preceptor_dict(preceptor)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="CPF ou CRM ja cadastrado.") from exc


@router.get("/unidades")
def list_units(session: Session = Depends(get_session)):
    statement = select(Unidade).order_by(Unidade.nome)
    return [unit_dict(unit) for unit in session.scalars(statement)]


@router.post("/unidades", status_code=status.HTTP_201_CREATED)
def create_unit(payload: UnitCreate, session: Session = Depends(get_session)):
    unit = Unidade(**payload.model_dump())
    try:
        session.add(unit)
        session.commit()
        return unit_dict(unit)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="Unidade ja cadastrada.") from exc


@router.get("/procedimentos")
def list_procedures(session: Session = Depends(get_session)):
    statement = select(Procedimento).order_by(Procedimento.nome)
    return [
        procedure_dict(procedure)
        for procedure in session.scalars(statement)
    ]


@router.post("/procedimentos", status_code=status.HTTP_201_CREATED)
def create_procedure(
    payload: ProcedureCreate,
    session: Session = Depends(get_session),
):
    procedure = Procedimento(**payload.model_dump())
    try:
        session.add(procedure)
        session.commit()
        return procedure_dict(procedure)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="Codigo de procedimento ja cadastrado.") from exc


@router.get("/escalas")
def list_schedules(session: Session = Depends(get_session)):
    statement = (
        select(Escala)
        .join(Escala.unidade)
        .options(
            joinedload(Escala.unidade),
            joinedload(Escala.residente)
            .joinedload(Residente.profissional)
            .joinedload(Profissional.pessoa),
            joinedload(Escala.preceptor)
            .joinedload(Preceptor.profissional)
            .joinedload(Profissional.pessoa),
        )
        .order_by(Escala.data_plantao, Escala.turno, Unidade.nome)
    )
    return [schedule_dict(schedule) for schedule in session.scalars(statement)]


@router.post("/escalas", status_code=status.HTTP_201_CREATED)
def create_schedule(
    payload: ScheduleCreate,
    session: Session = Depends(get_session),
):
    if payload.id_residente == payload.id_preceptor:
        raise HTTPException(status_code=400, detail="Residente e preceptor devem ser diferentes.")

    schedule = Escala(**payload.model_dump())
    try:
        with session.begin():
            create_schedule_with_lock(session, schedule)
        statement = (
            select(Escala)
            .where(Escala.id_escala == schedule.id_escala)
            .options(
                joinedload(Escala.unidade),
                joinedload(Escala.residente)
                .joinedload(Residente.profissional)
                .joinedload(Profissional.pessoa),
                joinedload(Escala.preceptor)
                .joinedload(Preceptor.profissional)
                .joinedload(Profissional.pessoa),
            )
        )
        return schedule_dict(session.scalar(statement))
    except ScheduleConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc
    except ResidentNotFoundError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except IntegrityError as exc:
        session.rollback()
        sqlstate = getattr(exc.orig, "sqlstate", None)
        if sqlstate == "23505":
            raise HTTPException(
                status_code=409,
                detail="Escala duplicada ou sobreposta.",
            ) from exc
        raise HTTPException(
            status_code=400,
            detail="Dados de escala violam uma regra de integridade.",
        ) from exc
