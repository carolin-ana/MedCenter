"""
Schemas Pydantic do módulo Financeiro.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel


class FaturamentoCreate(BaseModel):
    id_paciente: int
    id_consulta: Optional[int] = None
    id_internacao: Optional[int] = None
    id_convenio: Optional[int] = None  # se não vier, a rota tenta puxar do paciente
    valor_total: float
    data_faturamento: date
    status: str = "pendente"


class FaturamentoUpdate(BaseModel):
    """Todos os campos opcionais — só envia o que quer alterar."""
    valor_total: Optional[float] = None
    data_faturamento: Optional[date] = None
    status: Optional[str] = None


class FaturamentoOut(BaseModel):
    id_faturamento: int
    id_paciente: int
    id_consulta: Optional[int] = None
    id_internacao: Optional[int] = None
    id_convenio: Optional[int] = None
    valor_total: float
    data_faturamento: date
    status: str

    class Config:
        from_attributes = True
