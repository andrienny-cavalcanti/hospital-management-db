from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.db import get_session
from app.models import Atendimento, Paciente, Pessoa, Preceptor, Profissional, Residente
from app.schemas import PatientCreate, PatientUpdate
from app.serializers import patient_dict

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


@router.get("")
def list_patients(session: Session = Depends(get_session)):
    statement = (
        select(Paciente)
        .join(Paciente.pessoa)
        .options(joinedload(Paciente.pessoa))
        .order_by(Pessoa.nome)
    )
    return [patient_dict(patient) for patient in session.scalars(statement)]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_patient(payload: PatientCreate, session: Session = Depends(get_session)):
    person = Pessoa(
        nome=payload.nome,
        cpf=payload.cpf,
        data_nascimento=payload.data_nascimento,
        is_flamengo=payload.is_flamengo,
        telefone=payload.telefone,
    )
    patient = Paciente(
        pessoa=person,
        num_convenio=payload.num_convenio,
        alergias=payload.alergias,
        grupo_sanguineo=payload.grupo_sanguineo,
        endereco=payload.endereco,
    )

    try:
        session.add(patient)
        session.commit()
        return patient_dict(patient)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CPF ou numero de convenio ja cadastrado.",
        ) from exc


@router.put("/{id_pessoa}")
def update_patient(
    id_pessoa: int,
    payload: PatientUpdate,
    session: Session = Depends(get_session),
):
    values = payload.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(status_code=400, detail="Informe ao menos um campo para atualizar.")

    patient = session.get(Paciente, id_pessoa)
    if patient is None:
        raise HTTPException(status_code=404, detail="Paciente nao encontrado.")

    for field, value in values.items():
        setattr(patient, field, value)

    try:
        session.commit()
        return {
            "id_pessoa": patient.id_pessoa,
            "num_convenio": patient.num_convenio,
            "alergias": patient.alergias,
            "grupo_sanguineo": patient.grupo_sanguineo,
            "endereco": patient.endereco,
        }
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Numero de convenio ja cadastrado.",
        ) from exc


@router.get("/{id_pessoa}/atendimentos")
def list_patient_appointments(
    id_pessoa: int,
    session: Session = Depends(get_session),
):
    statement = (
        select(Atendimento)
        .where(Atendimento.id_paciente == id_pessoa)
        .options(
            joinedload(Atendimento.paciente).joinedload(Paciente.pessoa),
            joinedload(Atendimento.residente)
            .joinedload(Residente.profissional)
            .joinedload(Profissional.pessoa),
            joinedload(Atendimento.preceptor)
            .joinedload(Preceptor.profissional)
            .joinedload(Profissional.pessoa),
        )
        .order_by(Atendimento.data_hora)
    )
    appointments = session.scalars(statement).all()
    return [
        {
            "id_atendimento": appointment.id_atendimento,
            "data_hora": appointment.data_hora,
            "duracao_minutos": appointment.duracao_minutos,
            "paciente": appointment.paciente.pessoa.nome,
            "residente": appointment.residente.profissional.pessoa.nome,
            "preceptor": appointment.preceptor.profissional.pessoa.nome,
        }
        for appointment in appointments
    ]
