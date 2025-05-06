from typing import List, Optional, Dict, Any
from bson import ObjectId
from modules.sellers.models import Vendedor
from modules.users.models import Endereco
from modules.database.mongo_db import MongoDBConnection


class VendedorRepository:
    def __init__(self):
        self.mongo = MongoDBConnection()
        self.collection = self.mongo.get_collection("vendedor")

    def create(self, vendedor: Vendedor) -> ObjectId:
        documento = {
            "nome": vendedor.nome,
            "sobrenome": vendedor.sobrenome,
            "cpf": vendedor.cpf,
            "cnpj": vendedor.cnpj,
            "end": [self._endereco_to_dict(e) for e in vendedor.enderecos],
            "produtos": vendedor.produtos,
            "user_id": vendedor.user_id,
        }
        result = self.collection.insert_one(documento)
        return result.inserted_id

    def find_by_id(self, vendedor_id: str) -> Optional[Vendedor]:
        documento = self.collection.find_one({"_id": ObjectId(vendedor_id)})
        if documento:
            return self._documento_to_entity(documento)
        return None

    def find_by_nome(self, nome: str) -> List[Vendedor]:
        documentos = self.collection.find({"nome": nome})
        return [self._documento_to_entity(doc) for doc in documentos]

    def find_by_cnpj(self, cnpj: str) -> List[Vendedor]:
        documentos = self.collection.find({"cnpj": cnpj})
        return [self._documento_to_entity(doc) for doc in documentos]

    def find_all(self) -> List[Vendedor]:
        documentos = self.collection.find().sort("nome")
        return [self._documento_to_entity(doc) for doc in documentos]

    def update(self, vendedor_id: str, dados: dict) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(vendedor_id)}, {"$set": dados}
        )
        return result.modified_count > 0

    def delete(self, vendedor_id: str) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(vendedor_id)})
        return result.deleted_count > 0

    def adicionar_produto(self, vendedor_id: str, produto_id: ObjectId) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(vendedor_id)},
            {"$addToSet": {"produtos": produto_id}},
        )
        return result.modified_count > 0

    def _endereco_to_dict(self, endereco: Endereco) -> Dict[str, str]:
        return {
            "rua": endereco.rua,
            "num": endereco.num,
            "bairro": endereco.bairro,
            "cidade": endereco.cidade,
            "estado": endereco.estado,
            "cep": endereco.cep,
        }

    def _dict_to_endereco(self, endereco_dict: Dict[str, Any]) -> Endereco:
        return Endereco(
            rua=endereco_dict["rua"],
            num=endereco_dict["num"],
            bairro=endereco_dict["bairro"],
            cidade=endereco_dict["cidade"],
            estado=endereco_dict["estado"],
            cep=endereco_dict["cep"],
        )

    def _documento_to_entity(self, documento: Dict[str, Any]) -> Vendedor:
        return Vendedor(
            id=documento["_id"],
            nome=documento["nome"],
            sobrenome=documento["sobrenome"],
            cpf=documento["cpf"],
            cnpj=documento["cnpj"],
            enderecos=[self._dict_to_endereco(e) for e in documento["end"]],
            produtos=documento.get("produtos", []),
            user_id=documento.get("user_id"),
        ) 