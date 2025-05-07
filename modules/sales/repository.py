from typing import List, Optional, Dict, Any
from bson import ObjectId
from decimal import Decimal
from modules.sales.models import Pedido, ItemPedido, Pagamento, StatusPedido
from modules.database.mongo_db import MongoDBConnection
from modules.products.repository import ProdutoRepository
from datetime import datetime


class PedidoRepository:
    def __init__(self):
        self.mongo = MongoDBConnection()
        self.collection = self.mongo.get_collection("venda")
        self.produto_repository = ProdutoRepository()

    def create(self, pedido: Pedido) -> ObjectId:
        documento = {
            "usuario_id": pedido.usuario_id,
            "itens": [
                {
                    "produto_id": item.produto_id,
                    "nome_produto": item.nome_produto,
                    "quantidade": item.quantidade,
                    "preco_unitario": float(item.preco_unitario),
                }
                for item in pedido.itens
            ],
            "endereco_entrega": pedido.endereco_entrega,
            "frete": float(pedido.frete),
        }

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
        documentos = self.collection.find({"usuario_id": ObjectId(usuario_id)})
        return [self._documento_to_pedido(doc) for doc in documentos]

    def find_all(self) -> List[Pedido]:
        documentos = self.collection.find()
        return [self._documento_to_pedido(doc) for doc in documentos]

    def update_status(self, pedido_id: str, status: str) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(pedido_id)},
            {
                "$set": {
                    "status": status,
                    "data_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            },
        )
        return result.modified_count > 0

    def delete(self, pedido_id: str) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(pedido_id)})
        return result.deleted_count > 0

    def update_pagamento(self, pedido_id: str, pagamento: Pagamento) -> bool:
        pagamento_dict = {
            "metodo": pagamento.metodo,
            "status": pagamento.status,
            "valor": float(pagamento.valor),
            "detalhes": pagamento.detalhes,
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        result = self.collection.update_one(
            {"_id": ObjectId(pedido_id)},
            {
                "$set": {
                    "pagamento": pagamento_dict,
                    "status": StatusPedido.PAGAMENTO_APROVADO.value,
                    "data_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            },
        )
        return result.modified_count > 0

    def _documento_to_pedido(self, documento: Dict[str, Any]) -> Pedido:
        itens = []
        for item_doc in documento["itens"]:
            item = ItemPedido(
                produto_id=item_doc["produto_id"],
                nome_produto=item_doc["nome_produto"],
                quantidade=item_doc["quantidade"],
                preco_unitario=Decimal(str(item_doc["preco_unitario"])),
            )
            itens.append(item)

        status_str = documento.get("status", "pendente")
        status = StatusPedido(status_str) if status_str else StatusPedido.PENDENTE

        pagamento = None
        pagamento_doc = documento.get("pagamento")
        if pagamento_doc:
            pagamento = Pagamento(
                metodo=pagamento_doc.get("metodo", ""),
                status=pagamento_doc.get("status", ""),
                valor=Decimal(str(pagamento_doc.get("valor", 0))),
                detalhes=pagamento_doc.get("detalhes", {}),
                data=pagamento_doc.get("data", ""),
            )

        return Pedido(
            id=documento["_id"],
            usuario_id=documento["usuario_id"],
            itens=itens,
            endereco_entrega=documento["endereco_entrega"],
            frete=Decimal(str(documento["frete"])),
            status=status,
            data_criacao=documento.get("data_criacao", ""),
            data_atualizacao=documento.get("data_atualizacao", ""),
            pagamento=pagamento,
        )
