"""
Serviços do módulo "Visão do Paciente" — o diferencial do MedCenter.

Problema que resolve: num hospital, a informação de um mesmo paciente fica
espalhada por setores (recepção, agenda, farmácia, exames, enfermagem e
financeiro). Para entender a situação de uma pessoa, alguém precisa abrir
vários sistemas. Aqui, uma única consulta junta tudo em uma linha do tempo,
e um painel de alertas avisa o que precisa de atenção (leitos, estoque,
exames sem resultado e cobranças pendentes).

POO: cada serviço é uma classe que guarda a sessão do banco em um atributo
interno (_db) e expõe poucos métodos públicos; os métodos pequenos que
começam com "_" são o trabalho interno (encapsulamento).
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.modules.agenda.models import Atendimento, Consulta, Medico
from app.modules.farmacia_exames.models import (
    Exame,
    Medicamento,
    PedidoExame,
    PedidoExameItem,
    Prescricao,
    PrescricaoMedicamento,
)
from app.modules.financeiro.models import Faturamento
from app.modules.internacao.models import Internacao, InternacaoQuarto, Quarto
from app.modules.pacientes.models import ContatoPaciente, Convenio, Paciente, Prontuario


# ---------------------------------------------------------------
# Funções auxiliares (internas do módulo)
# ---------------------------------------------------------------
def _como_datetime(valor) -> Optional[datetime]:
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, date):
        return datetime.combine(valor, datetime.min.time())
    return None


def _iso(valor) -> Optional[str]:
    dt = _como_datetime(valor)
    return dt.isoformat() if dt else None


def _idade(nascimento) -> Optional[int]:
    if not nascimento:
        return None
    hoje = date.today()
    return hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))


def _texto(valor) -> str:
    return (valor or "").strip() if isinstance(valor, str) else ""


class VisaoPacienteService:
    """Monta a linha do tempo completa de um paciente."""

    def __init__(self, db: Session):
        self._db = db

    # ----- cabeçalho do paciente -----
    def _cabecalho(self, paciente: Paciente) -> Dict[str, Any]:
        convenio = None
        if paciente.id_convenio:
            convenio = self._db.query(Convenio).filter(Convenio.id_convenio == paciente.id_convenio).first()
        prontuario = (
            self._db.query(Prontuario)
            .filter(Prontuario.id_paciente == paciente.id_paciente)
            .first()
        )
        contatos = (
            self._db.query(ContatoPaciente)
            .filter(ContatoPaciente.id_paciente == paciente.id_paciente)
            .all()
        )
        return {
            "id_paciente": paciente.id_paciente,
            "nome": paciente.nome,
            "cpf": paciente.cpf,
            "data_nascimento": _iso(paciente.data_nascimento),
            "idade": _idade(paciente.data_nascimento),
            "sexo": paciente.sexo,
            "convenio": convenio.nome if convenio else None,
            "numero_carteirinha": paciente.numero_carteirinha,
            "tipo_sangue": prontuario.tipo_sangue if prontuario else None,
            "observacoes_prontuario": _texto(prontuario.observacoes) if prontuario else "",
            "contatos": [
                {
                    "tipo": c.tipo_contato,
                    "valor": c.valor_contato,
                    "preferencial": bool(c.eh_preferencial),
                }
                for c in contatos
            ],
        }

    # ----- consultas e atendimentos -----
    def _consultas(self, id_paciente: int):
        consultas = self._db.query(Consulta).filter(Consulta.id_paciente == id_paciente).all()
        ids_consulta = [c.id_consulta for c in consultas]
        ids_medico = {c.id_medico for c in consultas if c.id_medico}

        medicos = {}
        if ids_medico:
            medicos = {
                m.id_medico: m
                for m in self._db.query(Medico).filter(Medico.id_medico.in_(ids_medico)).all()
            }
        atendimentos = []
        if ids_consulta:
            atendimentos = (
                self._db.query(Atendimento).filter(Atendimento.id_consulta.in_(ids_consulta)).all()
            )
        por_consulta = {a.id_consulta: a for a in atendimentos}

        eventos = []
        for c in consultas:
            medico = medicos.get(c.id_medico)
            detalhes = []
            atendimento = por_consulta.get(c.id_consulta)
            if atendimento:
                if _texto(atendimento.diagnostico):
                    detalhes.append(f"Diagnóstico: {_texto(atendimento.diagnostico)}")
                if _texto(atendimento.observacoes):
                    detalhes.append(f"Observações: {_texto(atendimento.observacoes)}")
            eventos.append(
                {
                    "tipo": "consulta",
                    "data": _iso(c.data_consulta),
                    "titulo": f"Consulta com {medico.nome}" if medico else "Consulta",
                    "detalhes": detalhes,
                    "status": (c.status or "").lower(),
                }
            )
        return eventos, atendimentos

    # ----- prescrições -----
    def _prescricoes(self, atendimentos: List[Atendimento]):
        ids_atendimento = [a.id_atendimento for a in atendimentos]
        if not ids_atendimento:
            return []
        prescricoes = (
            self._db.query(Prescricao).filter(Prescricao.id_atendimento.in_(ids_atendimento)).all()
        )
        ids_prescricao = [p.id_prescricao for p in prescricoes]
        itens = []
        if ids_prescricao:
            itens = (
                self._db.query(PrescricaoMedicamento, Medicamento)
                .join(Medicamento, Medicamento.id_medicamento == PrescricaoMedicamento.id_medicamento)
                .filter(PrescricaoMedicamento.id_prescricao.in_(ids_prescricao))
                .all()
            )
        linhas: Dict[int, List[str]] = {}
        for item, medicamento in itens:
            linha = f"{medicamento.nome} — {item.dosagem}, {item.frequencia}, por {item.duracao}"
            linhas.setdefault(item.id_prescricao, []).append(linha)

        eventos = []
        for p in prescricoes:
            detalhes = linhas.get(p.id_prescricao, [])
            if _texto(p.observacao):
                detalhes = detalhes + [f"Observação: {_texto(p.observacao)}"]
            eventos.append(
                {
                    "tipo": "prescricao",
                    "data": _iso(p.data_prescricao),
                    "titulo": "Prescrição de medicamentos",
                    "detalhes": detalhes,
                    "status": (p.status or "").lower(),
                }
            )
        return eventos

    # ----- exames -----
    def _exames(self, atendimentos: List[Atendimento]):
        ids_atendimento = [a.id_atendimento for a in atendimentos]
        if not ids_atendimento:
            return []
        pedidos = (
            self._db.query(PedidoExame).filter(PedidoExame.id_atendimento.in_(ids_atendimento)).all()
        )
        ids_pedido = [p.id_pedido_exame for p in pedidos]
        itens = []
        if ids_pedido:
            itens = (
                self._db.query(PedidoExameItem, Exame)
                .join(Exame, Exame.id_exame == PedidoExameItem.id_exame)
                .filter(PedidoExameItem.id_pedido_exame.in_(ids_pedido))
                .all()
            )
        linhas: Dict[int, List[str]] = {}
        for item, exame in itens:
            resultado = _texto(item.resultado)
            linha = f"{exame.nome}: {resultado}" if resultado else f"{exame.nome}: aguardando resultado"
            linhas.setdefault(item.id_pedido_exame, []).append(linha)

        return [
            {
                "tipo": "exame",
                "data": _iso(p.data_pedido),
                "titulo": "Pedido de exames",
                "detalhes": linhas.get(p.id_pedido_exame, []),
                "status": (p.status or "").lower(),
            }
            for p in pedidos
        ]

    # ----- internações -----
    def _internacoes(self, id_paciente: int):
        internacoes = self._db.query(Internacao).filter(Internacao.id_paciente == id_paciente).all()
        ids_internacao = [i.id_internacao for i in internacoes]
        ids_medico = {i.id_medico_responsavel for i in internacoes if i.id_medico_responsavel}

        medicos = {}
        if ids_medico:
            medicos = {
                m.id_medico: m
                for m in self._db.query(Medico).filter(Medico.id_medico.in_(ids_medico)).all()
            }
        quartos_por_internacao: Dict[int, List[str]] = {}
        if ids_internacao:
            vinculos = (
                self._db.query(InternacaoQuarto, Quarto)
                .join(Quarto, Quarto.id_quarto == InternacaoQuarto.id_quarto)
                .filter(InternacaoQuarto.id_internacao.in_(ids_internacao))
                .all()
            )
            for vinculo, quarto in vinculos:
                rotulo = f"Quarto {quarto.numero_quarto}" + (f" ({quarto.tipo})" if quarto.tipo else "")
                quartos_por_internacao.setdefault(vinculo.id_internacao, []).append(rotulo)

        eventos = []
        for i in internacoes:
            medico = medicos.get(i.id_medico_responsavel)
            detalhes = []
            if _texto(i.motivo_internacao):
                detalhes.append(f"Motivo: {_texto(i.motivo_internacao)}")
            if medico:
                detalhes.append(f"Médico responsável: {medico.nome}")
            if quartos_por_internacao.get(i.id_internacao):
                detalhes.append("Quartos: " + ", ".join(quartos_por_internacao[i.id_internacao]))
            eventos.append(
                {
                    "tipo": "internacao",
                    "data": _iso(i.data_entrada),
                    "titulo": "Internação",
                    "detalhes": detalhes,
                    "status": "ativa" if i.data_saida is None else "encerrada",
                }
            )
            if i.data_saida is not None:
                eventos.append(
                    {
                        "tipo": "alta",
                        "data": _iso(i.data_saida),
                        "titulo": "Alta hospitalar",
                        "detalhes": [],
                        "status": "alta",
                    }
                )
        return eventos, internacoes

    # ----- cobranças -----
    def _cobrancas(self, id_paciente: int):
        faturamentos = self._db.query(Faturamento).filter(Faturamento.id_paciente == id_paciente).all()
        ids_convenio = {f.id_convenio for f in faturamentos if f.id_convenio}
        convenios = {}
        if ids_convenio:
            convenios = {
                c.id_convenio: c
                for c in self._db.query(Convenio).filter(Convenio.id_convenio.in_(ids_convenio)).all()
            }
        eventos = []
        for f in faturamentos:
            origem = "Consulta" if f.id_consulta else ("Internação" if f.id_internacao else "Atendimento")
            convenio = convenios.get(f.id_convenio)
            eventos.append(
                {
                    "tipo": "cobranca",
                    "data": _iso(f.data_faturamento),
                    "titulo": f"Cobrança de {origem.lower()}",
                    "detalhes": [f"Cobrado de: {convenio.nome if convenio else 'Particular'}"],
                    "valor": float(f.valor_total or 0),
                    "status": (f.status or "").lower(),
                }
            )
        return eventos

    # ----- método público: monta tudo -----
    def montar(self, id_paciente: int) -> Optional[Dict[str, Any]]:
        paciente = self._db.query(Paciente).filter(Paciente.id_paciente == id_paciente).first()
        if not paciente:
            return None

        eventos_consulta, atendimentos = self._consultas(id_paciente)
        eventos_internacao, internacoes = self._internacoes(id_paciente)
        eventos_prescricao = self._prescricoes(atendimentos)
        eventos_exame = self._exames(atendimentos)
        eventos_cobranca = self._cobrancas(id_paciente)

        eventos = (
            eventos_consulta + eventos_prescricao + eventos_exame + eventos_internacao + eventos_cobranca
        )
        eventos.sort(key=lambda e: e["data"] or "", reverse=True)  # mais recentes primeiro

        itens_exame_sem_resultado = sum(
            1
            for e in eventos_exame
            for linha in e["detalhes"]
            if linha.endswith("aguardando resultado")
        )
        total_cobrado = sum(e["valor"] for e in eventos_cobranca)
        total_pendente = sum(e["valor"] for e in eventos_cobranca if e["status"] == "pendente")

        return {
            "paciente": self._cabecalho(paciente),
            "resumo": {
                "consultas": len(eventos_consulta),
                "prescricoes": len(eventos_prescricao),
                "exames": len(eventos_exame),
                "internacoes": len(internacoes),
                "internado_agora": any(i.data_saida is None for i in internacoes),
                "exames_sem_resultado": itens_exame_sem_resultado,
                "total_cobrado": total_cobrado,
                "total_pendente": total_pendente,
            },
            "eventos": eventos,
        }


class AlertasService:
    """Reúne o que precisa de atenção no hospital agora."""

    def __init__(self, db: Session):
        self._db = db

    def _leitos(self) -> Dict[str, Any]:
        quartos = self._db.query(Quarto).order_by(Quarto.numero_quarto).all()
        ativos = (
            self._db.query(InternacaoQuarto.id_quarto, func.count(InternacaoQuarto.id_internacao_quarto))
            .filter(InternacaoQuarto.data_saida.is_(None))
            .group_by(InternacaoQuarto.id_quarto)
            .all()
        )
        ocupacao = {id_quarto: total for id_quarto, total in ativos}

        lista = []
        total_leitos = 0
        total_ocupados = 0
        for q in quartos:
            manutencao = (q.status or "").lower() == "manutencao"
            capacidade = q.capacidade or 0
            ocupados = ocupacao.get(q.id_quarto, 0)
            if not manutencao:
                total_leitos += capacidade
                total_ocupados += ocupados
            lista.append(
                {
                    "numero": q.numero_quarto,
                    "tipo": q.tipo,
                    "capacidade": capacidade,
                    "ocupados": ocupados,
                    "manutencao": manutencao,
                }
            )
        taxa = round(100 * total_ocupados / total_leitos) if total_leitos else 0
        return {
            "total": total_leitos,
            "ocupados": total_ocupados,
            "livres": max(total_leitos - total_ocupados, 0),
            "taxa": taxa,
            "quartos": lista,
        }

    def _estoque_baixo(self, limite: int) -> List[Dict[str, Any]]:
        medicamentos = (
            self._db.query(Medicamento)
            .filter(Medicamento.quantidade_estoque <= limite)
            .order_by(Medicamento.quantidade_estoque)
            .all()
        )
        return [{"nome": m.nome, "quantidade": m.quantidade_estoque} for m in medicamentos]

    def montar(self, limite_estoque: int = 70) -> Dict[str, Any]:
        exames_sem_resultado = (
            self._db.query(func.count(PedidoExameItem.id_pedido_exame_item))
            .filter(or_(PedidoExameItem.resultado.is_(None), PedidoExameItem.resultado == ""))
            .scalar()
            or 0
        )
        pendentes = (
            self._db.query(func.count(Faturamento.id_faturamento), func.coalesce(func.sum(Faturamento.valor_total), 0))
            .filter(Faturamento.status == "pendente")
            .first()
        )
        internados = (
            self._db.query(func.count(Internacao.id_internacao)).filter(Internacao.data_saida.is_(None)).scalar() or 0
        )
        return {
            "leitos": self._leitos(),
            "estoque_baixo": self._estoque_baixo(limite_estoque),
            "limite_estoque": limite_estoque,
            "exames_sem_resultado": exames_sem_resultado,
            "faturamentos_pendentes": pendentes[0] if pendentes else 0,
            "valor_pendente": float(pendentes[1]) if pendentes else 0.0,
            "internados": internados,
        }
