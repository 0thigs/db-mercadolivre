from dataclasses import dataclass, field
from typing import List, Optional, Dict
from bson import ObjectId
from decimal import Decimal
from enum import Enum
from datetime import datetime


class StatusPedido(str, Enum):
    PENDENTE = "pendente"
    AGUARDANDO_PAGAMENTO = "aguardando_pagamento"
    PAGAMENTO_APROVADO = "pagamento_aprovado"
    EM_PREPARACAO = "em_preparacao"
    ENVIADO = "enviado"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"


@dataclass
class ItemPedido:
    produto_id: ObjectId
    nome_produto: str
    quantidade: int
    preco_unitario: Decimal

    @property
    def preco_total(self) -> Decimal:
        return self.quantidade * self.preco_unitario

    @property
    def total_item(self) -> Decimal:
        return self.preco_total


@dataclass
class Pagamento:
    metodo: str
    status: str
    valor: Decimal
    detalhes: Dict = field(default_factory=dict)
    data: str = ""


@dataclass
class Pedido:
    usuario_id: ObjectId
    itens: List[ItemPedido]
    endereco_entrega: Dict[str, str]
    frete: Decimal = Decimal("0.00")
    valor_total: Optional[Decimal] = None
    status: StatusPedido = StatusPedido.PENDENTE
    data_criacao: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    data_atualizacao: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    pagamento: Optional[Pagamento] = None
    id: Optional[ObjectId] = None

    def __post_init__(self):
        if self.valor_total is None:
            total_itens = sum(item.preco_total for item in self.itens)
            self.valor_total = total_itens + self.frete

    @property
    def total(self) -> Decimal:
        return self.valor_total
