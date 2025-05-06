from typing import List, Optional, Dict, Any
from bson import ObjectId
from modules.users.models import Usuario, Endereco
from modules.database.mongo_db import MongoDBConnection


class UsuarioRepository:
    def __init__(self):
        self.mongo = MongoDBConnection()
        self.collection = self.mongo.get_collection("usuario")

    def create(self, usuario: Usuario) -> ObjectId:
        documento = {
            "nome": usuario.nome,
            "sobrenome": usuario.sobrenome,
            "cpf": usuario.cpf,
            "end": [self._endereco_to_dict(e) for e in usuario.enderecos],
            "favoritos": usuario.favoritos,
        }
        result = self.collection.insert_one(documento)
        return result.inserted_id

    def find_by_id(self, usuario_id: str) -> Optional[Usuario]:
        documento = self.collection.find_one({"_id": ObjectId(usuario_id)})
        if documento:
            return self._documento_to_entity(documento)
        return None

    def find_by_nome(self, nome: str) -> List[Usuario]:
        documentos = self.collection.find({"nome": nome})
        return [self._documento_to_entity(doc) for doc in documentos]

    def find_by_cpf(self, cpf: str) -> List[Usuario]:
        documentos = self.collection.find({"cpf": cpf})
        return [self._documento_to_entity(doc) for doc in documentos]

    def find_all(self) -> List[Usuario]:
        documentos = self.collection.find().sort("nome")
        return [self._documento_to_entity(doc) for doc in documentos]

    def update(self, usuario_id: str, dados: dict) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(usuario_id)}, {"$set": dados}
        )
        return result.modified_count > 0

    def delete(self, usuario_id: str) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(usuario_id)})
        return result.deleted_count > 0

    def adicionar_favorito(self, usuario_id: str, produto_id: ObjectId) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(usuario_id)},
            {"$addToSet": {"favoritos": produto_id}},
        )
        return result.modified_count > 0

    def remover_favorito(self, usuario_id: str, produto_id: ObjectId) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(usuario_id)}, {"$pull": {"favoritos": produto_id}}
        )
        return result.modified_count > 0

    def listar_favoritos(self, usuario_id: str) -> List[ObjectId]:
        usuario = self.collection.find_one({"_id": ObjectId(usuario_id)})
        if usuario and "favoritos" in usuario:
            return usuario["favoritos"]
        return []

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

    def _documento_to_entity(self, documento: Dict[str, Any]) -> Usuario:
        return Usuario(
            id=documento["_id"],
            nome=documento["nome"],
            sobrenome=documento["sobrenome"],
            cpf=documento["cpf"],
            enderecos=[self._dict_to_endereco(e) for e in documento["end"]],
            favoritos=documento.get("favoritos", []),
        )
