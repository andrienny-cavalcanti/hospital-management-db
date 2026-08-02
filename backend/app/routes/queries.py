from datetime import date, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Numeric, case, cast, desc, exists, func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.db import get_session
from app.models import (
    Atendimento,
    Escala,
    Paciente,
    Pessoa,
    Preceptor,
    Procedimento,
    ProcedimentoRealizado,
    Profissional,
    Residente,
    Unidade,
)
from app.serializers import performed_procedure_dict, preceptor_dict

router = APIRouter(prefix="/consultas", tags=["Consultas"])


@router.get("/ranking-residentes")
def ranking_residents(session: Session = Depends(get_session)):
    total = func.count(Atendimento.id_atendimento).label("total_atendimentos")
    statement = (
        select(Pessoa.nome.label("residente"), total)
        .select_from(Residente)
        .join(Residente.profissional)
        .join(Profissional.pessoa)
        .outerjoin(
            Atendimento,
            Atendimento.id_residente == Residente.id_profissional,
        )
        .group_by(Pessoa.id_pessoa, Pessoa.nome)
        .order_by(desc(total), Pessoa.nome)
    )
    return [dict(row) for row in session.execute(statement).mappings()]


@router.get("/preceptores-por-mes")
def preceptors_by_month(
    ano: int = Query(2026, ge=1900),
    mes: int = Query(7, ge=1, le=12),
    minimo: int = Query(5, ge=0),
    session: Session = Depends(get_session),
):
    start = datetime(ano, mes, 1)
    end = datetime(ano + 1, 1, 1) if mes == 12 else datetime(ano, mes + 1, 1)
    total = func.count(Atendimento.id_atendimento).label(
        "total_supervisionados"
    )
    statement = (
        select(Pessoa.nome.label("preceptor"), total)
        .select_from(Preceptor)
        .join(Preceptor.profissional)
        .join(Profissional.pessoa)
        .join(
            Atendimento,
            Atendimento.id_preceptor == Preceptor.id_profissional,
        )
        .where(Atendimento.data_hora >= start, Atendimento.data_hora < end)
        .group_by(Pessoa.id_pessoa, Pessoa.nome)
        .having(total > minimo)
        .order_by(desc(total), Pessoa.nome)
    )
    return [dict(row) for row in session.execute(statement).mappings()]


@router.get("/plantoes-mes-corrente")
def current_month_schedules(session: Session = Depends(get_session)):
    today = date.today()
    start = date(today.year, today.month, 1)
    end = (
        date(today.year + 1, 1, 1)
        if today.month == 12
        else date(today.year, today.month + 1, 1)
    )
    total = func.count(Escala.id_escala).label(
        "total_plantoes_mes_corrente"
    )
    statement = (
        select(
            Unidade.nome.label("unidade"),
            Pessoa.nome.label("residente"),
            total,
        )
        .select_from(Escala)
        .join(Escala.unidade)
        .join(Escala.residente)
        .join(Residente.profissional)
        .join(Profissional.pessoa)
        .where(Escala.data_plantao >= start, Escala.data_plantao < end)
        .group_by(Unidade.id_unidade, Unidade.nome, Pessoa.id_pessoa, Pessoa.nome)
        .order_by(Unidade.nome, desc(total), Pessoa.nome)
    )
    return [dict(row) for row in session.execute(statement).mappings()]


@router.get("/pacientes-sem-risco-alto")
def patients_without_high_risk(session: Session = Depends(get_session)):
    high_risk = exists(
        select(1)
        .select_from(Atendimento)
        .join(
            ProcedimentoRealizado,
            ProcedimentoRealizado.id_atendimento
            == Atendimento.id_atendimento,
        )
        .join(
            Procedimento,
            Procedimento.id_procedimento
            == ProcedimentoRealizado.id_procedimento,
        )
        .where(
            Atendimento.id_paciente == Paciente.id_pessoa,
            Procedimento.nivel_risco == "ALTO",
        )
    )
    statement = (
        select(
            Paciente.id_pessoa.label("id_paciente"),
            Pessoa.nome.label("paciente"),
        )
        .select_from(Paciente)
        .join(Paciente.pessoa)
        .where(~high_risk)
        .order_by(Pessoa.nome)
    )
    return [dict(row) for row in session.execute(statement).mappings()]


@router.get("/demonstracao-carregamento/{id_atendimento}")
def relationship_loading_demo(
    id_atendimento: int,
    estrategia: Literal["lazy", "eager"] = Query("eager"),
    session: Session = Depends(get_session),
):
    if estrategia == "eager":
        statement = (
            select(Atendimento)
            .where(Atendimento.id_atendimento == id_atendimento)
            .options(
                selectinload(Atendimento.procedimentos).joinedload(
                    ProcedimentoRealizado.procedimento
                )
            )
        )
        appointment = session.scalar(statement)
    else:
        appointment = session.get(Atendimento, id_atendimento)

    if appointment is None:
        raise HTTPException(status_code=404, detail="Atendimento nao encontrado.")

    procedures = []
    for item in appointment.procedimentos:
        if estrategia == "lazy":
            item.procedimento
        procedures.append(performed_procedure_dict(item))

    return {
        "estrategia": estrategia,
        "descricao": (
            "Relacionamentos carregados junto com a consulta principal."
            if estrategia == "eager"
            else "Relacionamentos carregados quando foram acessados."
        ),
        "id_atendimento": appointment.id_atendimento,
        "procedimentos": procedures,
    }


