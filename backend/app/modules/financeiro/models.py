"""
Model do módulo Financeiro.
Descreve a tabela FATURAMENTO, que já existe no MySQL (criada manualmente).
"""

from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey

from app.core.database import Base


class Faturamento(Base):
    __tablename__ = "faturamento"

    id_faturamento = Column(Integer, primary_key=True, index=True)
    id_paciente = Column(Integer, ForeignKey("pacientes.id_paciente"), nullable=False)
    id_consulta = Column(Integer, ForeignKey("consulta.id_consulta"), nullable=True)
    id_internacao = Column(Integer, ForeignKey("internacao.id_internacao"), nullable=True)
    id_convenio = Column(Integer, ForeignKey("convenio.id_convenio"), nullable=True)
    valor_total = Column(Numeric(10, 2))
    data_faturamento = Column(Date)
    status = Column(String(20))  # pendente, pago, cancelado
