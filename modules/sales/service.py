from typing import List, Optional, Dict
from bson import ObjectId
from decimal import Decimal
from modules.sales.models import Pedido, ItemPedido, Pagamento, StatusPedido
from modules.sales.repository import PedidoRepository
from modules.products.service import ProdutoService
from modules.users.service import UsuarioService


class PedidoService:
    def __init__(self):
        self.repository = PedidoRepository()
        self.produto_service = ProdutoService()
        self.usuario_service = UsuarioService()

    def criar_pedido(self, pedido: Pedido) -> ObjectId:
        for item in pedido.itens:
            produto = self.produto_service.buscar_produto_por_id(str(item.produto_id))
            if not produto:
                raise ValueError(f"Produto não encontrado: {item.produto_id}")

            if produto.estoque < item.quantidade:
                raise ValueError(
                    f"Estoque insuficiente para o produto {produto.nome}. Disponível: {produto.estoque}, Solicitado: {item.quantidade}"
                )

        return self.repository.create(pedido)

    def criar_pedido_por_carrinho(
        self,
        usuario_id: str,
        itens_carrinho: List[Dict],
        endereco_entrega: Dict[str, str],
        frete: Decimal = Decimal("0.00"),
    ) -> ObjectId:
        usuario = self.usuario_service.buscar_usuario_por_id(usuario_id)
        if not usuario:
            raise ValueError(f"Usuário não encontrado: {usuario_id}")

        itens_pedido = []
        for item_carrinho in itens_carrinho:
            produto_id = item_carrinho["produto_id"]
            quantidade = item_carrinho["quantidade"]

            produto = self.produto_service.buscar_produto_por_id(str(produto_id))
            if not produto:
                raise ValueError(f"Produto não encontrado: {produto_id}")

            if produto.estoque < quantidade:
                raise ValueError(
                    f"Estoque insuficiente para o produto {produto.nome}. Disponível: {produto.estoque}, Solicitado: {quantidade}"
                )

            item_pedido = ItemPedido(
                produto_id=ObjectId(produto_id),
                nome_produto=produto.nome,
                quantidade=quantidade,
                preco_unitario=produto.preco,
            )
            itens_pedido.append(item_pedido)

        pedido = Pedido(
            usuario_id=ObjectId(usuario_id),
            itens=itens_pedido,
            endereco_entrega=endereco_entrega,
            frete=frete,
        )

        return self.repository.create(pedido)

    def buscar_pedido_por_id(self, pedido_id: str) -> Optional[Pedido]:
        return self.repository.find_by_id(pedido_id)

    def buscar_pedidos_por_usuario(self, usuario_id: str) -> List[Pedido]:
        return self.repository.find_by_usuario(usuario_id)

    def buscar_pedidos_por_status(self, status: StatusPedido) -> List[Pedido]:
        return self.repository.find_by_status(status)

    def atualizar_status_pedido(self, pedido_id: str, status: StatusPedido) -> bool:
        return self.repository.update_status(pedido_id, status)

    def registrar_pagamento(
        self,
        pedido_id: str,
        metodo: str,
        valor: Decimal,
        detalhes: Dict[str, str] = None,
    ) -> bool:
        pedido = self.repository.find_by_id(pedido_id)
        if not pedido:
            raise ValueError(f"Pedido não encontrado: {pedido_id}")

        if pedido.status != StatusPedido.AGUARDANDO_PAGAMENTO:
            raise ValueError(
                f"Pedido não está aguardando pagamento. Status atual: {pedido.status.value}"
            )

        if valor < pedido.total:
            raise ValueError(
                f"Valor do pagamento inferior ao total do pedido. Pagamento: {valor}, Total: {pedido.total}"
            )

        pagamento = Pagamento(
            metodo=metodo,
            status="aprovado",
            valor=valor,
            detalhes=detalhes or {},
        )

        return self.repository.update_pagamento(pedido_id, pagamento)

    def cancelar_pedido(self, pedido_id: str) -> bool:
        pedido = self.repository.find_by_id(pedido_id)
        if not pedido:
            raise ValueError(f"Pedido não encontrado: {pedido_id}")

        if pedido.status in [
            StatusPedido.ENVIADO,
            StatusPedido.ENTREGUE,
            StatusPedido.CANCELADO,
        ]:
            raise ValueError(
                f"Pedido não pode ser cancelado. Status atual: {pedido.status.value}"
            )

        return self.repository.update_status(pedido_id, StatusPedido.CANCELADO)

    def buscar_todos_pedidos(self):
        documentos = self.repository.find_all()
        return documentos
