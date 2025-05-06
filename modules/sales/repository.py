from typing import List, Optional, Dict, Any
from bson import ObjectId
from decimal import Decimal
from datetime import datetime
from modules.sales.models import Pedido, ItemPedido, Pagamento, StatusPedido
from modules.database.mongo_db import MongoDBConnection
from modules.products.repository import ProdutoRepository


class PedidoRepository:
    def __init__(self):
        self.mongo = MongoDBConnection()
        self.collection = self.mongo.get_collection("pedido")
        self.produto_repository = ProdutoRepository()

    def create(self, pedido: Pedido) -> ObjectId:
        pedido.data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pedido.data_atualizacao = pedido.data_criacao

        documento = self._pedido_to_documento(pedido)

        result = self.collection.insert_one(documento)

        for item in pedido.itens:
            self.produto_repository.atualizar_estoque(
                str(item.produto_id), -item.quantidade
            )

        return result.inserted_id

    def find_by_id(self, pedido_id: str) -> Optional[Pedido]:
        documento = self.collection.find_one({"_id": ObjectId(pedido_id)})
        if documento:
            return self._documento_to_pedido(documento)
        return None

    def find_by_usuario(self, usuario_id: str) -> List[Pedido]:
        documentos = self.collection.find({"usuario_id": ObjectId(usuario_id)}).sort(
            "data_criacao", -1
        )
        return [self._documento_to_pedido(doc) for doc in documentos]

    def find_by_status(self, status: StatusPedido) -> List[Pedido]:
        documentos = self.collection.find({"status": status.value}).sort(
            "data_criacao", -1
        )
        return [self._documento_to_pedido(doc) for doc in documentos]

    def update_status(self, pedido_id: str, status: StatusPedido) -> bool:
        data_atualizacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        result = self.collection.update_one(
            {"_id": ObjectId(pedido_id)},
            {"$set": {"status": status.value, "data_atualizacao": data_atualizacao}},
        )

        if status == StatusPedido.CANCELADO:
            pedido = self.find_by_id(pedido_id)
            if pedido:
                for item in pedido.itens:
                    self.produto_repository.atualizar_estoque(
                        str(item.produto_id), item.quantidade
                    )

        return result.modified_count > 0

    def update_pagamento(self, pedido_id: str, pagamento: Pagamento) -> bool:
        data_atualizacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pagamento.data = data_atualizacao

        documento_pagamento = {
            "metodo": pagamento.metodo,
            "status": pagamento.status,
            "valor": float(pagamento.valor),
            "detalhes": pagamento.detalhes,
            "data": pagamento.data,
        }

        result = self.collection.update_one(
            {"_id": ObjectId(pedido_id)},
            {
                "$set": {
                    "pagamento": documento_pagamento,
                    "data_atualizacao": data_atualizacao,
                }
            },
        )
        if pagamento.status == "aprovado":
            self.update_status(pedido_id, StatusPedido.PAGAMENTO_APROVADO)

        return result.modified_count > 0

    def _pedido_to_documento(self, pedido: Pedido) -> Dict[str, Any]:
        itens_documento = []
        for item in pedido.itens:
            itens_documento.append(
                {
                    "produto_id": item.produto_id,
                    "nome_produto": item.nome_produto,
                    "quantidade": item.quantidade,
                    "preco_unitario": float(item.preco_unitario),
                    "total_item": float(item.total_item),
                }
            )

        pagamento_documento = None
        if pedido.pagamento:
            pagamento_documento = {
                "metodo": pedido.pagamento.metodo,
                "status": pedido.pagamento.status,
                "valor": float(pedido.pagamento.valor),
                "detalhes": pedido.pagamento.detalhes,
                "data": pedido.pagamento.data,
            }

        documento = {
            "usuario_id": pedido.usuario_id,
            "itens": itens_documento,
            "endereco_entrega": pedido.endereco_entrega,
            "status": pedido.status.value,
            "pagamento": pagamento_documento,
            "data_criacao": pedido.data_criacao,
            "data_atualizacao": pedido.data_atualizacao,
            "total": float(pedido.total),
            "frete": float(pedido.frete),
        }

        return documento

    def _documento_to_pedido(self, documento: Dict[str, Any]) -> Pedido:
        itens = []
        for item_doc in documento["itens"]:
            item = ItemPedido(
                produto_id=item_doc["produto_id"],
                nome_produto=item_doc["nome_produto"],
                quantidade=item_doc["quantidade"],
                preco_unitario=Decimal(str(item_doc["preco_unitario"])),
                total_item=Decimal(str(item_doc["total_item"])),
            )
            itens.append(item)

        pagamento = None
        if documento.get("pagamento"):
            pagamento_doc = documento["pagamento"]
            pagamento = Pagamento(
                metodo=pagamento_doc["metodo"],
                status=pagamento_doc["status"],
                valor=Decimal(str(pagamento_doc["valor"])),
                detalhes=pagamento_doc.get("detalhes", {}),
                data=pagamento_doc.get("data", ""),
            )

        pedido = Pedido(
            id=documento["_id"],
            usuario_id=documento["usuario_id"],
            itens=itens,
            endereco_entrega=documento["endereco_entrega"],
            status=StatusPedido(documento["status"]),
            pagamento=pagamento,
            data_criacao=documento.get("data_criacao", ""),
            data_atualizacao=documento.get("data_atualizacao", ""),
            total=Decimal(str(documento["total"])),
            frete=Decimal(str(documento["frete"])),
        )

        return pedido

    def find_all(self):
        documentos = self.collection.find().sort("data_criacao", -1)
        pedidos = [self._documento_to_pedido(doc) for doc in documentos]
        return pedidos
