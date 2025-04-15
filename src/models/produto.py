from src.database.connection import get_database
from bson.objectid import ObjectId


class Produto:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.produto

    def create(self, nome, descricao, preco, quantidade, categorias, vendedor_id):
        documento = {
            "nome": nome,
            "descricao": descricao,
            "preco": preco,
            "quantidade": quantidade,
            "categorias": categorias,
            "vendedor_id": vendedor_id,
        }
        return self.collection.insert_one(documento)

    def read(self, produto_id=None, nome=None, categoria=None, vendedor_id=None):
        filtro = {}

        if produto_id:
            filtro["_id"] = ObjectId(produto_id)
        if nome:
            filtro["nome"] = {"$regex": nome, "$options": "i"}
        if categoria:
            filtro["categorias"] = categoria
        if vendedor_id:
            filtro["vendedor_id"] = vendedor_id

        if filtro:
            return self.collection.find(filtro)
        return self.collection.find().sort("nome")

    def update(self, produto_id, dados_novos):
        return self.collection.update_one(
            {"_id": ObjectId(produto_id)}, {"$set": dados_novos}
        )

    def delete(self, produto_id):
        return self.collection.delete_one({"_id": ObjectId(produto_id)})
