from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import Connection
from psycopg.errors import UniqueViolation

from app.db import get_connection
from app.schemas import PatientCreate, PatientUpdate

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


@router.get("")
def list_patients(conn: Connection = Depends(get_connection)):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                p.id_pessoa,
                p.nome,
                p.cpf,
                p.data_nascimento,
                p.is_flamengo,
                p.telefone,
                pac.num_convenio,
                pac.alergias,
                pac.grupo_sanguineo,
                pac.endereco
            FROM paciente pac
            JOIN pessoa p ON p.id_pessoa = pac.id_pessoa
            ORDER BY p.nome;
            """
        )
        return cur.fetchall()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_patient(payload: PatientCreate, conn: Connection = Depends(get_connection)):
    try:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO pessoa (nome, cpf, data_nascimento, is_flamengo, telefone)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id_pessoa, nome, cpf, data_nascimento, is_flamengo, telefone;
                    """,
                    (
                        payload.nome,
                        payload.cpf,
                        payload.data_nascimento,
                        payload.is_flamengo,
                        payload.telefone,
                    ),
                )
                person = cur.fetchone()
                cur.execute(
                    """
                    INSERT INTO paciente (id_pessoa, num_convenio, alergias, grupo_sanguineo, endereco)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING num_convenio, alergias, grupo_sanguineo, endereco;
                    """,
                    (
                        person["id_pessoa"],
                        payload.num_convenio,
                        payload.alergias,
                        payload.grupo_sanguineo,
                        payload.endereco,
                    ),
                )
                patient = cur.fetchone()
                return {**person, **patient}
    except UniqueViolation as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CPF ou numero de convenio ja cadastrado.",
        ) from exc


@router.put("/{id_pessoa}")
def update_patient(
    id_pessoa: int,
    payload: PatientUpdate,
    conn: Connection = Depends(get_connection),
):
    values = payload.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(status_code=400, detail="Informe ao menos um campo para atualizar.")

    assignments = []
    params = []
    for field, value in values.items():
        assignments.append(f"{field} = %s")
        params.append(value)
    params.append(id_pessoa)

    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE paciente
                SET {", ".join(assignments)}
                WHERE id_pessoa = %s
                RETURNING id_pessoa, num_convenio, alergias, grupo_sanguineo, endereco;
                """,
                params,
            )
            row = cur.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Paciente nao encontrado.")
            conn.commit()
            return row
    except UniqueViolation as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Numero de convenio ja cadastrado.",
        ) from exc


@router.get("/{id_pessoa}/atendimentos")
def list_patient_appointments(id_pessoa: int, conn: Connection = Depends(get_connection)):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                a.id_atendimento,
                a.data_hora,
                a.duracao_minutos,
                paciente.nome AS paciente,
                residente.nome AS residente,
                preceptor.nome AS preceptor
            FROM atendimento a
            JOIN pessoa paciente ON paciente.id_pessoa = a.id_paciente
            JOIN pessoa residente ON residente.id_pessoa = a.id_residente
            JOIN pessoa preceptor ON preceptor.id_pessoa = a.id_preceptor
            WHERE a.id_paciente = %s
            ORDER BY a.data_hora;
            """,
            (id_pessoa,),
        )
        return cur.fetchall()
