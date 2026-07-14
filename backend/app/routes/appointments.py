from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import Connection
from psycopg.errors import ForeignKeyViolation, UniqueViolation

from app.db import get_connection
from app.schemas import AppointmentCreate, PerformedProcedureCreate

router = APIRouter(prefix="/atendimentos", tags=["Atendimentos"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_appointment(payload: AppointmentCreate, conn: Connection = Depends(get_connection)):
    if payload.id_residente == payload.id_preceptor:
        raise HTTPException(status_code=400, detail="Residente e preceptor devem ser diferentes.")

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO atendimento (
                data_hora,
                duracao_minutos,
                id_paciente,
                id_residente,
                id_preceptor
            )
            SELECT %s, %s, %s, %s, %s
            WHERE EXISTS (SELECT 1 FROM paciente WHERE id_pessoa = %s)
              AND EXISTS (SELECT 1 FROM residente WHERE id_profissional = %s)
              AND EXISTS (SELECT 1 FROM preceptor WHERE id_profissional = %s)
            RETURNING *;
            """,
            (
                payload.data_hora,
                payload.duracao_minutos,
                payload.id_paciente,
                payload.id_residente,
                payload.id_preceptor,
                payload.id_paciente,
                payload.id_residente,
                payload.id_preceptor,
            ),
        )
        row = cur.fetchone()
        if row is None:
            raise HTTPException(
                status_code=400,
                detail="Paciente, residente ou preceptor inexistente.",
            )
        conn.commit()
        return row


@router.get("/{id_atendimento}/procedimentos")
def list_appointment_procedures(id_atendimento: int, conn: Connection = Depends(get_connection)):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                pr.id_atendimento,
                pr.id_procedimento,
                proc.nome AS procedimento,
                proc.nivel_risco,
                pr.quantidade,
                pr.tempo_real_minutos,
                pr.observacao,
                pr.faturado
            FROM procedimento_realizado pr
            JOIN procedimento proc ON proc.id_procedimento = pr.id_procedimento
            WHERE pr.id_atendimento = %s
            ORDER BY proc.nome;
            """,
            (id_atendimento,),
        )
        return cur.fetchall()


@router.post("/{id_atendimento}/procedimentos", status_code=status.HTTP_201_CREATED)
def add_appointment_procedure(
    id_atendimento: int,
    payload: PerformedProcedureCreate,
    conn: Connection = Depends(get_connection),
):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO procedimento_realizado (
                    id_atendimento,
                    id_procedimento,
                    quantidade,
                    tempo_real_minutos,
                    observacao,
                    faturado
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *;
                """,
                (
                    id_atendimento,
                    payload.id_procedimento,
                    payload.quantidade,
                    payload.tempo_real_minutos,
                    payload.observacao,
                    payload.faturado,
                ),
            )
            row = cur.fetchone()
            conn.commit()
            return row
    except ForeignKeyViolation as exc:
        raise HTTPException(
            status_code=400,
            detail="Atendimento ou procedimento inexistente.",
        ) from exc
    except UniqueViolation as exc:
        raise HTTPException(
            status_code=409,
            detail="Procedimento ja registrado para este atendimento.",
        ) from exc


@router.delete("/{id_atendimento}/procedimentos/{id_procedimento}")
def delete_appointment_procedure(
    id_atendimento: int,
    id_procedimento: int,
    conn: Connection = Depends(get_connection),
):
    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM procedimento_realizado
            WHERE id_atendimento = %s
              AND id_procedimento = %s
              AND faturado = FALSE
            RETURNING *;
            """,
            (id_atendimento, id_procedimento),
        )
        row = cur.fetchone()
        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Procedimento nao encontrado ou ja faturado.",
            )
        conn.commit()
        return {"deleted": row}
