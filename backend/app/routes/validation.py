from fastapi import APIRouter, Depends
from psycopg import Connection

from app.db import get_connection

router = APIRouter(prefix="/validacao", tags=["Validacao"])


@router.get("/dados-minimos")
def validate_minimum_data(conn: Connection = Depends(get_connection)):
    with conn.cursor() as cur:
        cur.execute(
            """
            WITH validation_rules AS (
                SELECT
                    'Pacientes cadastrados' AS requisito,
                    5 AS minimo_esperado,
                    (SELECT COUNT(*) FROM paciente) AS total_encontrado
                UNION ALL
                SELECT 'Residentes cadastrados', 5, (SELECT COUNT(*) FROM residente)
                UNION ALL
                SELECT 'Preceptores cadastrados', 5, (SELECT COUNT(*) FROM preceptor)
                UNION ALL
                SELECT 'Unidades cadastradas', 3, (SELECT COUNT(*) FROM unidade)
                UNION ALL
                SELECT 'Atendimentos cadastrados', 10, (SELECT COUNT(*) FROM atendimento)
                UNION ALL
                SELECT
                    'Procedimentos realizados cadastrados',
                    10,
                    (SELECT COUNT(*) FROM procedimento_realizado)
            )
            SELECT
                requisito,
                minimo_esperado,
                total_encontrado,
                CASE
                    WHEN total_encontrado >= minimo_esperado THEN 'OK'
                    ELSE 'FALHA'
                END AS status
            FROM validation_rules
            ORDER BY requisito;
            """
        )
        rows = cur.fetchall()
        return {
            "status_geral_etapa_1": "OK"
            if all(row["status"] == "OK" for row in rows)
            else "FALHA",
            "checks": rows,
        }
