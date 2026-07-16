from __future__ import annotations

import threading
import time
from datetime import date, datetime

from sqlalchemy import delete, func, select

from app.db import SessionLocal
from app.models import Escala
from app.services.scheduling import (
    ScheduleConflictError,
    create_schedule_with_lock,
)


TARGET_DATE = date(2030, 1, 5)
TARGET_SHIFT = "manha"
RESIDENT_ID = 6


def run() -> None:
    output_lock = threading.Lock()
    first_lock_acquired = threading.Event()
    outcomes: dict[str, str] = {}
    created_ids: list[int] = []

    def log(transaction: str, message: str) -> None:
        timestamp = datetime.now().isoformat(timespec="milliseconds")
        with output_lock:
            print(f"{timestamp} [{transaction}] {message}", flush=True)

    with SessionLocal() as session:
        existing = session.scalar(
            select(func.count())
            .select_from(Escala)
            .where(
                Escala.id_residente == RESIDENT_ID,
                Escala.data_plantao == TARGET_DATE,
                Escala.turno == TARGET_SHIFT,
            )
        )
        if existing:
            raise RuntimeError(
                "A data usada pela demonstracao ja possui uma escala."
            )

    def worker(
        transaction: str,
        unit_id: int,
        preceptor_id: int,
        hold_lock: bool,
    ) -> None:
        if not hold_lock:
            if not first_lock_acquired.wait(timeout=5):
                outcomes[transaction] = "TIMEOUT"
                log(transaction, "timeout aguardando a primeira transacao")
                return

        started = time.monotonic()
        log(transaction, "BEGIN; tentando bloquear o residente")

        try:
            with SessionLocal() as session:
                with session.begin():
                    schedule = Escala(
                        id_unidade=unit_id,
                        data_plantao=TARGET_DATE,
                        dia_semana="sabado",
                        turno=TARGET_SHIFT,
                        id_residente=RESIDENT_ID,
                        id_preceptor=preceptor_id,
                        supervisao_ativa=True,
                    )

                    def after_lock() -> None:
                        waited = time.monotonic() - started
                        log(
                            transaction,
                            f"lock adquirido apos {waited:.3f}s",
                        )
                        if hold_lock:
                            first_lock_acquired.set()
                            log(
                                transaction,
                                "mantendo o lock por 1.2s para simular trabalho",
                            )
                            time.sleep(1.2)

                    create_schedule_with_lock(
                        session,
                        schedule,
                        after_lock=after_lock,
                    )
                    created_ids.append(schedule.id_escala)
                    log(
                        transaction,
                        f"escala {schedule.id_escala} preparada",
                    )

                outcomes[transaction] = "COMMIT"
                log(transaction, "COMMIT realizado")
        except ScheduleConflictError as exc:
            outcomes[transaction] = "CONFLICT"
            log(transaction, f"ROLLBACK por conflito: {exc}")

    first = threading.Thread(
        target=worker,
        args=("TX-A", 1, 11, True),
        daemon=True,
    )
    second = threading.Thread(
        target=worker,
        args=("TX-B", 2, 12, False),
        daemon=True,
    )

    first.start()
    second.start()
    first.join(timeout=10)
    second.join(timeout=10)

    if first.is_alive() or second.is_alive():
        raise RuntimeError("As transacoes concorrentes nao terminaram.")

    with SessionLocal() as session:
        final_count = session.scalar(
            select(func.count())
            .select_from(Escala)
            .where(
                Escala.id_residente == RESIDENT_ID,
                Escala.data_plantao == TARGET_DATE,
                Escala.turno == TARGET_SHIFT,
            )
        )

    assert outcomes == {"TX-A": "COMMIT", "TX-B": "CONFLICT"}
    assert final_count == 1
    assert len(created_ids) == 1

    log(
        "RESULT",
        "uma transacao confirmou, uma foi revertida e existe 1 escala",
    )

    with SessionLocal() as session:
        with session.begin():
            session.execute(
                delete(Escala).where(Escala.id_escala == created_ids[0])
            )
    log("CLEANUP", f"escala de teste {created_ids[0]} removida")
    print("Concurrency demo: OK")


if __name__ == "__main__":
    run()
