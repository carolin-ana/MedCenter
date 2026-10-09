"""
Rotas do módulo Financeiro.
Agora as rotas só "conversam" com a classe FaturamentoService — elas não
sabem mais como os dados são salvos no banco, só pedem pro serviço fazer
(isso também é um reflexo do encapsulamento da camada de serviço).
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.financeiro import schemas
from app.modules.financeiro.service import FaturamentoService

router = APIRouter()


@router.post("/", response_model=schemas.FaturamentoOut)
def criar_faturamento(
    dados: schemas.FaturamentoCreate,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    service = FaturamentoService(db)
    try:
        return service.criar(dados.model_dump())
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))


@router.get("/", response_model=List[schemas.FaturamentoOut])
def listar_faturamentos(db: Session = Depends(get_db), usuario: dict = Depends(get_current_user)):
    return FaturamentoService(db).listar()


@router.get("/{id_faturamento}", response_model=schemas.FaturamentoOut)
def obter_faturamento(
    id_faturamento: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    faturamento = FaturamentoService(db).obter(id_faturamento, "id_faturamento")
    if not faturamento:
        raise HTTPException(status_code=404, detail="Faturamento não encontrado")
    return faturamento


@router.put("/{id_faturamento}", response_model=schemas.FaturamentoOut)
def atualizar_faturamento(
    id_faturamento: int,
    dados: schemas.FaturamentoUpdate,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    service = FaturamentoService(db)
    faturamento = service.obter(id_faturamento, "id_faturamento")
    if not faturamento:
        raise HTTPException(status_code=404, detail="Faturamento não encontrado")
    return service.atualizar(faturamento, dados.model_dump(exclude_unset=True))


@router.delete("/{id_faturamento}")
def excluir_faturamento(
    id_faturamento: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    service = FaturamentoService(db)
    faturamento = service.obter(id_faturamento, "id_faturamento")
    if not faturamento:
        raise HTTPException(status_code=404, detail="Faturamento não encontrado")
    service.excluir(faturamento)
    return {"mensagem": "Faturamento excluído com sucesso"}
