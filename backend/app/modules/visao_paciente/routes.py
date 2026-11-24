"""
Rotas do módulo Visão do Paciente (linha do tempo e alertas).
Acesso: administrador, médico e enfermagem (dado clínico; a recepção não vê).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissoes import exigir_acesso
from app.modules.visao_paciente.service import AlertasService, VisaoPacienteService

router = APIRouter(dependencies=[Depends(exigir_acesso("visao"))])


@router.get("/pacientes/{id_paciente}/linha-do-tempo")
def linha_do_tempo(id_paciente: int, db: Session = Depends(get_db)):
    """Tudo o que aconteceu com o paciente, em ordem de data, numa só resposta."""
    visao = VisaoPacienteService(db).montar(id_paciente)
    if visao is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return visao


@router.get("/alertas")
def alertas(limite_estoque: int = Query(70, ge=0), db: Session = Depends(get_db)):
    """Painel de atenção: leitos, estoque baixo, exames sem resultado e cobranças pendentes."""
    return AlertasService(db).montar(limite_estoque)
