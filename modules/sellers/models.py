from dataclasses import dataclass, field
from typing import List, Optional
from bson import ObjectId
from modules.users.models import Endereco


@dataclass
class Vendedor:
    nome: str
    sobrenome: str
    cpf: str
    cnpj: str
    enderecos: List[Endereco]
    produtos: List[ObjectId] = field(default_factory=list)
    user_id: Optional[ObjectId] = None
    id: Optional[ObjectId] = None 