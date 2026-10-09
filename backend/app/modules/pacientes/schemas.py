"""
Schemas Pydantic do módulo Pacientes.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel


# ---------- Convenio ----------
class ConvenioCreate(BaseModel):
    nome: str
    registro_ans: Optional[str] = None
    telefone: Optional[str] = None


class ConvenioOut(BaseModel):
    id_convenio: int
    nome: str
    registro_ans: Optional[str] = None
    telefone: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- Paciente ----------
class PacienteCreate(BaseModel):
    nome: str
    data_nascimento: Optional[date] = None
    cpf: Optional[str] = None
    sexo: Optional[str] = None
    id_convenio: Optional[int] = None  # None = particular
    numero_carteirinha: Optional[str] = None


class PacienteUpdate(BaseModel):
    nome: Optional[str] = None
    data_nascimento: Optional[date] = None
    cpf: Optional[str] = None
    sexo: Optional[str] = None
    id_convenio: Optional[int] = None
    numero_carteirinha: Optional[str] = None


class PacienteOut(BaseModel):
    id_paciente: int
    nome: str
    data_nascimento: Optional[date] = None
    cpf: Optional[str] = None
    sexo: Optional[str] = None
    id_convenio: Optional[int] = None
    numero_carteirinha: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- Contato do paciente ----------
class ContatoPacienteCreate(BaseModel):
    id_paciente: int
    tipo_contato: str
    valor_contato: str
    eh_preferencial: bool = False


class ContatoPacienteOut(BaseModel):
    id_contato: int
    id_paciente: int
    tipo_contato: str
    valor_contato: str
    eh_preferencial: bool

    class Config:
        from_attributes = True


# ---------- Prontuário ----------
class ProntuarioCreate(BaseModel):
    id_paciente: int
    data_abertura: Optional[date] = None
    tipo_sangue: Optional[str] = None
    observacoes: Optional[str] = None


class ProntuarioOut(BaseModel):
    id_prontuario: int
    id_paciente: int
    data_abertura: Optional[date] = None
    tipo_sangue: Optional[str] = None
    observacoes: Optional[str] = None

    class Config:
        from_attributes = True
