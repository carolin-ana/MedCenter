
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.farmacia_exames import service
from app.modules.farmacia_exames.models import Medicamento, Exame, Prescricao, PrescricaoMedicamento, PedidoExame, PedidoExameItem

from app.modules.farmacia_exames.schema import (
    MedicamentoCreate,
    MedicamentoResponse,
    ExameCreate,
    ExameResponse,
    PrescricaoCreate,
    PrescricaoResponse,
    PrescricaoMedicamentoCreate,
    PrescricaoMedicamentoResponse,
    PedidoExameCreate,
    PedidoExameResponse,
    PedidoExameItemCreate,
    PedidoExameItemResponse,
)


router = APIRouter()

from pydantic import BaseModel

class MedicamentoEntrada(BaseModel):
    nome: str
    descricao: str | None = None
    quantidade_estoque: int = 0

class ExameEntrada(BaseModel):
    nome: str
    descricao: str | None = None

#=======================Listar Medicamentos==========/================*/
@router.get("/medicamentos", response_model=list[MedicamentoResponse])
def listar_medicamentos(db: Session = Depends(get_db)):
    return service.listar_medicamentos(db)

#=======================Cadastrar Medicamento==========================*/   
@router.post("/medicamentos", response_model=MedicamentoResponse)
def cadastrar_medicamento(
    dados: MedicamentoCreate,
    db: Session = Depends(get_db),
):
    return service.cadastrar_medicamento(db, dados)

#=======================Atualizar Medicamento==========================*/
@router.put("/medicamentos/{id_medicamento}", response_model=MedicamentoResponse)
def atualizar_medicamento(
    id_medicamento: int,
    dados: MedicamentoCreate,
    db: Session = Depends(get_db),
):
    return service.atualizar_medicamento(db, id_medicamento, dados)


#=======================Excluir Medicamento==========================*/
@router.delete("/medicamentos/{id_medicamento}")
def excluir_medicamento(
    id_medicamento: int,
    db: Session = Depends(get_db),
):
    return service.excluir_medicamento(db, id_medicamento)


#=======================Listar Exames==========================*/ 
@router.get("/exames", response_model=list[ExameResponse])
def listar_exames(db: Session = Depends(get_db)):
    return service.listar_exames(db)


 #=======================Cadastrar Exame==========================*/
@router.post("/exames", response_model=ExameResponse)
def cadastrar_exame(
    dados: ExameCreate,
    db: Session = Depends(get_db),
):
    return service.cadastrar_exame(db, dados)


#=======================Atualizar Exame==========================*/
@router.put("/exames/{id_exame}", response_model=ExameResponse)
def atualizar_exame(
    id_exame: int,
    dados: ExameCreate,
    db: Session = Depends(get_db),
):
    return service.atualizar_exame(db, id_exame, dados)

#=======================Excluir Exame==========================
@router.delete("/exames/{id_exame}")
def excluir_exame(
    id_exame: int,
    db: Session = Depends(get_db),
):
    return service.excluir_exame(db, id_exame)

#=======================Lista Prescrições==========================*/


@router.get("/prescricoes/{id_prescricao}", response_model=PrescricaoResponse)
def buscar_prescricao(
    id_prescricao: int,
    db: Session = Depends(get_db),
):
    return service.buscar_prescricao(db, id_prescricao)



#======================Listar Prescrição==========================*/
@router.get("/prescricoes/{id_prescricao}", response_model=PrescricaoResponse)
def buscar_prescricao(
    id_prescricao: int,
    db: Session = Depends(get_db),
):
    registro = db.query(Prescricao).filter(
        Prescricao.id_prescricao == id_prescricao
    ).first()

    if registro is None:
        raise HTTPException(status_code=404, detail="Prescrição não encontrada")

    return registro

#=======================Cadastrar Prescrição==========================*/
@router.post("/prescricoes", response_model=PrescricaoResponse)
def cadastrar_prescricao(
    dados: PrescricaoCreate,
    db: Session = Depends(get_db),
):
    return service.cadastrar_prescricao(db, dados)

#=======================Atualizar Prescrição==========================*/
@router.put("/prescricoes/{id_prescricao}", response_model=PrescricaoResponse)
def atualizar_prescricao(
    id_prescricao: int,
    dados: PrescricaoCreate,
    db: Session = Depends(get_db),
):
    return service.atualizar_prescricao(db, id_prescricao, dados)

#=======================Excluir Prescrição==========================*/
@router.delete("/prescricoes/{id_prescricao}")
def excluir_prescricao(
    id_prescricao: int,
    db: Session = Depends(get_db),
):
    return service.excluir_prescricao(db, id_prescricao)

#=======================Listar Prescrição Medicamento==========================*/

# =========================
# PRESCRIÇÃO DE MEDICAMENTOS
# =========================

