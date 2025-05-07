from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from modules.products.models import Produto, Avaliacao
from modules.products.repository import ProdutoRepository


class ProdutoService:
    def __init__(self):
        self.repository = ProdutoRepository()

    def criar_produto(self, produto: Produto) -> ObjectId:
        return self.repository.create(produto)

    def buscar_produto_por_id(self, produto_id: str) -> Optional[Produto]:
        return self.repository.find_by_id(produto_id)

    def buscar_produtos_por_nome(self, nome: str) -> List[Produto]:
        return self.repository.find_by_nome(nome)

    def buscar_produtos_por_categoria(self, categoria: str) -> List[Produto]:
        return self.repository.find_by_categoria(categoria)

    def buscar_produtos_por_vendedor(self, vendedor_id: str) -> List[Produto]:
        return self.repository.find_by_vendedor(vendedor_id)

    def listar_todos_produtos(self) -> List[Produto]:
        return self.repository.find_all()

    def atualizar_produto(self, produto_id: str, produto: Produto) -> bool:
        dados = {
            "nome": produto.nome,
            "descricao": produto.descricao,
            "preco": produto.preco,
            "estoque": produto.estoque,
            "vendedor_id": produto.vendedor_id,
            "ativo": produto.ativo,
        }
        return self.repository.update(produto_id, dados)

    def deletar_produto(self, produto_id: str) -> bool:
        return self.repository.delete(produto_id)

    def atualizar_estoque(self, produto_id: str, quantidade: int) -> bool:
        return self.repository.atualizar_estoque(produto_id, quantidade)

    def adicionar_avaliacao(
        self, produto_id: str, usuario_id: str, nota: int, comentario: str
    ) -> bool:
        if not 1 <= nota <= 5:
            return False

        avaliacao = Avaliacao(
            produto_id=ObjectId(produto_id),
            usuario_id=ObjectId(usuario_id),
            nota=nota,
            comentario=comentario,
            data=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        return self.repository.adicionar_avaliacao(produto_id, avaliacao)
