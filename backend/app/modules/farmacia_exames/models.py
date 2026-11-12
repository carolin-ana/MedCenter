
from app.core.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Text
from sqlalchemy.sql import func






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

class Prescricao(Base):
    __tablename__ = "prescricoes"

    id_prescricao = Column(Integer, primary_key = True, index = True)
    data_prescricao = Column(DateTime, nullable = False,server_default=func.now() )
    observacao = Column(String(255), nullable = True)
    status = Column(String(20),nullable = False, default = "ativa")

    id_atendimento = Column(Integer, ForeignKey("atendimentos.id_atendimento"), nullable = False
    )   

class PrescricaoMedicamento(Base):
    __tablename__ = "prescricao_medicamento"

    id_prescricao_medicamento = Column(Integer, primary_key= True, index = True)
    id_prescricao = Column(Integer, ForeignKey("prescricoes.id_prescricao"), nullable = False)
    id_medicamento = Column(Integer, ForeignKey("medicamento.id_medicamento"), nullable = False)
    
    dosagem = Column(String(100), nullable = False)
    frequencia = Column(String(100), nullable = False)
    duracao = Column(String(100), nullable = False)
    quantidade = Column(Integer, nullable = False)
    instrucoes = Column(Text, nullable = True)

class PedidoExame(Base):
    __tablename__ = "pedido_exame"

    id_pedido_exame = Column(Integer, primary_key = True, index = True)
    id_atendimento = Column(Integer, ForeignKey("atendimentos.id_atendimento"), nullable = False)
    data_pedido =Column(DateTime, nullable = False, server_default=func.now()
    )
    status = Column(String(20), nullable = False, default = "pendente")
    observacoes = Column(Text, nullable = True)

class PedidoExameItem(Base):
    __tablename__ = "pedido_exame_item"
    id_pedido_exame_item = Column(
        Integer,
        primary_key=True,
        index=True
        )

    id_pedido_exame = Column(
        Integer,
        ForeignKey("pedido_exame.id_pedido_exame"),
        nullable=False
        )

    id_exame = Column(
        Integer,
        ForeignKey("exame.id_exame"),
        nullable=False
        )

    observacoes = Column(Text, nullable=True)

    # Resultado do exame (previsto no diagrama ER do projeto)
    resultado = Column(Text, nullable=True)
    data_resultado = Column(Date, nullable=True)
