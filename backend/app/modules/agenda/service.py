"""
Serviços do módulo Corpo Clínico & Agenda.

POO usada aqui:
- Herança: todas as classes herdam o CRUD pronto de BaseService
- Polimorfismo: criar() e atualizar() são sobrescritos para aplicar as
  regras de negócio de cada entidade, e depois chamam super() para
  reaproveitar o comportamento padrão da classe pai
- Encapsulamento: as rotas só chamam os métodos públicos; a conexão
  com o banco (_db) fica escondida dentro das classes
"""

from datetime import date
from typing import List, Optional

from sqlalchemy import func

from app.core.base_service import BaseService
from app.modules.agenda.models import (
    Atendimento,
    Consulta,
    Especialidade,
    Medico,
    MedicoEspecialidade,
)
from app.modules.pacientes.models import Paciente

STATUS_CONSULTA = ("agendada", "realizada", "cancelada")


class EspecialidadeService(BaseService[Especialidade]):
    model = Especialidade


class MedicoService(BaseService[Medico]):
    model = Medico

    def criar(self, dados: dict) -> Medico:
        ids_especialidades = dados.pop("ids_especialidades", None) or []

        if dados.get("crm"):
            repetido = self._db.query(Medico).filter(Medico.crm == dados["crm"]).first()
            if repetido:
                raise ValueError("Já existe um médico cadastrado com esse CRM")

        # Valida as especialidades ANTES de criar, para não deixar médico pela metade
        for id_especialidade in ids_especialidades:
            if not self._db.query(Especialidade).filter(
                Especialidade.id_especialidade == id_especialidade
            ).first():
                raise ValueError(f"Especialidade {id_especialidade} não encontrada")

        medico = super().criar(dados)
        for id_especialidade in ids_especialidades:
            self.vincular_especialidade(medico.id_medico, id_especialidade)
        return medico

    def buscar(self, nome: Optional[str] = None) -> List[Medico]:
        query = self._db.query(Medico)
        if nome:
            query = query.filter(Medico.nome.ilike(f"%{nome}%"))
        return query.all()

    # ----- relação N:N com especialidade (tabela MEDICO_ESPECIALIDADE) -----
    def listar_especialidades(self, id_medico: int) -> List[Especialidade]:
        return (
            self._db.query(Especialidade)
            .join(
                MedicoEspecialidade,
                MedicoEspecialidade.id_especialidade == Especialidade.id_especialidade,
            )
            .filter(MedicoEspecialidade.id_medico == id_medico)
            .all()
        )

    def vincular_especialidade(
        self, id_medico: int, id_especialidade: int, data_inicio: Optional[date] = None
    ) -> MedicoEspecialidade:
        if not self.obter(id_medico, "id_medico"):
            raise ValueError("Médico não encontrado")
        if not self._db.query(Especialidade).filter(
            Especialidade.id_especialidade == id_especialidade
        ).first():
            raise ValueError("Especialidade não encontrada")

        ja_vinculado = (
            self._db.query(MedicoEspecialidade)
            .filter(
                MedicoEspecialidade.id_medico == id_medico,
                MedicoEspecialidade.id_especialidade == id_especialidade,
            )
            .first()
        )
        if ja_vinculado:
            raise ValueError("Esse médico já tem essa especialidade")

        vinculo = MedicoEspecialidade(
            id_medico=id_medico,
            id_especialidade=id_especialidade,
            data_inicio=data_inicio or date.today(),
        )
        self._db.add(vinculo)
        self._db.commit()
        self._db.refresh(vinculo)
        return vinculo

    def desvincular_especialidade(self, id_medico: int, id_especialidade: int) -> bool:
        vinculo = (
            self._db.query(MedicoEspecialidade)
            .filter(
                MedicoEspecialidade.id_medico == id_medico,
                MedicoEspecialidade.id_especialidade == id_especialidade,
            )
            .first()
        )
        if not vinculo:
            return False
        self._db.delete(vinculo)
        self._db.commit()
        return True


class ConsultaService(BaseService[Consulta]):
    model = Consulta

    def _tem_conflito(self, id_medico: int, data_consulta, ignorar_id: Optional[int] = None) -> bool:
        """Verifica se o médico já tem outra consulta (não cancelada) no mesmo horário."""
        query = self._db.query(Consulta).filter(
            Consulta.id_medico == id_medico,
            Consulta.data_consulta == data_consulta,
            Consulta.status != "cancelada",
        )
        if ignorar_id:
            query = query.filter(Consulta.id_consulta != ignorar_id)
        return query.first() is not None

    def criar(self, dados: dict) -> Consulta:
        status = dados.get("status") or "agendada"
        if status not in STATUS_CONSULTA:
            raise ValueError(f"Status inválido. Use um destes: {', '.join(STATUS_CONSULTA)}")

        if not self._db.query(Paciente).filter(Paciente.id_paciente == dados["id_paciente"]).first():
            raise ValueError("Paciente não encontrado")
        if not self._db.query(Medico).filter(Medico.id_medico == dados["id_medico"]).first():
            raise ValueError("Médico não encontrado")

        if self._tem_conflito(dados["id_medico"], dados["data_consulta"]):
            raise ValueError("Esse médico já tem uma consulta nesse horário")

        dados["status"] = status
        return super().criar(dados)

    def atualizar(self, objeto: Consulta, dados: dict) -> Consulta:
        if "status" in dados and dados["status"] not in STATUS_CONSULTA:
            raise ValueError(f"Status inválido. Use um destes: {', '.join(STATUS_CONSULTA)}")

        nova_data = dados.get("data_consulta")
        if nova_data and nova_data != objeto.data_consulta:
            if self._tem_conflito(objeto.id_medico, nova_data, ignorar_id=objeto.id_consulta):
                raise ValueError("Esse médico já tem uma consulta nesse horário")

        return super().atualizar(objeto, dados)

    def buscar(
        self,
        id_medico: Optional[int] = None,
        id_paciente: Optional[int] = None,
        data: Optional[date] = None,
        status: Optional[str] = None,
    ) -> List[Consulta]:
        """Usado pela tela de agenda: filtra por médico, paciente, dia e status."""
        query = self._db.query(Consulta)
        if id_medico:
            query = query.filter(Consulta.id_medico == id_medico)
        if id_paciente:
            query = query.filter(Consulta.id_paciente == id_paciente)
        if data:
            query = query.filter(func.date(Consulta.data_consulta) == data)
        if status:
            query = query.filter(Consulta.status == status)
        return query.order_by(Consulta.data_consulta).all()


class AtendimentoService(BaseService[Atendimento]):
    model = Atendimento

    def criar(self, dados: dict) -> Atendimento:
        consulta = self._db.query(Consulta).filter(
            Consulta.id_consulta == dados["id_consulta"]
        ).first()
        if not consulta:
            raise ValueError("Consulta não encontrada")
        if consulta.status == "cancelada":
            raise ValueError("Não dá para registrar atendimento de uma consulta cancelada")
        if self.obter_por_consulta(dados["id_consulta"]):
            raise ValueError("Essa consulta já tem um atendimento registrado")

        atendimento = super().criar(dados)

        # Regra: ao registrar o atendimento, a consulta passa a "realizada"
        consulta.status = "realizada"
        self._db.commit()
        return atendimento

    def obter_por_consulta(self, id_consulta: int) -> Optional[Atendimento]:
        return (
            self._db.query(Atendimento)
            .filter(Atendimento.id_consulta == id_consulta)
            .first()
        )
