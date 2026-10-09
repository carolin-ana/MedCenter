"""
Serviços do módulo Pacientes — cada classe herda de BaseService.
"""

from typing import List, Optional

from app.core.base_service import BaseService
from app.modules.pacientes.models import Convenio, Paciente, ContatoPaciente, Prontuario


class ConvenioService(BaseService[Convenio]):
    model = Convenio


class PacienteService(BaseService[Paciente]):
    model = Paciente

    def buscar(self, nome: Optional[str] = None, cpf: Optional[str] = None) -> List[Paciente]:
        """
        Método extra (além do CRUD básico) para a tela de busca de
        paciente por nome ou CPF — demonstra que a classe de serviço
        pode crescer com métodos próprios do módulo, não só o CRUD.
        """
        query = self._db.query(self.model)
        if nome:
            query = query.filter(self.model.nome.ilike(f"%{nome}%"))
        if cpf:
            query = query.filter(self.model.cpf == cpf)
        return query.all()


class ContatoPacienteService(BaseService[ContatoPaciente]):
    model = ContatoPaciente

    def listar_por_paciente(self, id_paciente: int) -> List[ContatoPaciente]:
        return self._db.query(self.model).filter(self.model.id_paciente == id_paciente).all()


class ProntuarioService(BaseService[Prontuario]):
    model = Prontuario

    def obter_por_paciente(self, id_paciente: int) -> Optional[Prontuario]:
        return self._db.query(self.model).filter(self.model.id_paciente == id_paciente).first()