@router.get("/avancadas/preceptores-pacientes-flamenguistas")
def preceptors_of_flamengo_patients(
    session: Session = Depends(get_session),
):
    statement = (
        select(Preceptor)
        .join(Preceptor.atendimentos)
        .join(Atendimento.paciente)
        .join(Paciente.pessoa)
        .where(Pessoa.is_flamengo.is_(True))
        .options(
            joinedload(Preceptor.profissional).joinedload(Profissional.pessoa)
        )
        .distinct()
    )
    preceptors = session.scalars(statement).all()
    return sorted(
        [preceptor_dict(preceptor) for preceptor in preceptors],
        key=lambda item: item["nome"],
    )


@router.get("/avancadas/ultimo-atendimento-pacientes")
def latest_appointment_by_patient(
    session: Session = Depends(get_session),
):
    patients_statement = (
        select(Paciente)
        .join(Paciente.pessoa)
        .options(joinedload(Paciente.pessoa))
        .order_by(Pessoa.nome)
    )
    all_patients = session.scalars(patients_statement).all()

    position = func.row_number().over(
        partition_by=Atendimento.id_paciente,
        order_by=(
            Atendimento.data_hora.desc(),
            Atendimento.id_atendimento.desc(),
        ),
    ).label("posicao")
    ranked_appointments = select(
        Atendimento.id_atendimento.label("id_atendimento"),
        position,
    ).subquery()

    latest_statement = (
        select(Atendimento)
        .join(
            ranked_appointments,
            ranked_appointments.c.id_atendimento
            == Atendimento.id_atendimento,
        )
        .where(ranked_appointments.c.posicao == 1)
        .options(
            joinedload(Atendimento.unidade),
            joinedload(Atendimento.residente)
            .joinedload(Residente.profissional)
            .joinedload(Profissional.pessoa),
            joinedload(Atendimento.preceptor)
            .joinedload(Preceptor.profissional)
            .joinedload(Profissional.pessoa),
            selectinload(Atendimento.procedimentos).joinedload(
                ProcedimentoRealizado.procedimento
            ),
        )
    )
    latest_by_patient = {
        appointment.id_paciente: appointment
        for appointment in session.scalars(latest_statement)
    }

    result = []
    for patient in all_patients:
        appointment = latest_by_patient.get(patient.id_pessoa)
        latest = None
        if appointment is not None:
            latest = {
                "id_atendimento": appointment.id_atendimento,
                "data_hora": appointment.data_hora,
                "duracao_minutos": appointment.duracao_minutos,
                "unidade": appointment.unidade.nome,
                "residente": appointment.residente.profissional.pessoa.nome,
                "preceptor": appointment.preceptor.profissional.pessoa.nome,
                "procedimentos": [
                    {
                        "id_procedimento": item.id_procedimento,
                        "nome": item.procedimento.nome,
                        "quantidade": item.quantidade,
                        "tempo_real_minutos": item.tempo_real_minutos,
                        "nivel_risco": item.procedimento.nivel_risco,
                    }
                    for item in sorted(
                        appointment.procedimentos,
                        key=lambda procedure: (
                            procedure.data_hora_inicio,
                            procedure.id_procedimento,
                        ),
                    )
                ],
            }

        result.append(
            {
                "id_paciente": patient.id_pessoa,
                "paciente": patient.pessoa.nome,
                "ultimo_atendimento": latest,
            }
        )

    return result


@router.get("/avancadas/percentual-risco-alto-residentes")
def high_risk_percentage_by_resident(
    session: Session = Depends(get_session),
):
    procedure_stats = (
        select(
            Atendimento.id_residente.label("id_residente"),
            func.sum(ProcedimentoRealizado.quantidade).label(
                "total_procedimentos"
            ),
            func.sum(
                case(
                    (
                        Procedimento.nivel_risco == "ALTO",
                        ProcedimentoRealizado.quantidade,
                    ),
                    else_=0,
                )
            ).label("procedimentos_alto_risco"),
        )
        .select_from(Atendimento)
        .join(Atendimento.procedimentos)
        .join(ProcedimentoRealizado.procedimento)
        .group_by(Atendimento.id_residente)
        .subquery()
    )

    total = func.coalesce(procedure_stats.c.total_procedimentos, 0)
    high_risk = func.coalesce(
        procedure_stats.c.procedimentos_alto_risco,
        0,
    )
    percentage = case(
        (
            total > 0,
            func.round(
                cast(high_risk * 100, Numeric) / total,
                2,
            ),
        ),
        else_=cast(0, Numeric),
    ).label("percentual_alto_risco")

    statement = (
        select(
            Residente.id_profissional.label("id_residente"),
            Pessoa.nome.label("residente"),
            total.label("total_procedimentos"),
            high_risk.label("procedimentos_alto_risco"),
            percentage,
        )
        .select_from(Residente)
        .join(Residente.profissional)
        .join(Profissional.pessoa)
        .outerjoin(
            procedure_stats,
            procedure_stats.c.id_residente == Residente.id_profissional,
        )
        .order_by(desc(percentage), Pessoa.nome)
    )
    return [dict(row) for row in session.execute(statement).mappings()]
