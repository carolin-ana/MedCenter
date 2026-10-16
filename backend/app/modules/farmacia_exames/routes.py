from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.farmacia_exames.models import Medicamento, Exame

router = APIRouter()

from pydantic import BaseModel

class MedicamentoEntrada(BaseModel):
    nome: str
    descricao: str | None = None
    quantidade_estoque: int = 0

class ExameEntrada(BaseModel):
    nome: str
    descricao: str | None = None

 
@router.get("/medicamentos")
def listar_medicamentos(db: Session = Depends(get_db)):
    return db.query(Medicamento).all()

     
@router.post("/medicamentos")
def cadastrar_medicamento(
    dados: MedicamentoEntrada,
    db: Session = Depends(get_db)
):
    novo_medicamento = Medicamento(
        nome=dados.nome,
        descricao=dados.descricao,
        quantidade_estoque=dados.quantidade_estoque
    )

    db.add(novo_medicamento)
    db.commit()
    db.refresh(novo_medicamento)

    return novo_medicamento


 
@router.put("/medicamentos/{id_medicamento}")
def atualizar_medicamento(
    id_medicamento: int,
    dados: MedicamentoEntrada,
    db: Session = Depends(get_db)
):
    medicamento = db.query(Medicamento).filter(
        Medicamento.id_medicamento == id_medicamento
    ).first()

    if medicamento is None:
        return {"erro": "Medicamento não encontrado"}

    medicamento.nome = dados.nome
    medicamento.descricao = dados.descricao
    medicamento.quantidade_estoque = dados.quantidade_estoque

    db.commit()
    db.refresh(medicamento)

    return medicamento


 
@router.delete("/medicamentos/{id_medicamento}")
def excluir_medicamento(
    id_medicamento: int,
    db: Session = Depends(get_db)
):
    medicamento = db.query(Medicamento).filter(
        Medicamento.id_medicamento == id_medicamento
    ).first()

    if medicamento is None:
        return {"erro": "Medicamento não encontrado"}

    db.delete(medicamento)
    db.commit()

    return {"mensagem": "Medicamento excluído com sucesso"}


 
@router.get("/exames")
def listar_exames(db: Session = Depends(get_db)):
    return db.query(Exame).all()


 
@router.post("/exames")
def cadastrar_exame(
    dados: ExameEntrada,
    db: Session = Depends(get_db)
):
    novo_exame = Exame(
        nome=dados.nome,
        descricao=dados.descricao
    )

    db.add(novo_exame)
    db.commit()
    db.refresh(novo_exame)

    return novo_exame

@router.put("/exames/{id_exame}")
def atualizar_exame(
    id_exame:int,
    dados: ExameEntrada,
    db:Session = Depends(get_db)
):
    exame = db.query(Exame).filter(
        Exame.id_exame == id_exame).first()
    if exame is None:
        return {"erro": "Exame não encontrado"}

    exame.nome = dados.nome
    exame.descricao = dados.descricao

    db.commit()
    db.refresh(exame)

    return exame


@router.delete("/exames/{id_exame}")
def excluir_exame(
    id_exame: int,
    db: Session = Depends(get_db)
):
    exame = db.query(Exame).filter(
        Exame.id_exame == id_exame
    ).first()

    if exame is None:
        return {"erro": "Exame não encontrado"}

    db.delete(exame)
    db.commit()

    return {"mensagem": "Exame excluído com sucesso"}
 

