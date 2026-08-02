from app.models import (
    Atendimento,
    Escala,
    Paciente,
    Preceptor,
    Procedimento,
    ProcedimentoRealizado,
    Residente,
    Unidade,
)


def patient_dict(patient: Paciente) -> dict:
    person = patient.pessoa
    return {
        "id_pessoa": patient.id_pessoa,
        "nome": person.nome,
        "cpf": person.cpf,
        "data_nascimento": person.data_nascimento,
        "is_flamengo": person.is_flamengo,
        "telefone": person.telefone,
        "num_convenio": patient.num_convenio,
        "alergias": patient.alergias,
        "grupo_sanguineo": patient.grupo_sanguineo,
        "endereco": patient.endereco,
    }


def resident_dict(resident: Residente) -> dict:
    professional = resident.profissional
    person = professional.pessoa
    return {
        "id_pessoa": resident.id_profissional,
        "nome": person.nome,
        "cpf": person.cpf,
        "data_nascimento": person.data_nascimento,
        "is_flamengo": person.is_flamengo,
        "telefone": person.telefone,
        "crm": professional.crm,
        "data_admissao": professional.data_admissao,
        "especialidade": professional.especialidade,
        "ano_residencia": resident.ano_residencia,
    }


def preceptor_dict(preceptor: Preceptor) -> dict:
    professional = preceptor.profissional
    person = professional.pessoa
    return {
        "id_pessoa": preceptor.id_profissional,
        "nome": person.nome,
        "cpf": person.cpf,
        "data_nascimento": person.data_nascimento,
        "is_flamengo": person.is_flamengo,
        "telefone": person.telefone,
        "crm": professional.crm,
        "data_admissao": professional.data_admissao,
        "especialidade": professional.especialidade,
        "titulacao": preceptor.titulacao,
    }


def appointment_dict(appointment: Atendimento) -> dict:
    return {
        "id_atendimento": appointment.id_atendimento,
        "data_hora": appointment.data_hora,
        "duracao_minutos": appointment.duracao_minutos,
        "id_paciente": appointment.id_paciente,
        "id_residente": appointment.id_residente,
        "id_preceptor": appointment.id_preceptor,
        "id_unidade": appointment.id_unidade,
    }


def performed_procedure_dict(item: ProcedimentoRealizado) -> dict:
    return {
        "id_atendimento": item.id_atendimento,
        "id_procedimento": item.id_procedimento,
        "procedimento": item.procedimento.nome,
        "nivel_risco": item.procedimento.nivel_risco,
        "quantidade": item.quantidade,
        "tempo_real_minutos": item.tempo_real_minutos,
        "observacao": item.observacao,
        "faturado": item.faturado,
        "data_hora_inicio": item.data_hora_inicio,
    }


def unit_dict(unit: Unidade) -> dict:
    return {
        "id_unidade": unit.id_unidade,
        "nome": unit.nome,
        "tipo": unit.tipo,
        "capacidade_leitos": unit.capacidade_leitos,
    }


def procedure_dict(procedure: Procedimento) -> dict:
    return {
        "id_procedimento": procedure.id_procedimento,
        "codigo": procedure.codigo,
        "nome": procedure.nome,
        "tempo_medio_minutos": procedure.tempo_medio_minutos,
        "nivel_risco": procedure.nivel_risco,
        "media_tempo_procedimento": procedure.media_tempo_procedimento,
    }


def schedule_dict(schedule: Escala) -> dict:
    return {
        "id_escala": schedule.id_escala,
        "id_unidade": schedule.id_unidade,
        "unidade": schedule.unidade.nome,
        "data_plantao": schedule.data_plantao,
        "dia_semana": schedule.dia_semana,
        "turno": schedule.turno,
        "id_residente": schedule.id_residente,
        "residente": schedule.residente.profissional.pessoa.nome,
        "id_preceptor": schedule.id_preceptor,
        "preceptor": schedule.preceptor.profissional.pessoa.nome,
        "supervisao_ativa": schedule.supervisao_ativa,
    }
