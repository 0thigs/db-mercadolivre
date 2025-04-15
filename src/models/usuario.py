from src.database.connection import get_database
from bson.objectid import ObjectId


class Usuario:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.usuario

    def create(self, nome, sobrenome, cpf, enderecos):
        documento = {
            "nome": nome,
            "sobrenome": sobrenome,
            "cpf": cpf,
            "end": enderecos,
            "favoritos": [],
        }
        return self.collection.insert_one(documento)

    def read(self, usuario_id=None, nome=None, cpf=None):
        if usuario_id:
            return self.collection.find({"_id": ObjectId(usuario_id)})
        if nome:
            return self.collection.find({"nome": nome})
        if cpf:
            return self.collection.find({"cpf": cpf})
        return self.collection.find().sort("nome")

    def update(self, identificador, dados_novos, id_tipo="_id"):
        filtro = {}
        if id_tipo == "_id" or id_tipo == "usuario_id":
            try:
                filtro["_id"] = ObjectId(identificador)
            except Exception as e:
                print(f"Erro ao converter ID para ObjectId: {e}")
                return None
        else:
            filtro[id_tipo] = identificador

        if not filtro:
            print("Filtro de atualização inválido.")
            return None

        return self.collection.update_one(filtro, {"$set": dados_novos})

    def delete(self, identificador, id_tipo="_id"):
        if id_tipo == "_id":
            return self.collection.delete_one({"_id": ObjectId(identificador)})
        return self.collection.delete_one({id_tipo: identificador})

    def adicionar_favorito(self, usuario_id, produto_id):
        return self.collection.update_one(
            {"_id": ObjectId(usuario_id)},
            {"$addToSet": {"favoritos": produto_id}},
        )

    def remover_favorito(self, usuario_id, produto_id):
        return self.collection.update_one(
            {"_id": ObjectId(usuario_id)}, {"$pull": {"favoritos": produto_id}}
        )

    def listar_favoritos(self, usuario_id):
        usuario = self.collection.find_one({"_id": ObjectId(usuario_id)})
        if usuario and "favoritos" in usuario:
            return usuario["favoritos"]
        return []
