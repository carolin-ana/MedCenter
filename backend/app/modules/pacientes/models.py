"""
Models do módulo Pacientes.
Descrevem tabelas que já existem no MySQL (criadas manualmente) —
o SQLAlchemy não vai tentar recriá-las, só vai saber "lê-las".
"""

from sqlalchemy import Column, Integer, String, Date, Boolean, Text, ForeignKey

from app.core.database import Base


class Convenio(Base):
    __tablename__ = "convenio"

    id_convenio = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100))
    registro_ans = Column(String(20))
    telefone = Column(String(20))


class Paciente(Base):
    __tablename__ = "pacientes"

    id_paciente = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    data_nascimento = Column(Date)
    cpf = Column(String(14), unique=True)
    sexo = Column(String(1))
    id_convenio = Column(Integer, ForeignKey("convenio.id_convenio"), nullable=True)
    numero_carteirinha = Column(String(30))


class ContatoPaciente(Base):
    __tablename__ = "contato_paciente"

    id_contato = Column(Integer, primary_key=True, index=True)
    id_paciente = Column(Integer, ForeignKey("pacientes.id_paciente"), nullable=False)
    tipo_contato = Column(String(20))
    valor_contato = Column(String(150))
    eh_preferencial = Column(Boolean, default=False)


class Prontuario(Base):
    __tablename__ = "prontuario"

    id_prontuario = Column(Integer, primary_key=True, index=True)
    id_paciente = Column(Integer, ForeignKey("pacientes.id_paciente"), nullable=False)
    data_abertura = Column(Date)
    tipo_sangue = Column(String(3))
    observacoes = Column(Text)
