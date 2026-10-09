"""
Rotas do módulo Pacientes.
Cobre 4 recursos: convênios, pacientes, contatos e prontuário.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.pacientes import schemas
from app.modules.pacientes.service import (
    ConvenioService,
    PacienteService,
    ContatoPacienteService,
    ProntuarioService,
)

router = APIRouter()


# ======================= CONVÊNIOS =======================
@router.post("/convenios", response_model=schemas.ConvenioOut, tags=["Convênios"])
def criar_convenio(dados: schemas.ConvenioCreate, db: Session = Depends(get_db)):
    return ConvenioService(db).criar(dados.model_dump())


@router.get("/convenios", response_model=List[schemas.ConvenioOut], tags=["Convênios"])
def listar_convenios(db: Session = Depends(get_db)):
    return ConvenioService(db).listar()


# ======================= PACIENTES =======================
@router.post("/pacientes", response_model=schemas.PacienteOut, tags=["Pacientes"])
def criar_paciente(dados: schemas.PacienteCreate, db: Session = Depends(get_db)):
    return PacienteService(db).criar(dados.model_dump())


@router.get("/pacientes", response_model=List[schemas.PacienteOut], tags=["Pacientes"])
def listar_pacientes(
    nome: Optional[str] = None,
    cpf: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Sem filtro, lista todos. Com ?nome=... ou ?cpf=..., busca (usado pela tela de busca)."""
    service = PacienteService(db)
    if nome or cpf:
        return service.buscar(nome=nome, cpf=cpf)
    return service.listar()


@router.get("/pacientes/{id_paciente}", response_model=schemas.PacienteOut, tags=["Pacientes"])
def obter_paciente(id_paciente: int, db: Session = Depends(get_db)):
    paciente = PacienteService(db).obter(id_paciente, "id_paciente")
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return paciente


@router.put("/pacientes/{id_paciente}", response_model=schemas.PacienteOut, tags=["Pacientes"])
def atualizar_paciente(id_paciente: int, dados: schemas.PacienteUpdate, db: Session = Depends(get_db)):
    service = PacienteService(db)
    paciente = service.obter(id_paciente, "id_paciente")
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return service.atualizar(paciente, dados.model_dump(exclude_unset=True))


@router.delete("/pacientes/{id_paciente}", tags=["Pacientes"])
def excluir_paciente(id_paciente: int, db: Session = Depends(get_db), usuario: dict = Depends(get_current_user)):
    service = PacienteService(db)
    paciente = service.obter(id_paciente, "id_paciente")
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    service.excluir(paciente)
    return {"mensagem": "Paciente excluído com sucesso"}


# ======================= CONTATOS =======================
@router.post("/contatos", response_model=schemas.ContatoPacienteOut, tags=["Contatos"])
def criar_contato(dados: schemas.ContatoPacienteCreate, db: Session = Depends(get_db)):
    return ContatoPacienteService(db).criar(dados.model_dump())


@router.get(
    "/pacientes/{id_paciente}/contatos",
    response_model=List[schemas.ContatoPacienteOut],
    tags=["Contatos"],
)
def listar_contatos_do_paciente(id_paciente: int, db: Session = Depends(get_db)):
    return ContatoPacienteService(db).listar_por_paciente(id_paciente)


# ======================= PRONTUÁRIO =======================
@router.post("/prontuarios", response_model=schemas.ProntuarioOut, tags=["Prontuário"])
def criar_prontuario(dados: schemas.ProntuarioCreate, db: Session = Depends(get_db)):
    return ProntuarioService(db).criar(dados.model_dump())


@router.get(
    "/pacientes/{id_paciente}/prontuario",
    response_model=schemas.ProntuarioOut,
    tags=["Prontuário"],
)
def obter_prontuario_do_paciente(id_paciente: int, db: Session = Depends(get_db)):
    prontuario = ProntuarioService(db).obter_por_paciente(id_paciente)
    if not prontuario:
        raise HTTPException(status_code=404, detail="Esse paciente ainda não tem prontuário")
    return prontuario
