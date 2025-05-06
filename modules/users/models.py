from dataclasses import dataclass, field
from typing import List, Optional
from bson import ObjectId


@dataclass
class Endereco:
    rua: str
    num: str
    bairro: str
    cidade: str
    estado: str
    cep: str


@dataclass
class Usuario:
    nome: str
    sobrenome: str
    cpf: str
    enderecos: List[Endereco]
    favoritos: List[ObjectId] = field(default_factory=list)
    id: Optional[ObjectId] = None
