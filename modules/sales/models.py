from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from bson import ObjectId
from decimal import Decimal
from datetime import datetime


class StatusPedido(Enum):
    AGUARDANDO_PAGAMENTO = "aguardando_pagamento"
    PAGAMENTO_APROVADO = "pagamento_aprovado"
    EM_SEPARACAO = "em_separacao"
    ENVIADO = "enviado"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"


@dataclass
class ItemPedido:
    produto_id: ObjectId
    nome_produto: str
    quantidade: int
    preco_unitario: Decimal
    preco_total: Optional[Decimal] = None

    def __post_init__(self):
        if self.preco_total is None:
            self.preco_total = self.preco_unitario * self.quantidade


@dataclass
class Pagamento:
    metodo: str
    status: str
    valor: Decimal
    detalhes: Dict[str, Any]
    data: str
    id: Optional[ObjectId] = None


@dataclass
class Pedido:
    usuario_id: ObjectId
    itens: List[ItemPedido]
    endereco_entrega: Dict[str, str]
    status: StatusPedido
    pagamento: Optional[Pagamento]
    data_criacao: Optional[str] = None
    data_atualizacao: Optional[str] = None
    valor_total: Optional[Decimal] = None
    frete: Decimal = Decimal("0.00")
    id: Optional[ObjectId] = None

    def __post_init__(self):
        if self.valor_total is None:
            total_itens = sum(item.preco_total for item in self.itens)
            self.valor_total = total_itens + self.frete
