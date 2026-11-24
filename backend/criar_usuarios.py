"""
Cria os usuários de demonstração (um para cada perfil).

Como rodar (dentro da pasta backend, com o venv ativo):
    python criar_usuarios.py

Pode rodar de novo sem problema: usuários que já existem são pulados.
Troque as senhas abaixo se quiser.
"""

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_senha
from app.modules.auth.models import Usuario

USUARIOS = [
    ("Administrador", "admin@medcenter.com", "Admin@2026", "admin"),
    ("Recepção MedCenter", "recepcao@medcenter.com", "Recepcao@2026", "recepcao"),
    ("Dr. Rafael Almeida", "medico@medcenter.com", "Medico@2026", "medico"),
    ("Juliana Ramos", "enfermagem@medcenter.com", "Enfermagem@2026", "enfermagem"),
]


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for nome, email, senha, perfil in USUARIOS:
            existente = db.query(Usuario).filter(Usuario.email == email).first()
            if existente:
                print(f"já existe:  {email}")
                continue
            db.add(Usuario(nome=nome, email=email, senha=hash_senha(senha), perfil=perfil))
            db.commit()
            print(f"criado:     {email}  (perfil {perfil})")
    finally:
        db.close()

    print("\nContas para a demonstração:")
    for nome, email, senha, perfil in USUARIOS:
        print(f"  {perfil:<11} {email:<28} senha: {senha}")


if __name__ == "__main__":
    main()
