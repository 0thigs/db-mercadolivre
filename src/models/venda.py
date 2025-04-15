from src.database.connection import get_database
from bson.objectid import ObjectId
from datetime import datetime


class Venda:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.venda

    def create(
        self,
        usuario_id,
        vendedor_id,
        produtos,
        total,
        forma_pagamento,
        endereco_entrega,
    ):
        documento = {
            "usuario_id": usuario_id,
            "vendedor_id": vendedor_id,
            "produtos": produtos,
            "total": total,
            "forma_pagamento": forma_pagamento,
            "endereco_entrega": endereco_entrega,
            "data": datetime.now(),
            "status": "pendente",
        }
        return self.collection.insert_one(documento)

    def read(self, venda_id=None, usuario_id=None, vendedor_id=None, status=None):
        filtro = {}
        if venda_id:
            filtro["_id"] = ObjectId(venda_id)
        if usuario_id:
            filtro["usuario_id"] = usuario_id
        if vendedor_id:
            filtro["vendedor_id"] = vendedor_id
        if status:
            filtro["status"] = status

        if filtro:
            return self.collection.find(filtro)
        return self.collection.find().sort("data", -1)

    def update(self, venda_id, dados_novos):
        return self.collection.update_one(
            {"_id": ObjectId(venda_id)}, {"$set": dados_novos}
        )

    def delete(self, venda_id):
        return self.collection.delete_one({"_id": ObjectId(venda_id)})
