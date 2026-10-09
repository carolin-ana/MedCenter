"""
Serviço de Faturamento.

Conceitos de POO usados aqui:
- Herança: FaturamentoService herda todo o CRUD pronto de BaseService
- Polimorfismo: sobrescreve o método criar() para adicionar a regra de
  negócio própria deste módulo (puxar o convênio do paciente, impedir
  duas origens ao mesmo tempo), e no final chama super().criar() para
  reaproveitar o comportamento padrão da classe pai
"""

from app.core.base_service import BaseService
from app.modules.financeiro.models import Faturamento
from app.modules.pacientes.models import Paciente


class FaturamentoService(BaseService[Faturamento]):
    model = Faturamento

    def criar(self, dados: dict) -> Faturamento:
        if dados.get("id_consulta") and dados.get("id_internacao"):
            raise ValueError(
                "Um faturamento deve vir de uma consulta OU de uma internação, não as duas ao mesmo tempo"
            )

        # Se o convênio não veio preenchido, tenta puxar automaticamente do paciente
        if dados.get("id_convenio") is None:
            paciente = (
                self._db.query(Paciente)
                .filter(Paciente.id_paciente == dados["id_paciente"])
                .first()
            )
            if paciente and paciente.id_convenio:
                dados["id_convenio"] = paciente.id_convenio

        return super().criar(dados)  # reaproveita o criar() genérico da classe pai
