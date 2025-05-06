from dataclasses import dataclass, field
from typing import List, Optional, Dict
from bson import ObjectId
from decimal import Decimal


@dataclass
class Produto:
    nome: str
    descricao: str
    preco: Decimal
    estoque: int
    categorias: List[str]
    vendedor_id: ObjectId
    imagens: List[str] = field(default_factory=list)
    especificacoes: Dict[str, str] = field(default_factory=dict)
    ativo: bool = True
    id: Optional[ObjectId] = None


@dataclass
class Avaliacao:
    produto_id: ObjectId
    usuario_id: ObjectId
    nota: int
    comentario: str
    data: str
    id: Optional[ObjectId] = None
