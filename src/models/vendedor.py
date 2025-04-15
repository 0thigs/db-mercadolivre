from src.database.connection import get_database


class Vendedor:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.vendedor

    def create(self, nome, sobrenome, cpf, cnpj, enderecos, produtos=None):
        documento = {
            "nome": nome,
            "sobrenome": sobrenome,
            "cpf": cpf,
            "cnpj": cnpj,
            "end": enderecos,
            "produtos": produtos or [],
        }
        return self.collection.insert_one(documento)

    def read(self, nome=None, cnpj=None):
        if nome:
            return self.collection.find({"nome": nome})
        if cnpj:
            return self.collection.find({"cnpj": cnpj})
        return self.collection.find().sort("nome")

    def update(self, identificador, dados_novos, id_tipo="nome"):
        return self.collection.update_one(
            {id_tipo: identificador}, {"$set": dados_novos}
        )

    def delete(self, identificador, id_tipo="nome"):
        return self.collection.delete_one({id_tipo: identificador})