@router.get(
    "/prescricao-medicamentos",
    response_model=List[PrescricaoMedicamentoResponse],
)
def listar_prescricao_medicamentos(
    db: Session = Depends(get_db),
):
    return service.listar_prescricao_medicamentos(db)


@router.get(
    "/prescricao-medicamentos/{id_prescricao_medicamento}",
    response_model=PrescricaoMedicamentoResponse,
)
def buscar_prescricao_medicamento(
    id_prescricao_medicamento: int,
    db: Session = Depends(get_db),
):
    return service.buscar_prescricao_medicamento(
        db, id_prescricao_medicamento
    )


@router.post(
    "/prescricao-medicamentos",
    response_model=PrescricaoMedicamentoResponse,
)
def cadastrar_prescricao_medicamento(
    dados: PrescricaoMedicamentoCreate,
    db: Session = Depends(get_db),
):
    return service.cadastrar_prescricao_medicamento(db, dados)


@router.put(
    "/prescricao-medicamentos/{id_prescricao_medicamento}",
    response_model=PrescricaoMedicamentoResponse,
)
def atualizar_prescricao_medicamento(
    id_prescricao_medicamento: int,
    dados: PrescricaoMedicamentoCreate,
    db: Session = Depends(get_db),
):
    return service.atualizar_prescricao_medicamento(
        db, id_prescricao_medicamento, dados
    )


@router.delete(
    "/prescricao-medicamentos/{id_prescricao_medicamento}",
)
def excluir_prescricao_medicamento(
    id_prescricao_medicamento: int,
    db: Session = Depends(get_db),
):
    return service.excluir_prescricao_medicamento(
        db, id_prescricao_medicamento
    )


   

# =========================
# PEDIDOS DE EXAMES
# =========================

@router.get(
    "/pedidos-exames",
    response_model=List[PedidoExameResponse],
)
def listar_pedidos_exames(
    db: Session = Depends(get_db),
):
    return service.listar_pedidos_exames(db)


@router.get(
    "/pedidos-exames/{id_pedido_exame}",
    response_model=PedidoExameResponse,
)
def buscar_pedido_exame(
    id_pedido_exame: int,
    db: Session = Depends(get_db),
):
    return service.buscar_pedido_exame(db, id_pedido_exame)


@router.post(
    "/pedidos-exames",
    response_model=PedidoExameResponse,
)
def cadastrar_pedido_exame(
    dados: PedidoExameCreate,
    db: Session = Depends(get_db),
):
    return service.cadastrar_pedido_exame(db, dados)


@router.put(
    "/pedidos-exames/{id_pedido_exame}",
    response_model=PedidoExameResponse,
)
def atualizar_pedido_exame(
    id_pedido_exame: int,
    dados: PedidoExameCreate,
    db: Session = Depends(get_db),
):
    return service.atualizar_pedido_exame(
        db, id_pedido_exame, dados
    )


@router.delete("/pedidos-exames/{id_pedido_exame}")
def excluir_pedido_exame(
    id_pedido_exame: int,
    db: Session = Depends(get_db),
):
    return service.excluir_pedido_exame(db, id_pedido_exame)



# =========================
# ITENS DOS PEDIDOS DE EXAMES
# =========================

@router.get(
    "/pedidos-exames-itens",
    response_model=List[PedidoExameItemResponse],
)
def listar_pedido_exame_itens(
    db: Session = Depends(get_db),
):
    return service.listar_pedido_exame_itens(db)


@router.get(
    "/pedidos-exames-itens/{id_pedido_exame_item}",
    response_model=PedidoExameItemResponse,
)
def buscar_pedido_exame_item(
    id_pedido_exame_item: int,
    db: Session = Depends(get_db),
):
    return service.buscar_pedido_exame_item(
        db, id_pedido_exame_item
    )


@router.post(
    "/pedidos-exames-itens",
    response_model=PedidoExameItemResponse,
)
def cadastrar_pedido_exame_item(
    dados: PedidoExameItemCreate,
    db: Session = Depends(get_db),
):
    return service.cadastrar_pedido_exame_item(db, dados)


@router.put(
    "/pedidos-exames-itens/{id_pedido_exame_item}",
    response_model=PedidoExameItemResponse,
)
def atualizar_pedido_exame_item(
    id_pedido_exame_item: int,
    dados: PedidoExameItemCreate,
    db: Session = Depends(get_db),
):
    return service.atualizar_pedido_exame_item(
        db, id_pedido_exame_item, dados
    )


@router.delete(
    "/pedidos-exames-itens/{id_pedido_exame_item}"
)
def excluir_pedido_exame_item(
    id_pedido_exame_item: int,
    db: Session = Depends(get_db),
):
    return service.excluir_pedido_exame_item(
        db, id_pedido_exame_item
    )

