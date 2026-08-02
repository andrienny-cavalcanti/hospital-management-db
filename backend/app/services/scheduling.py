from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Escala, Residente


class ScheduleConflictError(ValueError):
    pass


class ResidentNotFoundError(ValueError):
    pass


def create_schedule_with_lock(
    session: Session,
    schedule: Escala,
    *,
    after_lock: Callable[[], None] | None = None,
) -> Escala:
    resident = session.scalar(
        select(Residente)
        .where(Residente.id_profissional == schedule.id_residente)
        .with_for_update()
    )
    if resident is None:
        raise ResidentNotFoundError(
            f"Residente {schedule.id_residente} nao encontrado."
        )

    if after_lock is not None:
        after_lock()

    existing_schedule = session.scalar(
        select(Escala.id_escala)
        .where(
            Escala.id_residente == schedule.id_residente,
            Escala.data_plantao == schedule.data_plantao,
            Escala.turno == schedule.turno,
        )
        .limit(1)
    )
    if existing_schedule is not None:
        raise ScheduleConflictError(
            "O residente ja possui escala na mesma data e turno."
        )

    session.add(schedule)
    session.flush()
    return schedule
