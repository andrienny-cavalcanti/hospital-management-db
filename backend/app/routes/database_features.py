import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.db import get_session
from app.models import AuditoriaAtendimento, Internacao, Paciente, Unidade
from app.schemas import (
    AdmissionCreate,
    AdmissionDischarge,
    CompleteAppointmentCreate,
    ScheduleAdjust,
)


router = APIRouter(tags=["Recursos avancados"])


def _rows(result) -> list[dict]:
    return [dict(row) for row in result.mappings()]


@router.get("/internacoes")
def list_admissions(session: Session = Depends(get_session)):
    statement = (
        select(Internacao)
        .options(
            joinedload(Internacao.paciente).joinedload(Paciente.pessoa),
            joinedload(Internacao.unidade),
        )
        .order_by(Internacao.data_hora_entrada.desc())
    )
    return [
        {
            "id_internacao": admission.id_internacao,
            "id_paciente": admission.id_paciente,
            "paciente": admission.paciente.pessoa.nome,
            "id_unidade": admission.id_unidade,
            "unidade": admission.unidade.nome,
            "data_hora_entrada": admission.data_hora_entrada,
            "data_hora_saida": admission.data_hora_saida,
            "status": (
                "INTERNADO"
                if admission.data_hora_saida is None
                else "ALTA"
            ),
        }
        for admission in session.scalars(statement)
    ]


@router.post("/internacoes", status_code=status.HTTP_201_CREATED)
def create_admission(
    payload: AdmissionCreate,
    session: Session = Depends(get_session),
):
    if session.get(Paciente, payload.id_paciente) is None:
        raise HTTPException(status_code=400, detail="Paciente inexistente.")
    if session.get(Unidade, payload.id_unidade) is None:
        raise HTTPException(status_code=400, detail="Unidade inexistente.")

    admission = Internacao(**payload.model_dump())
    try:
        session.add(admission)
        session.commit()
        return {
            "id_internacao": admission.id_internacao,
            **payload.model_dump(),
            "data_hora_saida": None,
            "status": "INTERNADO",
        }
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Paciente ja possui internacao ativa ou os dados sao invalidos.",
        ) from exc


@router.put("/internacoes/{id_internacao}/alta")
def discharge_admission(
    id_internacao: int,
    payload: AdmissionDischarge,
    session: Session = Depends(get_session),
):
    admission = session.get(Internacao, id_internacao)
    if admission is None:
        raise HTTPException(status_code=404, detail="Internacao nao encontrada.")
    if admission.data_hora_saida is not None:
        raise HTTPException(status_code=409, detail="Internacao ja encerrada.")
    if payload.data_hora_saida <= admission.data_hora_entrada:
        raise HTTPException(
            status_code=400,
            detail="A alta deve ocorrer depois da entrada.",
        )

    admission.data_hora_saida = payload.data_hora_saida
    session.commit()
    return {
        "id_internacao": admission.id_internacao,
        "data_hora_saida": admission.data_hora_saida,
        "status": "ALTA",
    }


@router.get("/recursos/views/pacientes-internados")
def current_admitted_patients(session: Session = Depends(get_session)):
    return _rows(
        session.execute(
            text(
                "SELECT * FROM vw_pacientes_internados "
                "ORDER BY data_hora_entrada DESC"
            )
        )
    )


@router.get("/recursos/views/residentes-sem-supervisor")
def residents_without_supervisor(session: Session = Depends(get_session)):
    return _rows(
        session.execute(
            text(
                "SELECT * FROM vw_residentes_sem_supervisor "
                "ORDER BY data_plantao, turno, residente"
            )
        )
    )


@router.get("/recursos/views/estatisticas-mensais")
def monthly_appointment_statistics(session: Session = Depends(get_session)):
    return _rows(
        session.execute(
            text(
                "SELECT * FROM vw_estatisticas_atendimentos_mensal "
                "ORDER BY mes DESC, unidade"
            )
        )
    )


@router.get("/recursos/auditoria")
def appointment_audit(
    limite: int = Query(100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    statement = (
        select(AuditoriaAtendimento)
        .order_by(AuditoriaAtendimento.data_hora.desc())
        .limit(limite)
    )
    return [
        {
            "id_auditoria": audit.id_auditoria,
            "id_atendimento": audit.id_atendimento,
            "operacao": audit.operacao,
            "usuario": audit.usuario,
            "data_hora": audit.data_hora,
            "dados_antigos": audit.dados_antigos,
            "dados_novos": audit.dados_novos,
        }
        for audit in session.scalars(statement)
    ]


@router.post("/recursos/procedures/atendimento-completo")
def register_complete_appointment(
    payload: CompleteAppointmentCreate,
    session: Session = Depends(get_session),
):
    procedures = [
        procedure.model_dump(mode="json")
        for procedure in payload.procedimentos
    ]
    try:
        result = session.execute(
            text(
                """
                CALL sp_registrar_atendimento_completo(
                    :data_hora,
                    :duracao_minutos,
                    :id_paciente,
                    :id_residente,
                    :id_preceptor,
                    :id_unidade,
                    CAST(:procedimentos AS JSONB),
                    NULL
                )
                """
            ),
            {
                "data_hora": payload.data_hora,
                "duracao_minutos": payload.duracao_minutos,
                "id_paciente": payload.id_paciente,
                "id_residente": payload.id_residente,
                "id_preceptor": payload.id_preceptor,
                "id_unidade": payload.id_unidade,
                "procedimentos": json.dumps(procedures),
            },
        )
        row = result.mappings().one()
        session.commit()
        return {
            "id_atendimento": row["p_id_atendimento"],
            "procedimentos_registrados": len(procedures),
            "status": "REGISTRADO",
        }
    except DBAPIError as exc:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc.orig),
        ) from exc


@router.get("/recursos/procedures/tempo-medio-espera")
def calculate_average_waiting_time(session: Session = Depends(get_session)):
    try:
        result = session.execute(
            text("CALL sp_calcular_tempo_medio_espera(NULL)")
        )
        row = result.mappings().one()
        session.commit()
        return row["p_resultado"]
    except DBAPIError as exc:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(exc.orig)) from exc


@router.post("/recursos/procedures/reajustar-escala")
def adjust_schedule(
    payload: ScheduleAdjust,
    session: Session = Depends(get_session),
):
    try:
        result = session.execute(
            text(
                """
                CALL sp_reajustar_escala(
                    :id_residente,
                    :data_origem,
                    :turno_origem,
                    :data_destino,
                    :turno_destino,
                    0
                )
                """
            ),
            payload.model_dump(),
        )
        row = result.mappings().one()
        session.commit()
        return {
            "total_ajustado": row["p_total_ajustado"],
            "status": "REAJUSTADO",
        }
    except DBAPIError as exc:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(exc.orig)) from exc
