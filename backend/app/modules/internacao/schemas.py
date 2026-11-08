
"""
Schemas Pydantic do módulo Internação e Enfermagem.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ==========================
# INTERNAÇÃO
# ==========================

class InternacaoCreate(BaseModel):
    id_paciente: int
    id_medico_responsavel: Optional[int] = None
    data_entrada: Optional[datetime] = None
    data_saida: Optional[datetime] = None
    motivo_internacao: Optional[str] = None


class InternacaoUpdate(BaseModel):
    id_medico_responsavel: Optional[int] = None
    data_entrada: Optional[datetime] = None
    data_saida: Optional[datetime] = None
    motivo_internacao: Optional[str] = None


class InternacaoOut(InternacaoCreate):
    id_internacao: int
    model_config = ConfigDict(from_attributes=True)


# ==========================
# ENFERMEIRO
# ==========================

class EnfermeiroCreate(BaseModel):
    nome_enfermeiro: str
    coren: Optional[str] = None
    turno: Optional[str] = None
    telefone: Optional[str] = None


class EnfermeiroUpdate(BaseModel):
    nome_enfermeiro: Optional[str] = None
    coren: Optional[str] = None
    turno: Optional[str] = None
    telefone: Optional[str] = None


class EnfermeiroOut(EnfermeiroCreate):
    id_enfermeiro: int
    model_config = ConfigDict(from_attributes=True)


# ==========================
# ATENDIMENTO DE ENFERMAGEM
# ==========================

class AtendimentoEnfermeiroCreate(BaseModel):
    id_internacao: int
    id_enfermeiro: int
    data_enfermeiro: Optional[datetime] = None
    observacoes: Optional[str] = None


class AtendimentoEnfermeiroUpdate(BaseModel):
    data_enfermeiro: Optional[datetime] = None
    observacoes: Optional[str] = None


class AtendimentoEnfermeiroOut(AtendimentoEnfermeiroCreate):
    id_atendimento_enfermeiro: int
    model_config = ConfigDict(from_attributes=True)


# ==========================
# QUARTO
# ==========================

class QuartoCreate(BaseModel):
    numero_quarto: Optional[str] = None
    tipo: Optional[str] = None
    capacidade: Optional[int] = None
    status: Optional[str] = "disponivel"


class QuartoUpdate(BaseModel):
    numero_quarto: Optional[str] = None
    tipo: Optional[str] = None
    capacidade: Optional[int] = None
    status: Optional[str] = None


class QuartoOut(QuartoCreate):
    id_quarto: int
    model_config = ConfigDict(from_attributes=True)


# ==========================
# RELAÇÃO INTERNAÇÃO / QUARTO
# ==========================

class InternacaoQuartoCreate(BaseModel):
    id_internacao: int
    id_quarto: int
    data_entrada: Optional[datetime] = None
    data_saida: Optional[datetime] = None


class InternacaoQuartoUpdate(BaseModel):
    data_entrada: Optional[datetime] = None
    data_saida: Optional[datetime] = None


class InternacaoQuartoOut(InternacaoQuartoCreate):
    id_internacao_quarto: int
    model_config = ConfigDict(from_attributes=True)
