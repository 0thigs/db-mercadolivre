from typing import List, Optional, Dict, Any
from bson import ObjectId
from decimal import Decimal
from modules.products.models import Produto
from modules.database.mongo_db import MongoDBConnection


class ProdutoRepository:
    def __init__(self):
        self.mongo = MongoDBConnection()
        self.collection = self.mongo.get_collection("produto")

    def create(self, produto: Produto) -> ObjectId:
        documento = {
            "nome": produto.nome,
            "descricao": produto.descricao,
            "preco": float(produto.preco),
            "estoque": produto.estoque,
            "vendedor_id": produto.vendedor_id,
            "ativo": produto.ativo,
        }
        result = self.collection.insert_one(documento)
        return result.inserted_id

    def find_by_id(self, produto_id: str) -> Optional[Produto]:
        documento = self.collection.find_one({"_id": ObjectId(produto_id)})
        if documento:
            return self._documento_to_entity(documento)
        return None

    def find_by_nome(self, nome: str) -> List[Produto]:
        documentos = self.collection.find({"nome": {"$regex": nome, "$options": "i"}})
        return [self._documento_to_entity(doc) for doc in documentos]

    def find_by_vendedor(self, vendedor_id: str) -> List[Produto]:
        documentos = self.collection.find({"vendedor_id": ObjectId(vendedor_id)})
        return [self._documento_to_entity(doc) for doc in documentos]

    def find_all(self):
        documentos = self.collection.find()
        produtos = []
        for doc in documentos:
            print(f"Documento encontrado: {doc['_id']} - {doc.get('nome', 'Sem nome')}")
            try:
                produto = self._documento_to_entity(doc)
                produtos.append(produto)
            except Exception as e:
                print(f"Erro ao converter documento: {e}")

        print(f"Total de produtos encontrados: {len(produtos)}")
        return produtos

    def update(self, produto_id: str, dados: dict) -> bool:
        if "preco" in dados and isinstance(dados["preco"], Decimal):
            dados["preco"] = float(dados["preco"])

        result = self.collection.update_one(
            {"_id": ObjectId(produto_id)}, {"$set": dados}
        )
        return result.modified_count > 0

    def delete(self, produto_id: str) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(produto_id)})
        return result.deleted_count > 0

    def atualizar_estoque(self, produto_id: str, quantidade: int) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(produto_id)}, {"$inc": {"estoque": quantidade}}
        )
        return result.modified_count > 0

    def _documento_to_entity(self, documento: Dict[str, Any]) -> Produto:
        try:
            campos_obrigatorios = ["nome", "descricao", "preco", "vendedor_id"]
            for campo in campos_obrigatorios:
                if campo not in documento:
                    print(
                        f"Documento ID {documento['_id']} não possui o campo obrigatório: {campo}"
                    )
                    raise KeyError(
                        f"Campo obrigatório '{campo}' não encontrado no documento"
                    )

            vendedor_id = documento["vendedor_id"]
            if isinstance(vendedor_id, str):
                vendedor_id = ObjectId(vendedor_id)

            estoque = 0
            if "quantidade" in documento:
                estoque = documento["quantidade"]
            elif "estoque" in documento:
                estoque = documento["estoque"]

            return Produto(
                id=documento["_id"],
                nome=documento["nome"],
                descricao=documento["descricao"],
                preco=Decimal(str(documento["preco"])),
                estoque=estoque,
                vendedor_id=vendedor_id,
                ativo=documento.get("ativo", True),
            )
        except Exception as e:
            print(f"Erro ao converter documento {documento['_id']}: {e}")
            print(f"Conteúdo do documento: {documento}")
            raise
