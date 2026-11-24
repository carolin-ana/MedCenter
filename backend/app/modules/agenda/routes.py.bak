"""
Rotas do módulo Corpo Clínico & Agenda.
Todas as rotas exigem login (token JWT), definido uma vez só no router.
"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.agenda import schemas
from app.modules.agenda.service import (
    AtendimentoService,
    ConsultaService,
    EspecialidadeService,
    MedicoService,
)

router = APIRouter(dependencies=[Depends(get_current_user)])


# ---------- funções auxiliares ----------
def _obter_ou_404(service, valor, campo: str, mensagem: str):
    objeto = service.obter(valor, campo)
    if not objeto:
        raise HTTPException(status_code=404, detail=mensagem)
    return objeto


def _excluir(db: Session, service, objeto, mensagem_ok: str):
    """Exclui; se houver registros ligados a ele (ex: médico com consultas), avisa em vez de dar erro 500."""
    try:
        service.excluir(objeto)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Não é possível excluir: existem registros vinculados a este item",
        )
    return {"mensagem": mensagem_ok}


# ======================= ESPECIALIDADES =======================
@router.post("/especialidades", response_model=schemas.EspecialidadeOut, tags=["Especialidades"])
def criar_especialidade(dados: schemas.EspecialidadeCreate, db: Session = Depends(get_db)):
    return EspecialidadeService(db).criar(dados.model_dump())


@router.get("/especialidades", response_model=List[schemas.EspecialidadeOut], tags=["Especialidades"])
def listar_especialidades(db: Session = Depends(get_db)):
    return EspecialidadeService(db).listar()


@router.get("/especialidades/{id_especialidade}", response_model=schemas.EspecialidadeOut, tags=["Especialidades"])
def obter_especialidade(id_especialidade: int, db: Session = Depends(get_db)):
    return _obter_ou_404(EspecialidadeService(db), id_especialidade, "id_especialidade", "Especialidade não encontrada")


@router.put("/especialidades/{id_especialidade}", response_model=schemas.EspecialidadeOut, tags=["Especialidades"])
def atualizar_especialidade(id_especialidade: int, dados: schemas.EspecialidadeUpdate, db: Session = Depends(get_db)):
    service = EspecialidadeService(db)
    especialidade = _obter_ou_404(service, id_especialidade, "id_especialidade", "Especialidade não encontrada")
    return service.atualizar(especialidade, dados.model_dump(exclude_unset=True))


@router.delete("/especialidades/{id_especialidade}", tags=["Especialidades"])
def excluir_especialidade(id_especialidade: int, db: Session = Depends(get_db)):
    service = EspecialidadeService(db)
    especialidade = _obter_ou_404(service, id_especialidade, "id_especialidade", "Especialidade não encontrada")
    return _excluir(db, service, especialidade, "Especialidade excluída com sucesso")


# ======================= MÉDICOS =======================
@router.post("/medicos", response_model=schemas.MedicoOut, tags=["Médicos"])
def criar_medico(dados: schemas.MedicoCreate, db: Session = Depends(get_db)):
    try:
        return MedicoService(db).criar(dados.model_dump())
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))


@router.get("/medicos", response_model=List[schemas.MedicoOut], tags=["Médicos"])
def listar_medicos(nome: Optional[str] = None, db: Session = Depends(get_db)):
    """Sem filtro lista todos; com ?nome=... busca por parte do nome."""
    service = MedicoService(db)
    return service.buscar(nome) if nome else service.listar()


@router.get("/medicos/{id_medico}", response_model=schemas.MedicoOut, tags=["Médicos"])
def obter_medico(id_medico: int, db: Session = Depends(get_db)):
    return _obter_ou_404(MedicoService(db), id_medico, "id_medico", "Médico não encontrado")


@router.put("/medicos/{id_medico}", response_model=schemas.MedicoOut, tags=["Médicos"])
def atualizar_medico(id_medico: int, dados: schemas.MedicoUpdate, db: Session = Depends(get_db)):
    service = MedicoService(db)
    medico = _obter_ou_404(service, id_medico, "id_medico", "Médico não encontrado")
    try:
        return service.atualizar(medico, dados.model_dump(exclude_unset=True))
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe um médico com esse CRM")


@router.delete("/medicos/{id_medico}", tags=["Médicos"])
def excluir_medico(id_medico: int, db: Session = Depends(get_db)):
    service = MedicoService(db)
    medico = _obter_ou_404(service, id_medico, "id_medico", "Médico não encontrado")
    return _excluir(db, service, medico, "Médico excluído com sucesso")


# ----- especialidades de um médico (relação N:N) -----
@router.get("/medicos/{id_medico}/especialidades", response_model=List[schemas.EspecialidadeOut], tags=["Médicos"])
def listar_especialidades_do_medico(id_medico: int, db: Session = Depends(get_db)):
    service = MedicoService(db)
    _obter_ou_404(service, id_medico, "id_medico", "Médico não encontrado")
    return service.listar_especialidades(id_medico)


@router.post("/medicos/{id_medico}/especialidades", response_model=schemas.VinculoEspecialidadeOut, tags=["Médicos"])
def vincular_especialidade(id_medico: int, dados: schemas.VinculoEspecialidadeCreate, db: Session = Depends(get_db)):
    try:
        return MedicoService(db).vincular_especialidade(id_medico, dados.id_especialidade, dados.data_inicio)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))


@router.delete("/medicos/{id_medico}/especialidades/{id_especialidade}", tags=["Médicos"])
def desvincular_especialidade(id_medico: int, id_especialidade: int, db: Session = Depends(get_db)):
    if not MedicoService(db).desvincular_especialidade(id_medico, id_especialidade):
        raise HTTPException(status_code=404, detail="Esse médico não tem essa especialidade")
    return {"mensagem": "Especialidade removida do médico"}


# ======================= CONSULTAS =======================
@router.post("/consultas", response_model=schemas.ConsultaOut, tags=["Consultas"])
def criar_consulta(dados: schemas.ConsultaCreate, db: Session = Depends(get_db)):
    try:
        return ConsultaService(db).criar(dados.model_dump())
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))


@router.get("/consultas", response_model=List[schemas.ConsultaOut], tags=["Consultas"])
def listar_consultas(
    id_medico: Optional[int] = None,
    id_paciente: Optional[int] = None,
    data: Optional[date] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Tela de agenda: ?id_medico=1&data=2026-10-20&status=agendada (todos opcionais)."""
    return ConsultaService(db).buscar(id_medico, id_paciente, data, status)


