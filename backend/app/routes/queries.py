from fastapi import APIRouter, Depends, Query
from psycopg import Connection

from app.db import get_connection

router = APIRouter(prefix="/consultas", tags=["Consultas"])


@router.get("/ranking-residentes")
def ranking_residents(conn: Connection = Depends(get_connection)):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                r.nome AS residente,
                COUNT(a.id_atendimento) AS total_atendimentos
            FROM residente res
            JOIN pessoa r ON r.id_pessoa = res.id_profissional
            LEFT JOIN atendimento a ON a.id_residente = res.id_profissional
            GROUP BY r.nome
            ORDER BY total_atendimentos DESC, r.nome;
            """
        )
        return cur.fetchall()


@router.get("/preceptores-por-mes")
def preceptors_by_month(
    ano: int = Query(2026, ge=1900),
    mes: int = Query(7, ge=1, le=12),
    minimo: int = Query(5, ge=0),
    conn: Connection = Depends(get_connection),
):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                p.nome AS preceptor,
                COUNT(a.id_atendimento) AS total_supervisionados
            FROM atendimento a
            JOIN pessoa p ON p.id_pessoa = a.id_preceptor
            WHERE a.data_hora >= make_date(%s, %s, 1)
              AND a.data_hora <  make_date(%s, %s, 1) + INTERVAL '1 month'
            GROUP BY p.nome
            HAVING COUNT(a.id_atendimento) > %s
            ORDER BY total_supervisionados DESC;
            """,
            (ano, mes, ano, mes, minimo),
        )
        return cur.fetchall()


@router.get("/plantoes-mes-corrente")
def current_month_schedules(conn: Connection = Depends(get_connection)):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                u.nome AS unidade,
                r.nome AS residente,
                COUNT(e.id_escala) AS total_plantoes_mes_corrente
            FROM escala e
            JOIN unidade u ON u.id_unidade = e.id_unidade
            JOIN pessoa r ON r.id_pessoa = e.id_residente
            WHERE e.data_plantao >= date_trunc('month', CURRENT_DATE)
              AND e.data_plantao <  date_trunc('month', CURRENT_DATE) + INTERVAL '1 month'
            GROUP BY u.nome, r.nome
            ORDER BY u.nome, total_plantoes_mes_corrente DESC, r.nome;
            """
        )
        return cur.fetchall()


@router.get("/pacientes-sem-risco-alto")
def patients_without_high_risk(conn: Connection = Depends(get_connection)):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                p.id_pessoa AS id_paciente,
                p.nome AS paciente
            FROM paciente pac
            JOIN pessoa p ON p.id_pessoa = pac.id_pessoa
            WHERE NOT EXISTS (
                SELECT 1
                FROM atendimento a
                JOIN procedimento_realizado pr ON pr.id_atendimento = a.id_atendimento
                JOIN procedimento proc ON proc.id_procedimento = pr.id_procedimento
                WHERE a.id_paciente = pac.id_pessoa
                  AND proc.nivel_risco = 'ALTO'
            )
            ORDER BY p.nome;
            """
        )
        return cur.fetchall()
