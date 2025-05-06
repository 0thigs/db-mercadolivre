from modules.database.redis_db import RedisConnection
from modules.database.mongo_db import MongoDBConnection


class MongoRedisController:
    def __init__(self):
        self.redis = RedisConnection.get_client()
        self.mongo = MongoDBConnection()

    def executar_transferencia(self):
        print("\n===== TRANSFERÊNCIA MONGO <-> REDIS =====")
        print("1. Transferir do MongoDB para o Redis")
        print("2. Transferir do Redis para o MongoDB")
        opcao = input("\nDigite a opção desejada: ")

        if opcao == "1":
            print("\nTransferindo dados do MongoDB para o Redis...")
            colecao = input("Nome da coleção MongoDB: ")
            chave_prefixo = input("Prefixo da chave Redis: ")

            colecao_mongo = self.mongo.get_collection(colecao)
            documentos = colecao_mongo.find()

            contador = 0
            for doc in documentos:
                doc_id = str(doc["_id"])
                if "nome" in doc:
                    self.redis.hset(f"{chave_prefixo}:{doc_id}", "nome", doc["nome"])
                    contador += 1
                if "cpf" in doc:
                    self.redis.hset(f"{chave_prefixo}:{doc_id}", "cpf", doc["cpf"])

            print(f"Dados transferidos com sucesso! {contador} documentos processados.")

        elif opcao == "2":
            print("\nTransferindo dados do Redis para o MongoDB...")
            chave_padrao = input("Padrão de chave Redis (ex: usuario:*): ")
            colecao = input("Nome da coleção MongoDB: ")
            chaves = self.redis.keys(chave_padrao)

            colecao_mongo = self.mongo.get_collection(colecao)
            contador = 0

            for chave in chaves:
                dados = self.redis.hgetall(chave)
                if dados:
                    colecao_mongo.insert_one(dados)
                    contador += 1

            print(f"Dados transferidos com sucesso! {contador} documentos processados.")

        else:
            print("Opção inválida.")