@router.get("/consultas/{id_consulta}", response_model=schemas.ConsultaOut, tags=["Consultas"])
def obter_consulta(id_consulta: int, db: Session = Depends(get_db)):
    return _obter_ou_404(ConsultaService(db), id_consulta, "id_consulta", "Consulta não encontrada")


@router.put("/consultas/{id_consulta}", response_model=schemas.ConsultaOut, tags=["Consultas"])
def atualizar_consulta(id_consulta: int, dados: schemas.ConsultaUpdate, db: Session = Depends(get_db)):
    """Também serve para remarcar (data_consulta) ou cancelar (status = 'cancelada')."""
    service = ConsultaService(db)
    consulta = _obter_ou_404(service, id_consulta, "id_consulta", "Consulta não encontrada")
    try:
        return service.atualizar(consulta, dados.model_dump(exclude_unset=True))
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))


@router.delete("/consultas/{id_consulta}", tags=["Consultas"])
def excluir_consulta(id_consulta: int, db: Session = Depends(get_db)):
    service = ConsultaService(db)
    consulta = _obter_ou_404(service, id_consulta, "id_consulta", "Consulta não encontrada")
    return _excluir(db, service, consulta, "Consulta excluída com sucesso")


# ======================= ATENDIMENTOS =======================
@router.post("/atendimentos", response_model=schemas.AtendimentoOut, tags=["Atendimentos"])
def criar_atendimento(dados: schemas.AtendimentoCreate, db: Session = Depends(get_db)):
    try:
        return AtendimentoService(db).criar(dados.model_dump())
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))


@router.get("/atendimentos", response_model=List[schemas.AtendimentoOut], tags=["Atendimentos"])
def listar_atendimentos(db: Session = Depends(get_db)):
    return AtendimentoService(db).listar()


@router.get("/atendimentos/{id_atendimento}", response_model=schemas.AtendimentoOut, tags=["Atendimentos"])
def obter_atendimento(id_atendimento: int, db: Session = Depends(get_db)):
    return _obter_ou_404(AtendimentoService(db), id_atendimento, "id_atendimento", "Atendimento não encontrado")


@router.get("/consultas/{id_consulta}/atendimento", response_model=schemas.AtendimentoOut, tags=["Atendimentos"])
def obter_atendimento_da_consulta(id_consulta: int, db: Session = Depends(get_db)):
    atendimento = AtendimentoService(db).obter_por_consulta(id_consulta)
    if not atendimento:
        raise HTTPException(status_code=404, detail="Essa consulta ainda não tem atendimento registrado")
    return atendimento


@router.put("/atendimentos/{id_atendimento}", response_model=schemas.AtendimentoOut, tags=["Atendimentos"])
def atualizar_atendimento(id_atendimento: int, dados: schemas.AtendimentoUpdate, db: Session = Depends(get_db)):
    service = AtendimentoService(db)
    atendimento = _obter_ou_404(service, id_atendimento, "id_atendimento", "Atendimento não encontrado")
    return service.atualizar(atendimento, dados.model_dump(exclude_unset=True))
