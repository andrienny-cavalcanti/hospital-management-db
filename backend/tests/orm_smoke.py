from datetime import date, datetime

from sqlalchemy.orm import configure_mappers

from app.db import SessionLocal
from app.models import Base
from app.routes import appointments, patients, queries, references, validation
from app.schemas import (
    AppointmentCreate,
    PatientCreate,
    PatientUpdate,
    PerformedProcedureCreate,
    PreceptorCreate,
    ProcedureCreate,
    ResidentCreate,
    ScheduleCreate,
    UnitCreate,
)


def run() -> None:
    configure_mappers()
    assert len(Base.registry.mappers) == 12

    with SessionLocal() as session:
        assert len(patients.list_patients(session)) == 5
        assert len(references.list_residents(session)) == 5
        assert len(references.list_preceptors(session)) == 5
        assert len(references.list_units(session)) == 3
        assert len(references.list_procedures(session)) == 6
        assert len(references.list_schedules(session)) == 10
        assert validation.validate_minimum_data(session)["status_geral_etapa_1"] == "OK"

        patient = patients.create_patient(
            PatientCreate(
                nome="Paciente ORM",
                cpf="17171717171",
                data_nascimento=date(1992, 8, 10),
                telefone="83990000171",
                num_convenio="CONV-ORM-01",
                grupo_sanguineo="A+",
                endereco="Rua ORM, 10",
            ),
            session,
        )
        patients.update_patient(
            patient["id_pessoa"],
            PatientUpdate(endereco="Rua ORM, 20"),
            session,
        )

        resident = references.create_resident(
            ResidentCreate(
                nome="Residente ORM",
                cpf="18181818181",
                data_nascimento=date(1996, 1, 10),
                telefone="83990000181",
                crm="CRM-ORM-R",
                data_admissao=date(2026, 1, 10),
                especialidade="Clinica Medica",
                ano_residencia="R1",
            ),
            session,
        )
        preceptor = references.create_preceptor(
            PreceptorCreate(
                nome="Preceptor ORM",
                cpf="19191919191",
                data_nascimento=date(1975, 1, 10),
                telefone="83990000191",
                crm="CRM-ORM-P",
                data_admissao=date(2010, 1, 10),
                especialidade="Clinica Medica",
                titulacao="Doutor",
            ),
            session,
        )
        unit = references.create_unit(
            UnitCreate(
                nome="Unidade ORM",
                tipo="Ambulatorio",
                capacidade_leitos=5,
            ),
            session,
        )
        procedure = references.create_procedure(
            ProcedureCreate(
                codigo="PROC-ORM",
                nome="Procedimento ORM",
                tempo_medio_minutos=20,
                nivel_risco="BAIXO",
            ),
            session,
        )
        schedule = references.create_schedule(
            ScheduleCreate(
                id_unidade=unit["id_unidade"],
                data_plantao=date(2026, 7, 20),
                dia_semana="segunda",
                turno="tarde",
                id_residente=resident["id_pessoa"],
                id_preceptor=preceptor["id_pessoa"],
            ),
            session,
        )
        assert schedule["residente"] == "Residente ORM"

        appointment = appointments.create_appointment(
            AppointmentCreate(
                data_hora=datetime(2026, 7, 20, 14, 0),
                duracao_minutos=45,
                id_paciente=patient["id_pessoa"],
                id_residente=resident["id_pessoa"],
                id_preceptor=preceptor["id_pessoa"],
                id_unidade=unit["id_unidade"],
            ),
            session,
        )
        appointments.add_appointment_procedure(
            appointment["id_atendimento"],
            PerformedProcedureCreate(
                id_procedimento=procedure["id_procedimento"],
                quantidade=1,
                tempo_real_minutos=18,
                observacao="Teste ORM",
                data_hora_inicio=datetime(2026, 7, 20, 14, 5),
            ),
            session,
        )

        assert len(
            appointments.list_appointment_procedures(
                appointment["id_atendimento"],
                session,
            )
        ) == 1
        assert len(
            patients.list_patient_appointments(
                patient["id_pessoa"],
                session,
            )
        ) == 1
        assert len(queries.ranking_residents(session)) == 6
        queries.preceptors_by_month(2026, 7, 0, session)
        queries.current_month_schedules(session)
        queries.patients_without_high_risk(session)

        flamengo_preceptors = queries.preceptors_of_flamengo_patients(session)
        assert {
            item["id_pessoa"] for item in flamengo_preceptors
        } == {11, 12, 13}

        latest_appointments = queries.latest_appointment_by_patient(session)
        assert len(latest_appointments) == 6
        latest_by_patient = {
            item["id_paciente"]: item["ultimo_atendimento"]
            for item in latest_appointments
        }
        assert latest_by_patient[1]["id_atendimento"] == 6
        assert (
            latest_by_patient[patient["id_pessoa"]]["id_atendimento"]
            == appointment["id_atendimento"]
        )
        assert len(
            latest_by_patient[patient["id_pessoa"]]["procedimentos"]
        ) == 1

        risk_percentages = queries.high_risk_percentage_by_resident(session)
        risk_by_resident = {
            item["id_residente"]: item for item in risk_percentages
        }
        assert risk_by_resident[7]["percentual_alto_risco"] == 50
        assert risk_by_resident[9]["percentual_alto_risco"] == 50
        assert risk_by_resident[6]["percentual_alto_risco"] == 0

    with SessionLocal() as session:
        eager = queries.relationship_loading_demo(
            appointment["id_atendimento"],
            "eager",
            session,
        )
        assert eager["estrategia"] == "eager"
        assert len(eager["procedimentos"]) == 1

    with SessionLocal() as session:
        lazy = queries.relationship_loading_demo(
            appointment["id_atendimento"],
            "lazy",
            session,
        )
        assert lazy["estrategia"] == "lazy"
        assert len(lazy["procedimentos"]) == 1
        appointments.delete_appointment_procedure(
            appointment["id_atendimento"],
            procedure["id_procedimento"],
            session,
        )

    print("ORM smoke test: OK")


if __name__ == "__main__":
    run()
