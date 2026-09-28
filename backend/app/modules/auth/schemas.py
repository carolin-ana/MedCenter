"""
Schemas Pydantic: definem o formato dos dados que entram e saem da API.
"""

from pydantic import BaseModel


class UsuarioCreate(BaseModel):
    """Dados esperados para criar um usuário (rota /auth/registrar)."""
    nome: str
    email: str
    senha: str
    perfil: str  # admin, medico, enfermeira, recepcao


class UsuarioOut(BaseModel):
    """Dados devolvidos pela API sobre um usuário (nunca inclui a senha)."""
    id_usuario: int
    nome: str
    email: str
    perfil: str

    class Config:
        from_attributes = True  # permite converter direto do model do SQLAlchemy


class TokenResponse(BaseModel):
    """Resposta da rota de login."""
    access_token: str
    token_type: str
