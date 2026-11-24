"""
Controle de acesso por perfil.

Perfis do sistema: admin, recepcao, medico e enfermagem.
O perfil vem dentro do token JWT (campo "perfil"), gravado no login.

Cada módulo tem uma regra por perfil:
  "total"            -> pode ler e alterar
  "leitura"          -> só pode consultar (GET)
  ("/consultas",)    -> consulta tudo, mas só altera os caminhos que COMEÇAM com os listados
  ausente            -> sem acesso (erro 403)

Uso em um router (uma linha por módulo):
    router = APIRouter(dependencies=[Depends(exigir_acesso("pacientes"))])

IMPORTANTE: manter igual à tabela NIVEIS do frontend (services/layout.js).
"""

import unicodedata

from fastapi import Depends, HTTPException, Request, status

from app.core.security import get_current_user

METODOS_DE_LEITURA = {"GET", "HEAD", "OPTIONS"}

REGRAS = {
    # ----- Pacientes: recepção cadastra pacientes; médico atualiza o prontuário; convênios só o admin -----
    "pacientes": {
        "admin": "total",
        "recepcao": ("/pacientes", "/contatos", "/prontuarios"),
        "medico": ("/prontuarios",),
        "enfermagem": "leitura",
    },
    # ----- Agenda: médicos e especialidades só o admin; recepção marca consultas; médico atende -----
    "agenda": {
        "admin": "total",
        "recepcao": ("/consultas",),
        "medico": ("/consultas", "/atendimentos"),
        "enfermagem": "leitura",
    },
    # ----- Farmácia e exames: médico prescreve e pede exames; estoque e catálogo só o admin -----
    "farmacia": {
        "admin": "total",
        "medico": ("/prescricoes", "/prescricao-medicamentos", "/pedidos-exames"),
        "enfermagem": "leitura",
    },
    # ----- Internação: médico interna e dá alta; enfermagem registra cuidados e aloca quartos -----
    "internacao": {
        "admin": "total",
        "medico": ("/internacao/internacoes", "/internacao/internacao-quartos"),
        "enfermagem": ("/internacao/atendimentos", "/internacao/internacao-quartos"),
    },
    # ----- Visão do paciente: só consulta; dado clínico, então a recepção não vê -----
    "visao": {"admin": "total", "medico": "total", "enfermagem": "total"},
    # ----- Financeiro: recepção só consulta -----
    "financeiro": {"admin": "total", "recepcao": "leitura"},
    # ----- Criar contas de usuário -----
    "usuarios": {"admin": "total"},
}


def normalizar_perfil(perfil) -> str:
    """Aceita variações ('Médico', 'enfermeira', 'recepção') e devolve o nome padrão."""
    texto = unicodedata.normalize("NFKD", str(perfil or "")).encode("ascii", "ignore").decode().lower().strip()
    if texto.startswith("enferm"):
        return "enfermagem"
    if texto.startswith("recep"):
        return "recepcao"
    if texto.startswith("medic"):
        return "medico"
    if texto.startswith("admin"):
        return "admin"
    return texto


def _negar(mensagem: str):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=mensagem)


def exigir_acesso(modulo: str):
    """Cria a dependência que confere o perfil do usuário para o módulo informado."""
    regras_do_modulo = REGRAS[modulo]

    def verificar(request: Request, payload: dict = Depends(get_current_user)) -> dict:
        perfil = normalizar_perfil(payload.get("perfil"))
        regra = regras_do_modulo.get(perfil)

        if regra is None:
            _negar(f"O perfil '{perfil}' não tem acesso a esta área")
        if regra == "total" or request.method in METODOS_DE_LEITURA:
            return payload
        if regra == "leitura":
            _negar(f"O perfil '{perfil}' só pode consultar esta área")

        # regra com lista de caminhos: altera apenas o que estiver na lista
        caminho = request.url.path
        if any(caminho.startswith(prefixo) for prefixo in regra):
            return payload
        _negar(f"O perfil '{perfil}' só pode consultar esta área")

    return verificar
