"""
Configurações centrais do projeto.
Lê os dados sensíveis (senha do banco, chave secreta) de um arquivo .env,
em vez de deixar isso escrito direto no código.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Banco de dados MySQL ---
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_HOST: str = "localhost"
    DB_PORT: str = "3306"
    DB_NAME: str = "medcenter"

    # --- Autenticação (JWT) ---
    SECRET_KEY: str = "troque-essa-chave-por-uma-bem-aleatoria"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # token dura 8 horas

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"


# Instância única, importada em todo o resto do projeto
settings = Settings()
