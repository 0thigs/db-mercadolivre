from typing import List, Optional
from bson import ObjectId
from modules.users.models import Usuario
from modules.users.repository import UsuarioRepository


class UsuarioService:
    def __init__(self):
        self.repository = UsuarioRepository()
    
    def criar_usuario(self, usuario: Usuario) -> ObjectId:
        return self.repository.create(usuario)
    
    def buscar_usuario_por_id(self, usuario_id: str) -> Optional[Usuario]:
        return self.repository.find_by_id(usuario_id)
    
    def buscar_usuarios_por_nome(self, nome: str) -> List[Usuario]:
        return self.repository.find_by_nome(nome)
    
    def buscar_usuarios_por_cpf(self, cpf: str) -> List[Usuario]:
        return self.repository.find_by_cpf(cpf)
    
    def listar_todos_usuarios(self) -> List[Usuario]:
        return self.repository.find_all()
    
    def atualizar_usuario(self, usuario_id: str, dados: dict) -> bool:
        return self.repository.update(usuario_id, dados)
    
    def deletar_usuario(self, usuario_id: str) -> bool:
        return self.repository.delete(usuario_id)
    
    def adicionar_favorito(self, usuario_id: str, produto_id: ObjectId) -> bool:
        return self.repository.adicionar_favorito(usuario_id, produto_id)
    
    def remover_favorito(self, usuario_id: str, produto_id: ObjectId) -> bool:
        return self.repository.remover_favorito(usuario_id, produto_id)
    
    def listar_favoritos(self, usuario_id: str) -> List[ObjectId]:
        return self.repository.listar_favoritos(usuario_id) 