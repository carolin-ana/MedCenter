"""
Schemas Pydantic do módulo Corpo Clínico & Agenda.
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


# ---------- Especialidade ----------
class EspecialidadeCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    area: Optional[str] = None


class EspecialidadeUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    area: Optional[str] = None


class EspecialidadeOut(BaseModel):
    id_especialidade: int
    nome: Optional[str] = None
    descricao: Optional[str] = None
    area: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- Médico ----------
class MedicoCreate(BaseModel):
    nome: str
    crm: Optional[str] = None
    telefone: Optional[str] = None
    # Opcional: já vincula as especialidades na hora de cadastrar o médico
    ids_especialidades: List[int] = []


class MedicoUpdate(BaseModel):
    nome: Optional[str] = None
    crm: Optional[str] = None
    telefone: Optional[str] = None


class MedicoOut(BaseModel):
    id_medico: int
    nome: str
    crm: Optional[str] = None
    telefone: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- Vínculo médico <-> especialidade ----------
class VinculoEspecialidadeCreate(BaseModel):
    id_especialidade: int
    data_inicio: Optional[date] = None  # se não vier, usa a data de hoje


class VinculoEspecialidadeOut(BaseModel):
    id_relacao: int
    id_medico: int
    id_especialidade: int
    data_inicio: Optional[date] = None

    class Config:
        from_attributes = True


# ---------- Consulta ----------
class ConsultaCreate(BaseModel):
    id_paciente: int
    id_medico: int
    data_consulta: datetime
    status: str = "agendada"  # agendada, realizada, cancelada


class ConsultaUpdate(BaseModel):
    data_consulta: Optional[datetime] = None
    status: Optional[str] = None


class ConsultaOut(BaseModel):
    id_consulta: int
    id_paciente: int
    id_medico: int
    data_consulta: Optional[datetime] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- Atendimento ----------
class AtendimentoCreate(BaseModel):
    id_consulta: int
    descricao: Optional[str] = None
    diagnostico: Optional[str] = None
    observacoes: Optional[str] = None


class AtendimentoUpdate(BaseModel):
    descricao: Optional[str] = None
    diagnostico: Optional[str] = None
    observacoes: Optional[str] = None


class AtendimentoOut(BaseModel):
    id_atendimento: int
    id_consulta: int
    descricao: Optional[str] = None
    diagnostico: Optional[str] = None
    observacoes: Optional[str] = None

    class Config:
        from_attributes = True
