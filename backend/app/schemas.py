from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


BloodType = Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
RiskLevel = Literal["BAIXO", "MEDIO", "ALTO"]
Shift = Literal["manha", "tarde", "noite"]
Weekday = Literal["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]
ResidencyYear = Literal["R1", "R2", "R3"]


class PatientCreate(BaseModel):
    nome: str = Field(max_length=120)
    cpf: str = Field(pattern=r"^[0-9]{11}$")
    data_nascimento: date
    is_flamengo: bool = False
    telefone: str = Field(max_length=20)
    num_convenio: str = Field(max_length=40)
    alergias: str | None = None
    grupo_sanguineo: BloodType
    endereco: str | None = Field(default=None, max_length=160)


class PatientUpdate(BaseModel):
    num_convenio: str | None = Field(default=None, max_length=40)
    endereco: str | None = Field(default=None, max_length=160)


class ProfessionalBase(BaseModel):
    nome: str = Field(max_length=120)
    cpf: str = Field(pattern=r"^[0-9]{11}$")
    data_nascimento: date
    is_flamengo: bool = False
    telefone: str = Field(max_length=20)
    crm: str = Field(max_length=20)
    data_admissao: date
    especialidade: str = Field(max_length=80)


class ResidentCreate(ProfessionalBase):
    ano_residencia: ResidencyYear


class PreceptorCreate(ProfessionalBase):
    titulacao: str = Field(max_length=60)


class AppointmentCreate(BaseModel):
    data_hora: datetime
    duracao_minutos: int = Field(gt=0)
    id_paciente: int
    id_residente: int
    id_preceptor: int
    id_unidade: int


class PerformedProcedureCreate(BaseModel):
    id_procedimento: int
    quantidade: int = Field(gt=0)
    tempo_real_minutos: int = Field(gt=0)
    observacao: str | None = None
    faturado: bool = False
    data_hora_inicio: datetime


class UnitCreate(BaseModel):
    nome: str = Field(max_length=80)
    tipo: Literal["Enfermaria", "UTI", "Pronto-Socorro", "Ambulatorio"]
    capacidade_leitos: int = Field(ge=0)


class ProcedureCreate(BaseModel):
    codigo: str = Field(max_length=20)
    nome: str = Field(max_length=100)
    tempo_medio_minutos: int = Field(gt=0)
    nivel_risco: RiskLevel = "BAIXO"


class ScheduleCreate(BaseModel):
    id_unidade: int
    data_plantao: date
    dia_semana: Weekday
    turno: Shift
    id_residente: int
    id_preceptor: int
    supervisao_ativa: bool = True


class CompleteAppointmentCreate(AppointmentCreate):
    procedimentos: list[PerformedProcedureCreate] = Field(min_length=1)


class ScheduleAdjust(BaseModel):
    id_residente: int
    data_origem: date
    turno_origem: Shift
    data_destino: date
    turno_destino: Shift


class AdmissionCreate(BaseModel):
    id_paciente: int
    id_unidade: int
    data_hora_entrada: datetime


class AdmissionDischarge(BaseModel):
    data_hora_saida: datetime
