
"""
Rotas da API de Internação e Enfermagem.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.internacao import schemas
from app.modules.internacao.service import (
    InternacaoService,
    EnfermeiroService,
    AtendimentoEnfermeiroService,
    QuartoService,
    InternacaoQuartoService,
)

router = APIRouter()


# ==================================================
# INTERNAÇÕES
# ==================================================

@router.post("/internacoes", response_model=schemas.InternacaoOut)
def criar_internacao(
    dados: schemas.InternacaoCreate,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    return InternacaoService(db).criar(dados.model_dump())


@router.get("/internacoes", response_model=List[schemas.InternacaoOut])
def listar_internacoes(
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    return InternacaoService(db).listar()


@router.get("/internacoes/{id_internacao}", response_model=schemas.InternacaoOut)
def obter_internacao(
    id_internacao: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    registro = InternacaoService(db).obter(id_internacao, "id_internacao")
    if not registro:
        raise HTTPException(status_code=404, detail="Internação não encontrada")
    return registro


@router.put("/internacoes/{id_internacao}", response_model=schemas.InternacaoOut)
def atualizar_internacao(
    id_internacao: int,
    dados: schemas.InternacaoUpdate,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    service = InternacaoService(db)
    registro = service.obter(id_internacao, "id_internacao")
    if not registro:
        raise HTTPException(status_code=404, detail="Internação não encontrada")
    return service.atualizar(registro, dados.model_dump(exclude_unset=True))


@router.delete("/internacoes/{id_internacao}")
def excluir_internacao(
    id_internacao: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    service = InternacaoService(db)
    registro = service.obter(id_internacao, "id_internacao")
    if not registro:
        raise HTTPException(status_code=404, detail="Internação não encontrada")
    service.excluir(registro)
    return {"mensagem": "Internação excluída com sucesso"}


# ==================================================
# ENFERMEIROS
# ==================================================

@router.post("/enfermeiros", response_model=schemas.EnfermeiroOut)
def criar_enfermeiro(
    dados: schemas.EnfermeiroCreate,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    return EnfermeiroService(db).criar(dados.model_dump())


@router.get("/enfermeiros", response_model=List[schemas.EnfermeiroOut])
def listar_enfermeiros(
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    return EnfermeiroService(db).listar()


@router.get("/enfermeiros/{id_enfermeiro}", response_model=schemas.EnfermeiroOut)
def obter_enfermeiro(
    id_enfermeiro: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    registro = EnfermeiroService(db).obter(id_enfermeiro, "id_enfermeiro")
    if not registro:
        raise HTTPException(status_code=404, detail="Enfermeiro não encontrado")
    return registro


@router.put("/enfermeiros/{id_enfermeiro}", response_model=schemas.EnfermeiroOut)
def atualizar_enfermeiro(
    id_enfermeiro: int,
    dados: schemas.EnfermeiroUpdate,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    service = EnfermeiroService(db)
    registro = service.obter(id_enfermeiro, "id_enfermeiro")
    if not registro:
        raise HTTPException(status_code=404, detail="Enfermeiro não encontrado")
    return service.atualizar(registro, dados.model_dump(exclude_unset=True))


@router.delete("/enfermeiros/{id_enfermeiro}")
def excluir_enfermeiro(
    id_enfermeiro: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    service = EnfermeiroService(db)
    registro = service.obter(id_enfermeiro, "id_enfermeiro")
    if not registro:
        raise HTTPException(status_code=404, detail="Enfermeiro não encontrado")
    service.excluir(registro)
    return {"mensagem": "Enfermeiro excluído com sucesso"}


# ==================================================
# ATENDIMENTOS DE ENFERMAGEM
# ==================================================

@router.post("/atendimentos", response_model=schemas.AtendimentoEnfermeiroOut)
def criar_atendimento(
    dados: schemas.AtendimentoEnfermeiroCreate,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    return AtendimentoEnfermeiroService(db).criar(dados.model_dump())


@router.get("/atendimentos", response_model=List[schemas.AtendimentoEnfermeiroOut])
def listar_atendimentos(
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    return AtendimentoEnfermeiroService(db).listar()


@router.get("/atendimentos/{id_atendimento}", response_model=schemas.AtendimentoEnfermeiroOut)
def obter_atendimento(
    id_atendimento: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    registro = AtendimentoEnfermeiroService(db).obter(
        id_atendimento, "id_atendimento_enfermeiro"
    )
    if not registro:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado")
    return registro


@router.put("/atendimentos/{id_atendimento}", response_model=schemas.AtendimentoEnfermeiroOut)
def atualizar_atendimento(
    id_atendimento: int,
    dados: schemas.AtendimentoEnfermeiroUpdate,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    service = AtendimentoEnfermeiroService(db)
    registro = service.obter(id_atendimento, "id_atendimento_enfermeiro")
    if not registro:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado")
    return service.atualizar(registro, dados.model_dump(exclude_unset=True))


@router.delete("/atendimentos/{id_atendimento}")
def excluir_atendimento(
    id_atendimento: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    service = AtendimentoEnfermeiroService(db)
    registro = service.obter(id_atendimento, "id_atendimento_enfermeiro")
    if not registro:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado")
    service.excluir(registro)
    return {"mensagem": "Atendimento excluído com sucesso"}


# ==================================================
# QUARTOS
# ==================================================

@router.post("/quartos", response_model=schemas.QuartoOut)
def criar_quarto(
    dados: schemas.QuartoCreate,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    return QuartoService(db).criar(dados.model_dump())


@router.get("/quartos", response_model=List[schemas.QuartoOut])
def listar_quartos(
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    return QuartoService(db).listar()


@router.get("/quartos/{id_quarto}", response_model=schemas.QuartoOut)
def obter_quarto(
    id_quarto: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    registro = QuartoService(db).obter(id_quarto, "id_quarto")
    if not registro:
        raise HTTPException(status_code=404, detail="Quarto não encontrado")
    return registro


@router.put("/quartos/{id_quarto}", response_model=schemas.QuartoOut)
def atualizar_quarto(
    id_quarto: int,
    dados: schemas.QuartoUpdate,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    service = QuartoService(db)
    registro = service.obter(id_quarto, "id_quarto")
    if not registro:
        raise HTTPException(status_code=404, detail="Quarto não encontrado")
    return service.atualizar(registro, dados.model_dump(exclude_unset=True))


@router.delete("/quartos/{id_quarto}")
def excluir_quarto(
    id_quarto: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    service = QuartoService(db)
    registro = service.obter(id_quarto, "id_quarto")
    if not registro:
        raise HTTPException(status_code=404, detail="Quarto não encontrado")
    service.excluir(registro)
    return {"mensagem": "Quarto excluído com sucesso"}


# ==================================================
# VÍNCULO ENTRE INTERNAÇÃO E QUARTO
# ==================================================

@router.post("/internacao-quartos", response_model=schemas.InternacaoQuartoOut)
def criar_vinculo_quarto(
    dados: schemas.InternacaoQuartoCreate,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    return InternacaoQuartoService(db).criar(dados.model_dump())


@router.get("/internacao-quartos", response_model=List[schemas.InternacaoQuartoOut])
def listar_vinculos_quarto(
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    return InternacaoQuartoService(db).listar()


@router.get("/internacao-quartos/{id_vinculo}", response_model=schemas.InternacaoQuartoOut)
def obter_vinculo_quarto(
    id_vinculo: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    registro = InternacaoQuartoService(db).obter(
        id_vinculo, "id_internacao_quarto"
    )
    if not registro:
        raise HTTPException(status_code=404, detail="Vínculo não encontrado")
    return registro


@router.put("/internacao-quartos/{id_vinculo}", response_model=schemas.InternacaoQuartoOut)
def atualizar_vinculo_quarto(
    id_vinculo: int,
    dados: schemas.InternacaoQuartoUpdate,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    service = InternacaoQuartoService(db)
    registro = service.obter(id_vinculo, "id_internacao_quarto")
    if not registro:
        raise HTTPException(status_code=404, detail="Vínculo não encontrado")
    return service.atualizar(registro, dados.model_dump(exclude_unset=True))


@router.delete("/internacao-quartos/{id_vinculo}")
def excluir_vinculo_quarto(
    id_vinculo: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_current_user),
):
    service = InternacaoQuartoService(db)
    registro = service.obter(id_vinculo, "id_internacao_quarto")
    if not registro:
        raise HTTPException(status_code=404, detail="Vínculo não encontrado")
    service.excluir(registro)
    return {"mensagem": "Vínculo excluído com sucesso"}
