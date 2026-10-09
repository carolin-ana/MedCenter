"""
Classe genérica de serviço — fica entre as rotas e o banco de dados.

Conceitos de POO usados aqui:
- Classe genérica (reaproveitável para qualquer tabela)
- Encapsulamento: o atributo _db fica "protegido" dentro da classe;
  as rotas não precisam saber como o SQLAlchemy funciona por dentro
- Herança: cada módulo cria sua própria classe de serviço herdando
  desta aqui (ex: class FaturamentoService(BaseService[Faturamento]))
"""

from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    """
    Serviço genérico de CRUD. Toda classe de serviço de módulo deve
    herdar desta e definir o atributo "model" com o model do SQLAlchemy
    que ela representa.
    """

    model: Type[ModelType]

    def __init__(self, db: Session):
        self._db = db  # atributo "protegido": só as classes filhas mexem direto nele

    def listar(self) -> List[ModelType]:
        return self._db.query(self.model).all()

    def obter(self, valor_id, campo_id: str) -> Optional[ModelType]:
        coluna = getattr(self.model, campo_id)
        return self._db.query(self.model).filter(coluna == valor_id).first()

    def criar(self, dados: dict) -> ModelType:
        novo_registro = self.model(**dados)
        self._db.add(novo_registro)
        self._db.commit()
        self._db.refresh(novo_registro)
        return novo_registro

    def atualizar(self, objeto: ModelType, dados: dict) -> ModelType:
        for campo, valor in dados.items():
            setattr(objeto, campo, valor)
        self._db.commit()
        self._db.refresh(objeto)
        return objeto

    def excluir(self, objeto: ModelType) -> None:
        self._db.delete(objeto)
        self._db.commit()
