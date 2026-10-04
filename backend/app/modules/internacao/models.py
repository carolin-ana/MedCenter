"""
Models do módulo Internação & Enfermagem.
Descrevem tabelas que já existem no MySQL (criadas manualmente).
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey

from app.core.database import Base


class Internacao(Base):
    __tablename__ = "internacao"

    id_internacao = Column(Integer, primary_key=True, index=True)
    id_paciente = Column(Integer, ForeignKey("pacientes.id_paciente"), nullable=False)
    id_medico_responsavel = Column(Integer, ForeignKey("medicos.id_medico"), nullable=True)
    data_entrada = Column(DateTime)
    data_saida = Column(DateTime, nullable=True)
    motivo_internacao = Column(Text)


class Enfermeiro(Base):
    __tablename__ = "enfermeiros"

    id_enfermeiro = Column(Integer, primary_key=True, index=True)
    nome_enfermeiro = Column(String(150), nullable=False)
    coren = Column(String(20), unique=True)
    turno = Column(String(20))
    telefone = Column(String(20))


class AtendimentoEnfermeiro(Base):
    __tablename__ = "atendimento_enfermeiro"

    id_atendimento_enfermeiro = Column(Integer, primary_key=True, index=True)
    id_internacao = Column(Integer, ForeignKey("internacao.id_internacao"), nullable=False)
    id_enfermeiro = Column(Integer, ForeignKey("enfermeiros.id_enfermeiro"), nullable=False)
    data_enfermeiro = Column(DateTime)
    observacoes = Column(Text)


class Quarto(Base):
    __tablename__ = "quartos"

    id_quarto = Column(Integer, primary_key=True, index=True)
    numero_quarto = Column(String(10))
    tipo = Column(String(30))
    capacidade = Column(Integer)
    status = Column(String(20))  # disponivel, ocupado


class InternacaoQuarto(Base):
    __tablename__ = "internacao_quarto"

    id_internacao_quarto = Column(Integer, primary_key=True, index=True)
    id_internacao = Column(Integer, ForeignKey("internacao.id_internacao"), nullable=False)
    id_quarto = Column(Integer, ForeignKey("quartos.id_quarto"), nullable=False)
    data_entrada = Column(DateTime)
    data_saida = Column(DateTime, nullable=True)
