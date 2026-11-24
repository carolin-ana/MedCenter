"""
Aplica o controle de acesso por perfil nos módulos do backend.

Como rodar (na RAIZ do projeto, a pasta que tem backend e frontend):
    python aplicar_permissoes.py

O que faz: troca, em cada routes.py, a linha que criava o router por uma
que exige o perfil certo, e acrescenta o import. Antes de mexer em cada
arquivo, guarda uma cópia com final .bak. Pode rodar de novo sem problema.
"""

import re
import shutil
from pathlib import Path

BASE = Path("backend/app/modules")
IMPORT = "from app.core.permissoes import exigir_acesso"

# (arquivo, texto antigo, texto novo)
TROCAS = [
    ("pacientes/routes.py",
     "router = APIRouter(dependencies=[Depends(get_current_user)])",
     'router = APIRouter(dependencies=[Depends(exigir_acesso("pacientes"))])'),
    ("agenda/routes.py",
     "router = APIRouter(dependencies=[Depends(get_current_user)])",
     'router = APIRouter(dependencies=[Depends(exigir_acesso("agenda"))])'),
    ("farmacia_exames/routes.py",
     "dependencies=[Depends(get_current_user)],",
     'dependencies=[Depends(exigir_acesso("farmacia"))],'),
    ("internacao/routes.py",
     'router = APIRouter(tags=["Internação & Enfermagem"])',
     'router = APIRouter(tags=["Internação & Enfermagem"], dependencies=[Depends(exigir_acesso("internacao"))])'),
    ("financeiro/routes.py",
     "router = APIRouter()",
     'router = APIRouter(dependencies=[Depends(exigir_acesso("financeiro"))])'),
    ("auth/routes.py",
     "def registrar_usuario(dados: schemas.UsuarioCreate, db: Session = Depends(get_db)):",
     'def registrar_usuario(\n    dados: schemas.UsuarioCreate,\n    db: Session = Depends(get_db),\n    _admin: dict = Depends(exigir_acesso("usuarios")),\n):'),
]


def acrescentar_import(texto: str) -> str:
    if IMPORT in texto:
        return texto
    for ancora in (r"^from app\.core\.security import .*$", r"^from app\.core\.database import .*$"):
        m = re.search(ancora, texto, flags=re.MULTILINE)
        if m:
            return texto[: m.end()] + "\n" + IMPORT + texto[m.end():]
    # último recurso: depois da primeira linha de import do fastapi
    m = re.search(r"^from fastapi import .*$", texto, flags=re.MULTILINE)
    if m:
        return texto[: m.end()] + "\n" + IMPORT + texto[m.end():]
    return IMPORT + "\n" + texto


def main():
    if not BASE.exists():
        print("Não achei backend/app/modules. Rode este script na raiz do projeto (pasta com backend e frontend).")
        return
    problemas = 0
    for arquivo, antigo, novo in TROCAS:
        caminho = BASE / arquivo
        if not caminho.exists():
            print(f"[ATENÇÃO] {arquivo}: arquivo não encontrado")
            problemas += 1
            continue
        texto = caminho.read_text(encoding="utf-8")
        if "exigir_acesso(" in texto and novo.split("(", 1)[0] in texto and 'exigir_acesso("' in texto:
            print(f"[ok]      {arquivo}: já estava aplicado")
            continue
        if texto.count(antigo) != 1:
            print(f"[ATENÇÃO] {arquivo}: não achei a linha esperada. Edite à mão:\n          troque  {antigo!r}\n          por     {novo!r}")
            problemas += 1
            continue
        shutil.copy(caminho, str(caminho) + ".bak")
        texto = texto.replace(antigo, novo)
        texto = acrescentar_import(texto)
        caminho.write_text(texto, encoding="utf-8")
        print(f"[feito]   {arquivo}")
    print()
    if problemas:
        print(f"{problemas} arquivo(s) precisam de atenção (veja as mensagens acima).")
    else:
        print("Tudo aplicado. Reinicie o backend e rode: python criar_usuarios.py (dentro de backend).")


if __name__ == "__main__":
    main()
