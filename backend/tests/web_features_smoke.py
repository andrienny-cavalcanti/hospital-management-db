from datetime import date, datetime

from app.db import SessionLocal
from app.routes import database_features
from app.schemas import (
    AdmissionCreate,
    AdmissionDischarge,
    CompleteAppointmentCreate,
    PerformedProcedureCreate,
    ScheduleAdjust,
)


def run() -> None:
    with SessionLocal() as session:
        admission = database_features.create_admission(
            AdmissionCreate(
                id_paciente=2,
                id_unidade=1,
                data_hora_entrada=datetime(2026, 7, 16, 8, 0),
            ),
            session,
        )
        active = database_features.current_admitted_patients(session)
        assert any(
            row["id_internacao"] == admission["id_internacao"]
            for row in active
        )
        discharge = database_features.discharge_admission(
            admission["id_internacao"],
            AdmissionDischarge(
                data_hora_saida=datetime(2026, 7, 16, 12, 0),
            ),
            session,
        )
        assert discharge["status"] == "ALTA"

        appointment = database_features.register_complete_appointment(
            CompleteAppointmentCreate(
                data_hora=datetime(2026, 7, 16, 13, 0),
                duracao_minutos=30,
                id_paciente=2,
                id_residente=6,
                id_preceptor=11,
                id_unidade=1,
                procedimentos=[
                    PerformedProcedureCreate(
                        id_procedimento=2,
                        quantidade=1,
                        tempo_real_minutos=10,
                        observacao="Smoke test da interface web",
                        faturado=False,
                        data_hora_inicio=datetime(2026, 7, 16, 13, 5),
                    )
                ],
            ),
            session,
        )
        assert appointment["procedimentos_registrados"] == 1

        waiting_time = database_features.calculate_average_waiting_time(session)
        assert isinstance(waiting_time, list)
        assert database_features.monthly_appointment_statistics(session)
        assert isinstance(
            database_features.residents_without_supervisor(session),
            list,
        )
        assert database_features.appointment_audit(100, session)

        adjusted = database_features.adjust_schedule(
            ScheduleAdjust(
                id_residente=10,
                data_origem=date(2026, 7, 14),
                turno_origem="noite",
                data_destino=date(2026, 7, 15),
                turno_destino="tarde",
            ),
            session,
        )
        assert adjusted["total_ajustado"] == 1

    print("Web features smoke test: OK")


if __name__ == "__main__":
    run()
