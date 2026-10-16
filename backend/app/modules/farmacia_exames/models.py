from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Medicamento(Base):
    __tablename__ = "medicamento"

    id_medicamento = Column(Integer, primary_key = True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(255), nullable=True)
    quantidade_estoque = Column(Integer, nullable=False, default = 0)


class Exame(Base):
    __tablename__ = "exame"

    id_exame = Column(Integer, primary_key = True, index = True)
    nome = Column(String(100), nullable = False)
    descricao = Column(String(255), nullable = True)
