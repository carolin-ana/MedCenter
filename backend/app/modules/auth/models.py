"""
Model da tabela USUARIOS.
"""

from sqlalchemy import Column, Integer, String

from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    senha = Column(String(255), nullable=False)  # sempre o hash, nunca a senha em texto puro
    perfil = Column(String(20), nullable=False)  # admin, medico, enfermeira, recepcao
