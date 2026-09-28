"""
Conexão com o MySQL via SQLAlchemy.
Todos os módulos (pacientes, agenda, financeiro...) importam Base e get_db daqui.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# engine = a "porta de entrada" para o banco
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# fábrica de sessões (cada requisição usa uma sessão própria)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# classe base da qual todos os models (Paciente, Medico, etc.) vão herdar
Base = declarative_base()


def get_db():
    """
    Dependência do FastAPI: abre uma sessão do banco, entrega para a rota
    usar, e garante que ela é fechada no final — mesmo se der erro.

    Uso em uma rota:
        @router.get("/pacientes")
        def listar_pacientes(db: Session = Depends(get_db)):
            return db.query(Paciente).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
