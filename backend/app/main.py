"""
Ponto de entrada do backend. É esse arquivo que o comando
    uvicorn app.main:app --reload
procura (app/main.py -> variável "app").
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.auth.models import Usuario
from app.core.database import Base, engine
from app.modules.auth.models import Usuario

from app.modules.pacientes.models import Convenio, Paciente, ContatoPaciente, Prontuario
from app.modules.agenda.models import Especialidade, Medico, MedicoEspecialidade, Consulta, Atendimento
from app.modules.internacao.models import Internacao, Enfermeiro, AtendimentoEnfermeiro, Quarto, InternacaoQuarto
from app.modules.financeiro.models import Faturamento
from app.modules.farmacia_exames.models import Medicamento, Exame
# ---------------------------------------------------------------
# À medida que cada módulo (pacientes, agenda, farmacia_exames,
# internacao, financeiro) for criando seus models, importe-os
# aqui. É esse import que faz o SQLAlchemy "conhecer" a tabela
# na hora de criar tudo no banco (Base.metadata.create_all).
#
# Exemplo (descomente conforme os módulos forem ficando prontos):
# from app.modules.pacientes.models import Paciente, ContatoPaciente, Prontuario, Convenio
# from app.modules.agenda.models import Medico, Especialidade, Consulta, Atendimento
# from app.modules.farmacia_exames.models import Prescricao, Medicamento, PrescricaoMedicamento, Exame, PedidoExame, PedidoExameItem
# from app.modules.internacao.models import Internacao, Quarto, InternacaoQuarto, Enfermeira, AtendimentoEnfermeira
# from app.modules.financeiro.models import Faturamento
# from app.modules.auth.models import Usuario
# ---------------------------------------------------------------

app = FastAPI(title="MedCenter API")

# Libera o frontend (que roda como arquivo HTML separado, em outra
# "origem") a chamar essa API sem ser bloqueado pelo navegador.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção, troque "*" pelo endereço real do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cria automaticamente, no MySQL, todas as tabelas dos models importados
# acima — só cria as que ainda não existem, não apaga dados existentes.
Base.metadata.create_all(bind=engine)


@app.get("/")
def raiz():
    """Rota simples só para confirmar que a API está no ar."""
    return {"status": "MedCenter API no ar"}


from app.modules.auth.routes import router as auth_router
app.include_router(auth_router, prefix="/auth", tags=["Autenticação"])

from app.modules.financeiro.routes import router as financeiro_router
app.include_router(financeiro_router, prefix="/faturamento", tags=["Faturamento"])

from app.modules.pacientes.routes import router as pacientes_router
app.include_router(pacientes_router, tags=["Pacientes"])

from app.modules.farmacia_exames.routes import router as farmacia_exames_router
app.include_router(farmacia_exames_router)

from app.modules.agenda.routes import router as agenda_router
app.include_router(agenda_router)