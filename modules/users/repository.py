from typing import List, Dict, Optional, Any
from bson import ObjectId
from modules.users.models import Usuario, Endereco
from modules.database.mongo_db import MongoDBConnection


class UsuarioRepository:
    def __init__(self):
        self.mongo = MongoDBConnection()
        self.collection = self.mongo.get_collection("usuario")

    def create(self, usuario: Usuario) -> ObjectId:
        usuario_dict = {
            "nome": usuario.nome,
            "sobrenome": usuario.sobrenome,
            "cpf": usuario.cpf,
            "end": [self._endereco_to_dict(e) for e in usuario.enderecos],
            "favoritos": [str(f) for f in usuario.favoritos]
            if usuario.favoritos
            else [],
        }

        result = self.collection.insert_one(usuario_dict)
        return result.inserted_id

    def find_by_id(self, usuario_id: str) -> Optional[Usuario]:
        documento = self.collection.find_one({"_id": ObjectId(usuario_id)})
        return self._documento_to_entity(documento) if documento else None

    def find_by_nome(self, nome: str) -> List[Usuario]:
        documentos = self.collection.find({"nome": {"$regex": nome, "$options": "i"}})
        return [self._documento_to_entity(doc) for doc in documentos]

    def find_by_cpf(self, cpf: str) -> List[Usuario]:
        documentos = self.collection.find({"cpf": cpf})
        return [self._documento_to_entity(doc) for doc in documentos]

    def find_all(self) -> List[Usuario]:
        documentos = self.collection.find()
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
            {"$addToSet": {"favoritos": str(produto_id)}},
        )
        return result.modified_count > 0

    def remover_favorito(self, usuario_id: str, produto_id: ObjectId) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(usuario_id)},
            {"$pull": {"favoritos": str(produto_id)}},
        )
        return result.modified_count > 0

    def listar_favoritos(self, usuario_id: str) -> List[ObjectId]:
        documento = self.collection.find_one(
            {"_id": ObjectId(usuario_id)}, {"favoritos": 1}
        )
        return (
            [ObjectId(f) for f in documento.get("favoritos", [])] if documento else []
        )

    def _endereco_to_dict(self, endereco: Endereco) -> Dict[str, str]:
        return {
            "rua": endereco.rua,
            "num": endereco.num,
            "bairro": endereco.bairro,
            "cidade": endereco.cidade,
            "estado": endereco.estado,
            "cep": endereco.cep,
        }

    def _dict_to_endereco(self, endereco_dict):
        if isinstance(endereco_dict, str):
            try:
                import json

                endereco_dict = json.loads(endereco_dict)
            except:
                print(
                    f"Erro ao converter endereço de string para dict: {endereco_dict}"
                )
                from modules.users.models import Endereco

                return Endereco(
                    rua="Erro de conversão",
                    num="0",
                    bairro="Erro de conversão",
                    cidade="Erro de conversão",
                    estado="EE",
                    cep="00000-000",
                )

        from modules.users.models import Endereco

        if "numero" in endereco_dict and "num" not in endereco_dict:
            endereco_dict["num"] = endereco_dict["numero"]
        elif "num" in endereco_dict and "numero" not in endereco_dict:
            endereco_dict["numero"] = endereco_dict["num"]

        try:
            return Endereco(
                rua=endereco_dict["rua"],
                num=endereco_dict["num"],
                bairro=endereco_dict.get("bairro", ""),
                cidade=endereco_dict["cidade"],
                estado=endereco_dict["estado"],
                cep=endereco_dict["cep"],
            )
        except KeyError as e:
            print(
                f"Erro ao converter endereço. Campos disponíveis: {list(endereco_dict.keys())}"
            )
            raise e

    def _documento_to_entity(self, documento: Dict[str, Any]) -> Usuario:
        if "end" in documento:
            if isinstance(documento["end"], str):
                try:
                    import json

                    documento["end"] = json.loads(documento["end"])
                except Exception as e:
                    print(f"Erro ao converter campo 'end': {e}")
                    documento["end"] = []
            elif documento["end"] is None:
                documento["end"] = []
        else:
            documento["end"] = []

        return Usuario(
            id=documento["_id"],
            nome=documento["nome"],
            sobrenome=documento["sobrenome"],
            cpf=documento["cpf"],
            enderecos=[self._dict_to_endereco(e) for e in documento["end"]],
            favoritos=documento.get("favoritos", []),
        )
