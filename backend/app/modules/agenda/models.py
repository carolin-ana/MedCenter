"""
Models do módulo Corpo Clínico & Agenda.
Descrevem tabelas que já existem no MySQL (criadas manualmente).
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey

from app.core.database import Base


class Especialidade(Base):
    __tablename__ = "especialidade"

    id_especialidade = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100))
    descricao = Column(String(255))
    area = Column(String(100))


class Medico(Base):
    __tablename__ = "medicos"

    id_medico = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    crm = Column(String(20), unique=True)
    telefone = Column(String(20))


class MedicoEspecialidade(Base):
    __tablename__ = "medico_especialidade"

    id_relacao = Column(Integer, primary_key=True, index=True)
    id_medico = Column(Integer, ForeignKey("medicos.id_medico"), nullable=False)
    id_especialidade = Column(Integer, ForeignKey("especialidade.id_especialidade"), nullable=False)
    data_inicio = Column(Date)


class Consulta(Base):
    __tablename__ = "consulta"

    id_consulta = Column(Integer, primary_key=True, index=True)
    id_paciente = Column(Integer, ForeignKey("pacientes.id_paciente"), nullable=False)
    id_medico = Column(Integer, ForeignKey("medicos.id_medico"), nullable=False)
    data_consulta = Column(DateTime)
    status = Column(String(20))  # agendada, realizada, cancelada


class Atendimento(Base):
    __tablename__ = "atendimentos"

    id_atendimento = Column(Integer, primary_key=True, index=True)
    id_consulta = Column(Integer, ForeignKey("consulta.id_consulta"), nullable=False)
    descricao = Column(Text)
    diagnostico = Column(Text)
    observacoes = Column(Text)
