"""
Rotas de autenticação: registrar usuário, fazer login e consultar
o próprio usuário logado (exemplo de rota protegida).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import criar_token, get_current_user, hash_senha, verificar_senha
from app.modules.auth import models, schemas

router = APIRouter()


@router.post("/registrar", response_model=schemas.UsuarioOut)
def registrar_usuario(dados: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """Cria um novo usuário (login) no sistema."""
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.email == dados.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Já existe um usuário com esse email")

    novo_usuario = models.Usuario(
        nome=dados.nome,
        email=dados.email,
        senha=hash_senha(dados.senha),  # nunca salva a senha em texto puro
        perfil=dados.perfil,
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario


@router.post("/login", response_model=schemas.TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Faz login e devolve um token JWT.

    Usa OAuth2PasswordRequestForm (campos "username" e "password") porque
    é o formato que o próprio Swagger (/docs) já sabe preencher no botão
    "Authorize" — aqui "username" é usado para receber o email.
    """
    usuario = db.query(models.Usuario).filter(models.Usuario.email == form.username).first()
    if not usuario or not verificar_senha(form.password, usuario.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )

    token = criar_token({"sub": str(usuario.id_usuario), "perfil": usuario.perfil})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UsuarioOut)
def usuario_logado(db: Session = Depends(get_db), payload: dict = Depends(get_current_user)):
    """
    Rota de EXEMPLO de endpoint protegido: só responde se um token
    válido for enviado. Use get_current_user assim em qualquer rota
    de qualquer módulo que precisar exigir login.
    """
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == int(payload["sub"])).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario
