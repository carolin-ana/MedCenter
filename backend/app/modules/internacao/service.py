"""
Serviços do módulo Internação e Enfermagem.

POO usada aqui:
- Herança: todas as classes reaproveitam o CRUD pronto de BaseService
- Polimorfismo: criar(), atualizar() e excluir() são sobrescritos para aplicar
  as regras de negócio de cada entidade e depois chamam super() para
  reaproveitar o comportamento padrão da classe pai
- Encapsulamento: as rotas só chamam os métodos públicos; a conexão com o
  banco (_db) fica escondida dentro das classes
"""

from datetime import datetime
from typing import Optional

from app.core.base_service import BaseService

from app.modules.agenda.models import Medico
from app.modules.financeiro.models import Faturamento
from app.modules.internacao.models import (
    Internacao,
    Enfermeiro,
    AtendimentoEnfermeiro,
    Quarto,
    InternacaoQuarto,
)
from app.modules.pacientes.models import Paciente

STATUS_QUARTO = ("disponivel", "ocupado", "manutencao")


def sincronizar_status_quarto(db, id_quarto: int) -> None:
    """
    Deixa o status do quarto coerente com a ocupação: 'ocupado' quando todos
    os leitos estão em uso, 'disponivel' caso contrário. Quarto em manutenção
    não é alterado.
    """
    quarto = db.query(Quarto).filter(Quarto.id_quarto == id_quarto).first()
    if not quarto or quarto.status == "manutencao":
        return
    ocupados = (
        db.query(InternacaoQuarto)
        .filter(InternacaoQuarto.id_quarto == id_quarto, InternacaoQuarto.data_saida.is_(None))
        .count()
    )
    novo_status = "ocupado" if ocupados >= (quarto.capacidade or 1) else "disponivel"
    if quarto.status != novo_status:
        quarto.status = novo_status
        db.commit()


class InternacaoService(BaseService[Internacao]):
    model = Internacao

    def _vinculos_ativos(self, id_internacao: int):
        return (
            self._db.query(InternacaoQuarto)
            .filter(InternacaoQuarto.id_internacao == id_internacao, InternacaoQuarto.data_saida.is_(None))
            .all()
        )

    def _validar_medico(self, id_medico: Optional[int]) -> None:
        if id_medico and not self._db.query(Medico).filter(Medico.id_medico == id_medico).first():
            raise ValueError("Médico responsável não encontrado")

    def criar(self, dados: dict) -> Internacao:
        if not self._db.query(Paciente).filter(Paciente.id_paciente == dados["id_paciente"]).first():
            raise ValueError("Paciente não encontrado")
        self._validar_medico(dados.get("id_medico_responsavel"))

        ja_internado = (
            self._db.query(Internacao)
            .filter(Internacao.id_paciente == dados["id_paciente"], Internacao.data_saida.is_(None))
            .first()
        )
        if ja_internado:
            raise ValueError("Esse paciente já tem uma internação ativa")

        dados["data_entrada"] = dados.get("data_entrada") or datetime.now()
        if dados.get("data_saida") is not None:
            raise ValueError("Uma internação nova não pode já ter data de saída. A alta é registrada depois.")
        return super().criar(dados)

    def atualizar(self, objeto: Internacao, dados: dict) -> Internacao:
        self._validar_medico(dados.get("id_medico_responsavel"))

        dando_alta = False
        if "data_saida" in dados:
            nova_saida = dados["data_saida"]
            if nova_saida is None and objeto.data_saida is not None:
                raise ValueError("Não é possível reabrir uma internação que já teve alta")
            if nova_saida is not None:
                entrada = dados.get("data_entrada") or objeto.data_entrada
                if entrada and nova_saida < entrada:
                    raise ValueError("A data de saída não pode ser anterior à data de entrada")
                dando_alta = objeto.data_saida is None

        internacao = super().atualizar(objeto, dados)

        if dando_alta:
            # Regra: a alta encerra a ocupação do quarto e libera o leito
            quartos_afetados = []
            for vinculo in self._vinculos_ativos(internacao.id_internacao):
                vinculo.data_saida = internacao.data_saida
                quartos_afetados.append(vinculo.id_quarto)
            self._db.commit()
            for id_quarto in set(quartos_afetados):
                sincronizar_status_quarto(self._db, id_quarto)
        return internacao

    def excluir(self, objeto: Internacao) -> None:
        if self._db.query(Faturamento).filter(Faturamento.id_internacao == objeto.id_internacao).first():
            raise ValueError("Não é possível excluir: existe faturamento ligado a essa internação")

        quartos_afetados = [
            v.id_quarto
            for v in self._db.query(InternacaoQuarto).filter(InternacaoQuarto.id_internacao == objeto.id_internacao).all()
        ]
        self._db.query(AtendimentoEnfermeiro).filter(
            AtendimentoEnfermeiro.id_internacao == objeto.id_internacao
        ).delete()
        self._db.query(InternacaoQuarto).filter(
            InternacaoQuarto.id_internacao == objeto.id_internacao
        ).delete()
        super().excluir(objeto)
        for id_quarto in set(quartos_afetados):
            sincronizar_status_quarto(self._db, id_quarto)


class EnfermeiroService(BaseService[Enfermeiro]):
    model = Enfermeiro

    def _coren_repetido(self, coren: str, ignorar_id: Optional[int] = None) -> bool:
        query = self._db.query(Enfermeiro).filter(Enfermeiro.coren == coren)
        if ignorar_id:
            query = query.filter(Enfermeiro.id_enfermeiro != ignorar_id)
        return query.first() is not None

    def criar(self, dados: dict) -> Enfermeiro:
        if dados.get("coren") and self._coren_repetido(dados["coren"]):
            raise ValueError("Já existe um enfermeiro com esse COREN")
        return super().criar(dados)

    def atualizar(self, objeto: Enfermeiro, dados: dict) -> Enfermeiro:
        if dados.get("coren") and self._coren_repetido(dados["coren"], objeto.id_enfermeiro):
            raise ValueError("Já existe um enfermeiro com esse COREN")
        return super().atualizar(objeto, dados)

    def excluir(self, objeto: Enfermeiro) -> None:
        if (
            self._db.query(AtendimentoEnfermeiro)
            .filter(AtendimentoEnfermeiro.id_enfermeiro == objeto.id_enfermeiro)
            .first()
        ):
            raise ValueError("Não é possível excluir: o enfermeiro tem atendimentos registrados")
        super().excluir(objeto)


class AtendimentoEnfermeiroService(BaseService[AtendimentoEnfermeiro]):
    model = AtendimentoEnfermeiro

    def criar(self, dados: dict) -> AtendimentoEnfermeiro:
        internacao = (
            self._db.query(Internacao).filter(Internacao.id_internacao == dados["id_internacao"]).first()
        )
        if not internacao:
            raise ValueError("Internação não encontrada")
        if internacao.data_saida is not None:
            raise ValueError("Só é possível registrar atendimento de enfermagem em internação ativa")
        if not self._db.query(Enfermeiro).filter(Enfermeiro.id_enfermeiro == dados["id_enfermeiro"]).first():
            raise ValueError("Enfermeiro não encontrado")

        dados["data_enfermeiro"] = dados.get("data_enfermeiro") or datetime.now()
        return super().criar(dados)


class QuartoService(BaseService[Quarto]):
    model = Quarto

    def _ocupacao(self, id_quarto: int) -> int:
        return (
            self._db.query(InternacaoQuarto)
            .filter(InternacaoQuarto.id_quarto == id_quarto, InternacaoQuarto.data_saida.is_(None))
            .count()
        )

    def _validar(self, dados: dict, objeto: Optional[Quarto] = None) -> None:
        numero = dados.get("numero_quarto")
        if objeto is None and not (numero or "").strip():
            raise ValueError("Informe o número do quarto")
        if numero:
            query = self._db.query(Quarto).filter(Quarto.numero_quarto == numero)
            if objeto is not None:
                query = query.filter(Quarto.id_quarto != objeto.id_quarto)
            if query.first():
                raise ValueError("Já existe um quarto com esse número")

        capacidade = dados.get("capacidade")
        if capacidade is not None and capacidade < 1:
            raise ValueError("A capacidade precisa ser de 1 leito em diante")

        status = dados.get("status")
        if status is not None and status not in STATUS_QUARTO:
            raise ValueError(f"Status inválido. Use um destes: {', '.join(STATUS_QUARTO)}")

    def criar(self, dados: dict) -> Quarto:
        self._validar(dados)
        dados["capacidade"] = dados.get("capacidade") or 1
        dados["status"] = dados.get("status") or "disponivel"
        return super().criar(dados)

    def atualizar(self, objeto: Quarto, dados: dict) -> Quarto:
        self._validar(dados, objeto)
        ocupados = self._ocupacao(objeto.id_quarto)
        capacidade = dados.get("capacidade")
        if capacidade is not None and capacidade < ocupados:
            raise ValueError(f"A capacidade não pode ser menor que o número de pacientes no quarto ({ocupados})")
        if dados.get("status") == "manutencao" and ocupados > 0:
            raise ValueError("Não é possível colocar em manutenção um quarto que está ocupado")

        quarto = super().atualizar(objeto, dados)
        sincronizar_status_quarto(self._db, quarto.id_quarto)  # corrige ocupado/disponivel pela ocupação real
        return quarto

    def excluir(self, objeto: Quarto) -> None:
        if (
            self._db.query(InternacaoQuarto).filter(InternacaoQuarto.id_quarto == objeto.id_quarto).first()
        ):
            raise ValueError("Não é possível excluir: o quarto tem histórico de internações")
        super().excluir(objeto)


class InternacaoQuartoService(BaseService[InternacaoQuarto]):
    model = InternacaoQuarto

    def _ocupacao(self, id_quarto: int) -> int:
        return (
            self._db.query(InternacaoQuarto)
            .filter(InternacaoQuarto.id_quarto == id_quarto, InternacaoQuarto.data_saida.is_(None))
            .count()
        )

    def criar(self, dados: dict) -> InternacaoQuarto:
        internacao = (
            self._db.query(Internacao).filter(Internacao.id_internacao == dados["id_internacao"]).first()
        )
        if not internacao:
            raise ValueError("Internação não encontrada")
        if internacao.data_saida is not None:
            raise ValueError("Essa internação já teve alta")

        quarto = self._db.query(Quarto).filter(Quarto.id_quarto == dados["id_quarto"]).first()
        if not quarto:
            raise ValueError("Quarto não encontrado")
        if quarto.status == "manutencao":
            raise ValueError("Esse quarto está em manutenção")
        if dados.get("data_saida") is not None:
            raise ValueError("Uma ocupação nova não pode já ter data de saída")

        atual = (
            self._db.query(InternacaoQuarto)
            .filter(
                InternacaoQuarto.id_internacao == internacao.id_internacao,
                InternacaoQuarto.data_saida.is_(None),
            )
            .first()
        )
        if atual and atual.id_quarto == quarto.id_quarto:
            raise ValueError("O paciente já está nesse quarto")
        if self._ocupacao(quarto.id_quarto) >= (quarto.capacidade or 1):
            raise ValueError("Quarto lotado: não há leito livre")

        entrada = dados.get("data_entrada") or datetime.now()
        dados["data_entrada"] = entrada
        quartos_afetados = [quarto.id_quarto]
        if atual:
            # Regra: pedir um quarto novo para quem já está em um quarto é uma transferência,
            # então a ocupação anterior é encerrada
            atual.data_saida = entrada
            quartos_afetados.append(atual.id_quarto)

        novo = super().criar(dados)
        for id_quarto in set(quartos_afetados):
            sincronizar_status_quarto(self._db, id_quarto)
        return novo

    def atualizar(self, objeto: InternacaoQuarto, dados: dict) -> InternacaoQuarto:
        if "data_saida" in dados:
            if objeto.data_saida is not None:
                # ocupação já encerrada: mantém a data original em vez de dar erro
                dados.pop("data_saida")
            elif dados["data_saida"] is not None and objeto.data_entrada and dados["data_saida"] < objeto.data_entrada:
                raise ValueError("A data de saída não pode ser anterior à data de entrada")

        vinculo = super().atualizar(objeto, dados)
        sincronizar_status_quarto(self._db, vinculo.id_quarto)
        return vinculo

    def excluir(self, objeto: InternacaoQuarto) -> None:
        id_quarto = objeto.id_quarto
        super().excluir(objeto)
        sincronizar_status_quarto(self._db, id_quarto)
