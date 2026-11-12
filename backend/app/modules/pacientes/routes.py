"""
Rotas do módulo Pacientes.
Cobre 4 recursos: convênios, pacientes, contatos e prontuário.
Todas as rotas exigem login (token JWT), definido uma vez só no router.
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

router = APIRouter(dependencies=[Depends(get_current_user)])


# ---------- funções auxiliares ----------
def _obter_ou_404(service, valor, campo: str, mensagem: str):
    objeto = service.obter(valor, campo)
    if not objeto:
        raise HTTPException(status_code=404, detail=mensagem)
    return objeto


def _executar(acao):
    """Roda uma ação do serviço; regra de negócio violada (ValueError) vira erro 400."""
    try:
        return acao()
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))


def _excluir(service, objeto, mensagem_ok: str):
    """Exclusão: se houver vínculos, o serviço avisa e a API responde 409."""
    try:
        service.excluir(objeto)
    except ValueError as erro:
        raise HTTPException(status_code=409, detail=str(erro))
    return {"mensagem": mensagem_ok}


# ======================= CONVÊNIOS =======================
@router.post("/convenios", response_model=schemas.ConvenioOut, tags=["Convênios"])
def criar_convenio(dados: schemas.ConvenioCreate, db: Session = Depends(get_db)):
    return _executar(lambda: ConvenioService(db).criar(dados.model_dump()))


@router.get("/convenios", response_model=List[schemas.ConvenioOut], tags=["Convênios"])
def listar_convenios(db: Session = Depends(get_db)):
    return ConvenioService(db).listar()


@router.get("/convenios/{id_convenio}", response_model=schemas.ConvenioOut, tags=["Convênios"])
def obter_convenio(id_convenio: int, db: Session = Depends(get_db)):
    return _obter_ou_404(ConvenioService(db), id_convenio, "id_convenio", "Convênio não encontrado")


@router.put("/convenios/{id_convenio}", response_model=schemas.ConvenioOut, tags=["Convênios"])
def atualizar_convenio(id_convenio: int, dados: schemas.ConvenioUpdate, db: Session = Depends(get_db)):
    service = ConvenioService(db)
    convenio = _obter_ou_404(service, id_convenio, "id_convenio", "Convênio não encontrado")
    return _executar(lambda: service.atualizar(convenio, dados.model_dump(exclude_unset=True)))


@router.delete("/convenios/{id_convenio}", tags=["Convênios"])
def excluir_convenio(id_convenio: int, db: Session = Depends(get_db)):
    service = ConvenioService(db)
    convenio = _obter_ou_404(service, id_convenio, "id_convenio", "Convênio não encontrado")
    return _excluir(service, convenio, "Convênio excluído com sucesso")


# ======================= PACIENTES =======================
@router.post("/pacientes", response_model=schemas.PacienteOut, tags=["Pacientes"])
def criar_paciente(dados: schemas.PacienteCreate, db: Session = Depends(get_db)):
    return _executar(lambda: PacienteService(db).criar(dados.model_dump()))


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
    return _obter_ou_404(PacienteService(db), id_paciente, "id_paciente", "Paciente não encontrado")


@router.put("/pacientes/{id_paciente}", response_model=schemas.PacienteOut, tags=["Pacientes"])
def atualizar_paciente(id_paciente: int, dados: schemas.PacienteUpdate, db: Session = Depends(get_db)):
    service = PacienteService(db)
    paciente = _obter_ou_404(service, id_paciente, "id_paciente", "Paciente não encontrado")
    return _executar(lambda: service.atualizar(paciente, dados.model_dump(exclude_unset=True)))


@router.delete("/pacientes/{id_paciente}", tags=["Pacientes"])
def excluir_paciente(id_paciente: int, db: Session = Depends(get_db)):
    service = PacienteService(db)
    paciente = _obter_ou_404(service, id_paciente, "id_paciente", "Paciente não encontrado")
    return _excluir(service, paciente, "Paciente excluído com sucesso")


# ======================= CONTATOS =======================
@router.post("/contatos", response_model=schemas.ContatoPacienteOut, tags=["Contatos"])
def criar_contato(dados: schemas.ContatoPacienteCreate, db: Session = Depends(get_db)):
    return _executar(lambda: ContatoPacienteService(db).criar(dados.model_dump()))


@router.get(
    "/pacientes/{id_paciente}/contatos",
    response_model=List[schemas.ContatoPacienteOut],
    tags=["Contatos"],
)
def listar_contatos_do_paciente(id_paciente: int, db: Session = Depends(get_db)):
    return ContatoPacienteService(db).listar_por_paciente(id_paciente)


@router.put("/contatos/{id_contato}", response_model=schemas.ContatoPacienteOut, tags=["Contatos"])
def atualizar_contato(id_contato: int, dados: schemas.ContatoPacienteUpdate, db: Session = Depends(get_db)):
    service = ContatoPacienteService(db)
    contato = _obter_ou_404(service, id_contato, "id_contato", "Contato não encontrado")
    return _executar(lambda: service.atualizar(contato, dados.model_dump(exclude_unset=True)))


@router.delete("/contatos/{id_contato}", tags=["Contatos"])
def excluir_contato(id_contato: int, db: Session = Depends(get_db)):
    service = ContatoPacienteService(db)
    contato = _obter_ou_404(service, id_contato, "id_contato", "Contato não encontrado")
    return _excluir(service, contato, "Contato excluído com sucesso")


# ======================= PRONTUÁRIO =======================
@router.post("/prontuarios", response_model=schemas.ProntuarioOut, tags=["Prontuário"])
def criar_prontuario(dados: schemas.ProntuarioCreate, db: Session = Depends(get_db)):
    return _executar(lambda: ProntuarioService(db).criar(dados.model_dump()))


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


@router.put("/prontuarios/{id_prontuario}", response_model=schemas.ProntuarioOut, tags=["Prontuário"])
def atualizar_prontuario(id_prontuario: int, dados: schemas.ProntuarioUpdate, db: Session = Depends(get_db)):
    service = ProntuarioService(db)
    prontuario = _obter_ou_404(service, id_prontuario, "id_prontuario", "Prontuário não encontrado")
    return _executar(lambda: service.atualizar(prontuario, dados.model_dump(exclude_unset=True)))
