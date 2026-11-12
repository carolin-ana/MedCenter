"""
Serviços do módulo Pacientes — cada classe herda de BaseService (POO).

Polimorfismo: criar(), atualizar() e excluir() são sobrescritos para aplicar
as regras de cada entidade e depois chamam super() para reaproveitar o
comportamento padrão da classe pai.
"""

from typing import List, Optional

from sqlalchemy.exc import IntegrityError

from app.core.base_service import BaseService
from app.modules.pacientes.models import Convenio, Paciente, ContatoPaciente, Prontuario


class ConvenioService(BaseService[Convenio]):
    model = Convenio

    def _nome_repetido(self, nome: str, ignorar_id: Optional[int] = None) -> bool:
        query = self._db.query(Convenio).filter(Convenio.nome == nome)
        if ignorar_id:
            query = query.filter(Convenio.id_convenio != ignorar_id)
        return query.first() is not None

    def criar(self, dados: dict) -> Convenio:
        if self._nome_repetido(dados["nome"]):
            raise ValueError("Já existe um convênio com esse nome")
        return super().criar(dados)

    def atualizar(self, objeto: Convenio, dados: dict) -> Convenio:
        if dados.get("nome") and self._nome_repetido(dados["nome"], objeto.id_convenio):
            raise ValueError("Já existe um convênio com esse nome")
        return super().atualizar(objeto, dados)

    def excluir(self, objeto: Convenio) -> None:
        try:
            super().excluir(objeto)
        except IntegrityError:
            self._db.rollback()
            raise ValueError("Não é possível excluir: há pacientes ou faturamentos usando esse convênio")


class PacienteService(BaseService[Paciente]):
    model = Paciente

    def _validar(self, dados: dict, ignorar_id: Optional[int] = None) -> None:
        cpf = dados.get("cpf")
        if cpf:
            query = self._db.query(Paciente).filter(Paciente.cpf == cpf)
            if ignorar_id:
                query = query.filter(Paciente.id_paciente != ignorar_id)
            if query.first():
                raise ValueError("Já existe um paciente com esse CPF")

        id_convenio = dados.get("id_convenio")
        if id_convenio and not self._db.query(Convenio).filter(Convenio.id_convenio == id_convenio).first():
            raise ValueError("Convênio não encontrado")

    def criar(self, dados: dict) -> Paciente:
        self._validar(dados)
        return super().criar(dados)

    def atualizar(self, objeto: Paciente, dados: dict) -> Paciente:
        self._validar(dados, ignorar_id=objeto.id_paciente)
        return super().atualizar(objeto, dados)

    def excluir(self, objeto: Paciente) -> None:
        """Apaga também contatos e prontuário; se houver consultas, internações
        ou faturamentos, desfaz tudo e avisa em vez de dar erro 500."""
        try:
            self._db.query(ContatoPaciente).filter(ContatoPaciente.id_paciente == objeto.id_paciente).delete()
            self._db.query(Prontuario).filter(Prontuario.id_paciente == objeto.id_paciente).delete()
            super().excluir(objeto)
        except IntegrityError:
            self._db.rollback()
            raise ValueError("Não é possível excluir: o paciente tem consultas, internações ou faturamentos vinculados")

    def buscar(self, nome: Optional[str] = None, cpf: Optional[str] = None) -> List[Paciente]:
        """Busca por nome (parte do nome) ou CPF, usada pela tela de busca."""
        query = self._db.query(self.model)
        if nome:
            query = query.filter(self.model.nome.ilike(f"%{nome}%"))
        if cpf:
            query = query.filter(self.model.cpf == cpf)
        return query.all()


class ContatoPacienteService(BaseService[ContatoPaciente]):
    model = ContatoPaciente

    def _limpar_preferencial(self, id_paciente: int, ignorar_id: Optional[int] = None) -> None:
        """Regra: cada paciente tem no máximo um contato preferencial."""
        query = self._db.query(ContatoPaciente).filter(
            ContatoPaciente.id_paciente == id_paciente,
            ContatoPaciente.eh_preferencial.is_(True),
        )
        if ignorar_id:
            query = query.filter(ContatoPaciente.id_contato != ignorar_id)
        for contato in query.all():
            contato.eh_preferencial = False

    def criar(self, dados: dict) -> ContatoPaciente:
        if not self._db.query(Paciente).filter(Paciente.id_paciente == dados["id_paciente"]).first():
            raise ValueError("Paciente não encontrado")
        if dados.get("eh_preferencial"):
            self._limpar_preferencial(dados["id_paciente"])
        return super().criar(dados)

    def atualizar(self, objeto: ContatoPaciente, dados: dict) -> ContatoPaciente:
        if dados.get("eh_preferencial"):
            self._limpar_preferencial(objeto.id_paciente, ignorar_id=objeto.id_contato)
        return super().atualizar(objeto, dados)

    def listar_por_paciente(self, id_paciente: int) -> List[ContatoPaciente]:
        return self._db.query(self.model).filter(self.model.id_paciente == id_paciente).all()


class ProntuarioService(BaseService[Prontuario]):
    model = Prontuario

    def criar(self, dados: dict) -> Prontuario:
        if not self._db.query(Paciente).filter(Paciente.id_paciente == dados["id_paciente"]).first():
            raise ValueError("Paciente não encontrado")
        if self.obter_por_paciente(dados["id_paciente"]):
            raise ValueError("Esse paciente já tem um prontuário")
        return super().criar(dados)

    def obter_por_paciente(self, id_paciente: int) -> Optional[Prontuario]:
        return self._db.query(self.model).filter(self.model.id_paciente == id_paciente).first()
