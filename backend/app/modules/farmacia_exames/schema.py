
from pydantic import BaseModel, ConfigDict


class MedicamentoCreate(BaseModel):
    nome: str
    descricao: str | None = None
    quantidade_estoque: int = 0


class MedicamentoResponse(MedicamentoCreate):
    id_medicamento: int

    model_config = ConfigDict(from_attributes=True)


class ExameCreate(BaseModel):
    nome: str
    descricao: str | None = None


class ExameResponse(ExameCreate):
    id_exame: int

    model_config = ConfigDict(from_attributes=True)



from datetime import datetime


class PrescricaoCreate(BaseModel):
    id_atendimento: int
    observacao: str | None = None
    status: str = "ativa"


class PrescricaoResponse(PrescricaoCreate):
    id_prescricao: int
    data_prescricao: datetime

    model_config = ConfigDict(from_attributes=True)



class PrescricaoMedicamentoCreate(BaseModel):
    id_prescricao: int
    id_medicamento: int
    dosagem: str
    frequencia: str
    duracao: str
    quantidade: int
    instrucoes: str | None = None


class PrescricaoMedicamentoResponse(PrescricaoMedicamentoCreate):
    id_prescricao_medicamento: int

    model_config = ConfigDict(from_attributes=True)




class PedidoExameCreate(BaseModel):
    id_atendimento: int
    status: str = "pendente"
    observacoes: str | None = None


class PedidoExameResponse(PedidoExameCreate):
    id_pedido_exame: int
    data_pedido: datetime

    model_config = ConfigDict(from_attributes=True)





class PedidoExameItemCreate(BaseModel):
    id_pedido_exame: int
    id_exame: int
    observacoes: str | None = None


class PedidoExameItemResponse(PedidoExameItemCreate):
    id_pedido_exame_item: int

    model_config = ConfigDict(from_attributes=True)


