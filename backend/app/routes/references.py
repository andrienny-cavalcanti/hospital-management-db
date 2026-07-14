from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import Connection
from psycopg.errors import CheckViolation, ForeignKeyViolation, UniqueViolation

from app.db import get_connection
from app.schemas import PreceptorCreate, ProcedureCreate, ResidentCreate, ScheduleCreate, UnitCreate

router = APIRouter(tags=["Cadastros auxiliares"])


@router.get("/residentes")
def list_residents(conn: Connection = Depends(get_connection)):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT p.id_pessoa, p.nome, prof.crm, prof.especialidade, r.ano_residencia
            FROM residente r
            JOIN profissional prof ON prof.id_pessoa = r.id_profissional
            JOIN pessoa p ON p.id_pessoa = r.id_profissional
            ORDER BY p.nome;
            """
        )
        return cur.fetchall()


@router.post("/residentes", status_code=status.HTTP_201_CREATED)
def create_resident(payload: ResidentCreate, conn: Connection = Depends(get_connection)):
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
                    INSERT INTO profissional (id_pessoa, crm, data_admissao, especialidade)
                    VALUES (%s, %s, %s, %s)
                    RETURNING crm, data_admissao, especialidade;
                    """,
                    (
                        person["id_pessoa"],
                        payload.crm,
                        payload.data_admissao,
                        payload.especialidade,
                    ),
                )
                professional = cur.fetchone()
                cur.execute(
                    """
                    INSERT INTO residente (id_profissional, ano_residencia)
                    VALUES (%s, %s)
                    RETURNING ano_residencia;
                    """,
                    (person["id_pessoa"], payload.ano_residencia),
                )
                resident = cur.fetchone()
                return {**person, **professional, **resident}
    except UniqueViolation as exc:
        raise HTTPException(status_code=409, detail="CPF ou CRM ja cadastrado.") from exc


@router.get("/preceptores")
def list_preceptors(conn: Connection = Depends(get_connection)):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT p.id_pessoa, p.nome, prof.crm, prof.especialidade, pr.titulacao
            FROM preceptor pr
            JOIN profissional prof ON prof.id_pessoa = pr.id_profissional
            JOIN pessoa p ON p.id_pessoa = pr.id_profissional
            ORDER BY p.nome;
            """
        )
        return cur.fetchall()


@router.post("/preceptores", status_code=status.HTTP_201_CREATED)
def create_preceptor(payload: PreceptorCreate, conn: Connection = Depends(get_connection)):
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
                    INSERT INTO profissional (id_pessoa, crm, data_admissao, especialidade)
                    VALUES (%s, %s, %s, %s)
                    RETURNING crm, data_admissao, especialidade;
                    """,
                    (
                        person["id_pessoa"],
                        payload.crm,
                        payload.data_admissao,
                        payload.especialidade,
                    ),
                )
                professional = cur.fetchone()
                cur.execute(
                    """
                    INSERT INTO preceptor (id_profissional, titulacao)
                    VALUES (%s, %s)
                    RETURNING titulacao;
                    """,
                    (person["id_pessoa"], payload.titulacao),
                )
                preceptor = cur.fetchone()
                return {**person, **professional, **preceptor}
    except UniqueViolation as exc:
        raise HTTPException(status_code=409, detail="CPF ou CRM ja cadastrado.") from exc


@router.get("/unidades")
def list_units(conn: Connection = Depends(get_connection)):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM unidade ORDER BY nome;")
        return cur.fetchall()


@router.post("/unidades", status_code=status.HTTP_201_CREATED)
def create_unit(payload: UnitCreate, conn: Connection = Depends(get_connection)):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO unidade (nome, tipo, capacidade_leitos)
                VALUES (%s, %s, %s)
                RETURNING *;
                """,
                (payload.nome, payload.tipo, payload.capacidade_leitos),
            )
            row = cur.fetchone()
            conn.commit()
            return row
    except UniqueViolation as exc:
        raise HTTPException(status_code=409, detail="Unidade ja cadastrada.") from exc


@router.get("/procedimentos")
def list_procedures(conn: Connection = Depends(get_connection)):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM procedimento ORDER BY nome;")
        return cur.fetchall()


@router.post("/procedimentos", status_code=status.HTTP_201_CREATED)
def create_procedure(payload: ProcedureCreate, conn: Connection = Depends(get_connection)):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO procedimento (codigo, nome, tempo_medio_minutos, nivel_risco)
                VALUES (%s, %s, %s, %s)
                RETURNING *;
                """,
                (
                    payload.codigo,
                    payload.nome,
                    payload.tempo_medio_minutos,
                    payload.nivel_risco,
                ),
            )
            row = cur.fetchone()
            conn.commit()
            return row
    except UniqueViolation as exc:
        raise HTTPException(status_code=409, detail="Codigo de procedimento ja cadastrado.") from exc


@router.get("/escalas")
def list_schedules(conn: Connection = Depends(get_connection)):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                e.id_escala,
                u.nome AS unidade,
                e.data_plantao,
                e.dia_semana,
                e.turno,
                residente.nome AS residente,
                preceptor.nome AS preceptor
            FROM escala e
            JOIN unidade u ON u.id_unidade = e.id_unidade
            JOIN pessoa residente ON residente.id_pessoa = e.id_residente
            JOIN pessoa preceptor ON preceptor.id_pessoa = e.id_preceptor
            ORDER BY e.data_plantao, e.turno, u.nome;
            """
        )
        return cur.fetchall()


@router.post("/escalas", status_code=status.HTTP_201_CREATED)
def create_schedule(payload: ScheduleCreate, conn: Connection = Depends(get_connection)):
    if payload.id_residente == payload.id_preceptor:
        raise HTTPException(status_code=400, detail="Residente e preceptor devem ser diferentes.")

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO escala (
                    id_unidade,
                    data_plantao,
                    dia_semana,
                    turno,
                    id_residente,
                    id_preceptor
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *;
                """,
                (
                    payload.id_unidade,
                    payload.data_plantao,
                    payload.dia_semana,
                    payload.turno,
                    payload.id_residente,
                    payload.id_preceptor,
                ),
            )
            row = cur.fetchone()
            conn.commit()
            return row
    except UniqueViolation as exc:
        raise HTTPException(status_code=409, detail="Escala duplicada para a regra definida.") from exc
    except ForeignKeyViolation as exc:
        raise HTTPException(status_code=400, detail="Unidade, residente ou preceptor inexistente.") from exc
    except CheckViolation as exc:
        raise HTTPException(status_code=400, detail="Dados de escala violam uma regra CHECK.") from exc
