
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.farmacia_exames.models import (
    Medicamento,
    Exame,
    Prescricao,
    PrescricaoMedicamento,
    PedidoExame,
    PedidoExameItem,
)
from app.modules.farmacia_exames.schema import (
    MedicamentoCreate,
    ExameCreate,
    PrescricaoCreate,
    PrescricaoMedicamentoCreate,
    PedidoExameCreate,
    PedidoExameItemCreate,
)


# =====================================================
# FUNÇÕES AUXILIARES
# =====================================================

def obter_ou_404(db: Session, modelo, campo_id, valor_id, mensagem):
    registro = db.query(modelo).filter(
        campo_id == valor_id
    ).first()

    if registro is None:
        raise HTTPException(status_code=404, detail=mensagem)

    return registro


def salvar_novo(db: Session, registro):
    try:
        db.add(registro)
        db.commit()
        db.refresh(registro)
        return registro
    except Exception:
        db.rollback()
        raise


def salvar_alteracao(db: Session, registro):
    try:
        db.commit()
        db.refresh(registro)
        return registro
    except Exception:
        db.rollback()
        raise


def excluir_registro(db: Session, registro):
    try:
        db.delete(registro)
        db.commit()
    except Exception:
        db.rollback()
        raise


# =====================================================
# MEDICAMENTOS
# =====================================================

def listar_medicamentos(db: Session):
    return db.query(Medicamento).all()


def buscar_medicamento(db: Session, id_medicamento: int):
    return obter_ou_404(
        db, Medicamento, Medicamento.id_medicamento,
        id_medicamento, "Medicamento não encontrado"
    )


def cadastrar_medicamento(db: Session, dados: MedicamentoCreate):
    novo = Medicamento(
        nome=dados.nome,
        descricao=dados.descricao,
        quantidade_estoque=dados.quantidade_estoque,
    )
    return salvar_novo(db, novo)


def atualizar_medicamento(
    db: Session, id_medicamento: int, dados: MedicamentoCreate
):
    registro = buscar_medicamento(db, id_medicamento)
    registro.nome = dados.nome
    registro.descricao = dados.descricao
    registro.quantidade_estoque = dados.quantidade_estoque
    return salvar_alteracao(db, registro)


def excluir_medicamento(db: Session, id_medicamento: int):
    medicamento = buscar_medicamento(db, id_medicamento)

    try:
        db.delete(medicamento)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {"mensagem": "Medicamento excluído com sucesso"}


# =====================================================
# EXAMES
# =====================================================

def listar_exames(db: Session):
    return db.query(Exame).all()


def buscar_exame(db: Session, id_exame: int):
    return obter_ou_404(
        db, Exame, Exame.id_exame,
        id_exame, "Exame não encontrado"
    )


def cadastrar_exame(db: Session, dados: ExameCreate):
    novo = Exame(
        nome=dados.nome,
        descricao=dados.descricao,
    )
    return salvar_novo(db, novo)


def atualizar_exame(db: Session, id_exame: int, dados: ExameCreate):
    registro = buscar_exame(db, id_exame)
    registro.nome = dados.nome
    registro.descricao = dados.descricao
    return salvar_alteracao(db, registro)


def excluir_exame(db: Session, id_exame: int):
    registro = buscar_exame(db, id_exame)
    excluir_registro(db, registro)
    return {"mensagem": "Exame excluído com sucesso"}


# =====================================================
# PRESCRIÇÕES
# =====================================================

def listar_prescricoes(db: Session):
    return db.query(Prescricao).all()


def buscar_prescricao(db: Session, id_prescricao: int):
    return obter_ou_404(
        db, Prescricao, Prescricao.id_prescricao,
        id_prescricao, "Prescrição não encontrada"
    )


def cadastrar_prescricao(db: Session, dados: PrescricaoCreate):
    novo = Prescricao(
        id_atendimento=dados.id_atendimento,
        observacao=dados.observacao,
        status=dados.status,
    )
    return salvar_novo(db, novo)


def atualizar_prescricao(
    db: Session, id_prescricao: int, dados: PrescricaoCreate
):
    registro = buscar_prescricao(db, id_prescricao)
    registro.id_atendimento = dados.id_atendimento
    registro.observacao = dados.observacao
    registro.status = dados.status
    return salvar_alteracao(db, registro)


def excluir_prescricao(db: Session, id_prescricao: int):
    registro = buscar_prescricao(db, id_prescricao)
    excluir_registro(db, registro)
    return {"mensagem": "Prescrição excluída com sucesso"}


# =====================================================
# MEDICAMENTOS DA PRESCRIÇÃO
# =====================================================

