from typing import List, Optional
from bson import ObjectId
from modules.sellers.models import Vendedor
from modules.sellers.repository import VendedorRepository


class VendedorService:
    def __init__(self):
        self.repository = VendedorRepository()
    
    def criar_vendedor(self, vendedor: Vendedor) -> ObjectId:
        return self.repository.create(vendedor)
    
    def buscar_vendedor_por_id(self, vendedor_id: str) -> Optional[Vendedor]:
        return self.repository.find_by_id(vendedor_id)
    
    def buscar_vendedores_por_nome(self, nome: str) -> List[Vendedor]:
        return self.repository.find_by_nome(nome)
    
    def buscar_vendedores_por_cnpj(self, cnpj: str) -> List[Vendedor]:
        return self.repository.find_by_cnpj(cnpj)
    
    def listar_todos_vendedores(self) -> List[Vendedor]:
        return self.repository.find_all()
    
    def atualizar_vendedor(self, vendedor_id: str, dados: dict) -> bool:
        return self.repository.update(vendedor_id, dados)
    
    def deletar_vendedor(self, vendedor_id: str) -> bool:
        return self.repository.delete(vendedor_id)
    
    def adicionar_produto(self, vendedor_id: str, produto_id: ObjectId) -> bool:
        return self.repository.adicionar_produto(vendedor_id, produto_id) 