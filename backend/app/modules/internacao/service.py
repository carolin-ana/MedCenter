
"""
Serviços do módulo Internação e Enfermagem.
Reaproveitam o CRUD da classe BaseService.
"""

from app.core.base_service import BaseService

from app.modules.internacao.models import (
    Internacao,
    Enfermeiro,
    AtendimentoEnfermeiro,
    Quarto,
    InternacaoQuarto,
)


class InternacaoService(BaseService[Internacao]):
    model = Internacao


class EnfermeiroService(BaseService[Enfermeiro]):
    model = Enfermeiro


class AtendimentoEnfermeiroService(BaseService[AtendimentoEnfermeiro]):
    model = AtendimentoEnfermeiro


class QuartoService(BaseService[Quarto]):
    model = Quarto


class InternacaoQuartoService(BaseService[InternacaoQuarto]):
    model = InternacaoQuarto
