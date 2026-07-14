import os
from collections.abc import Iterator

from psycopg import Connection
from psycopg.rows import dict_row


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/hospital_management_db",
)


def get_connection() -> Iterator[Connection]:
    conn = Connection.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()
