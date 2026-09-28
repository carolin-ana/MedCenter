"""
Funções de segurança: hash de senha e geração/validação de token JWT.
Usado principalmente pelo módulo de auth, mas o get_current_user pode
ser importado por qualquer rota que precise exigir login.
"""

from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# --- Senhas ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_senha(senha: str) -> str:
    """Transforma a senha em texto puro em um hash seguro para salvar no banco."""
    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Confere se a senha digitada no login bate com o hash salvo no banco."""
    return pwd_context.verify(senha, senha_hash)


# --- Token JWT ---
def criar_token(dados: dict) -> str:
    """Gera um token JWT contendo os dados informados (ex: id e perfil do usuário)."""
    dados_para_codificar = dados.copy()
    expira_em = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    dados_para_codificar.update({"exp": expira_em})
    return jwt.encode(dados_para_codificar, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# --- Proteção de rotas ---
# aponta para a rota de login, que é quem vai gerar o token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependência do FastAPI para proteger uma rota.

    Uso em uma rota:
        @router.get("/faturamento")
        def listar_faturamento(usuario = Depends(get_current_user)):
            ...
    """
    erro_credenciais = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        id_usuario = payload.get("sub")
        if id_usuario is None:
            raise erro_credenciais
        return payload
    except JWTError:
        raise erro_credenciais