def listar_prescricao_medicamentos(db: Session):
    return db.query(PrescricaoMedicamento).all()


def buscar_prescricao_medicamento(
    db: Session, id_prescricao_medicamento: int
):
    return obter_ou_404(
        db,
        PrescricaoMedicamento,
        PrescricaoMedicamento.id_prescricao_medicamento,
        id_prescricao_medicamento,
        "Medicamento da prescrição não encontrado",
    )


def cadastrar_prescricao_medicamento(
    db: Session, dados: PrescricaoMedicamentoCreate
):
    novo = PrescricaoMedicamento(
        id_prescricao=dados.id_prescricao,
        id_medicamento=dados.id_medicamento,
        dosagem=dados.dosagem,
        frequencia=dados.frequencia,
        duracao=dados.duracao,
        quantidade=dados.quantidade,
        instrucoes=dados.instrucoes,
    )
    return salvar_novo(db, novo)


def atualizar_prescricao_medicamento(
    db: Session,
    id_prescricao_medicamento: int,
    dados: PrescricaoMedicamentoCreate,
):
    registro = buscar_prescricao_medicamento(
        db, id_prescricao_medicamento
    )
    registro.id_prescricao = dados.id_prescricao
    registro.id_medicamento = dados.id_medicamento
    registro.dosagem = dados.dosagem
    registro.frequencia = dados.frequencia
    registro.duracao = dados.duracao
    registro.quantidade = dados.quantidade
    registro.instrucoes = dados.instrucoes
    return salvar_alteracao(db, registro)


def excluir_prescricao_medicamento(
    db: Session, id_prescricao_medicamento: int
):
    registro = buscar_prescricao_medicamento(
        db, id_prescricao_medicamento
    )
    excluir_registro(db, registro)
    return {"mensagem": "Medicamento da prescrição excluído com sucesso"}


# =====================================================
# PEDIDOS DE EXAMES
# =====================================================

def listar_pedidos_exames(db: Session):
    return db.query(PedidoExame).all()


def buscar_pedido_exame(db: Session, id_pedido_exame: int):
    return obter_ou_404(
        db, PedidoExame, PedidoExame.id_pedido_exame,
        id_pedido_exame, "Pedido de exame não encontrado"
    )


def cadastrar_pedido_exame(db: Session, dados: PedidoExameCreate):
    novo = PedidoExame(
        id_atendimento=dados.id_atendimento,
        status=dados.status,
        observacoes=dados.observacoes,
    )
    return salvar_novo(db, novo)


def atualizar_pedido_exame(
    db: Session, id_pedido_exame: int, dados: PedidoExameCreate
):
    registro = buscar_pedido_exame(db, id_pedido_exame)
    registro.id_atendimento = dados.id_atendimento
    registro.status = dados.status
    registro.observacoes = dados.observacoes
    return salvar_alteracao(db, registro)


def excluir_pedido_exame(db: Session, id_pedido_exame: int):
    registro = buscar_pedido_exame(db, id_pedido_exame)
    excluir_registro(db, registro)
    return {"mensagem": "Pedido de exame excluído com sucesso"}


# =====================================================
# ITENS DOS PEDIDOS DE EXAMES
# =====================================================

def listar_pedido_exame_itens(db: Session):
    return db.query(PedidoExameItem).all()


def buscar_pedido_exame_item(db: Session, id_pedido_exame_item: int):
    return obter_ou_404(
        db,
        PedidoExameItem,
        PedidoExameItem.id_pedido_exame_item,
        id_pedido_exame_item,
        "Item do pedido de exame não encontrado",
    )


def cadastrar_pedido_exame_item(
    db: Session, dados: PedidoExameItemCreate
):
    novo = PedidoExameItem(
        id_pedido_exame=dados.id_pedido_exame,
        id_exame=dados.id_exame,
        observacoes=dados.observacoes,
    )
    return salvar_novo(db, novo)


def atualizar_pedido_exame_item(
    db: Session,
    id_pedido_exame_item: int,
    dados: PedidoExameItemCreate,
):
    registro = buscar_pedido_exame_item(db, id_pedido_exame_item)
    registro.id_pedido_exame = dados.id_pedido_exame
    registro.id_exame = dados.id_exame
    registro.observacoes = dados.observacoes
    return salvar_alteracao(db, registro)


def excluir_pedido_exame_item(db: Session, id_pedido_exame_item: int):
    registro = buscar_pedido_exame_item(db, id_pedido_exame_item)
    excluir_registro(db, registro)
    return {"mensagem": "Item do pedido de exame excluído com sucesso"}
