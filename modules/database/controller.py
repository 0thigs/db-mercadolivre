from modules.database.redis_db import RedisConnection
from modules.database.mongo_db import MongoDBConnection
import uuid
from bson import ObjectId


class MongoRedisController:
    def __init__(self):
        self.redis = RedisConnection.get_client()
        self.mongo = MongoDBConnection()
        self.current_token = None
        self.token_expiry = 60

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

    def redis_main_menu(self):
        while True:
            print("\n===== MENU REDIS =====")
            print("1. Fazer Login")
            print("2. Usuário")
            print("3. Produto")
            print("4. Enviar para o Mongo")
            print("5. Puxar do Mongo")
            print("6. Validar Sessão")
            print("V. Voltar")

            opcao = input("\nDigite a opção desejada: ")

            if opcao.upper() == "V":
                break

            if opcao == "1":
                self.fazer_login()
            elif opcao == "2":
                self.menu_usuario()
            elif opcao == "3":
                self.menu_produto()
            elif opcao == "4":
                self.enviar_para_mongo()
            elif opcao == "5":
                self.puxar_do_mongo()
            elif opcao == "6":
                self.validar_sessao()
            else:
                print("Opção inválida!")

    def fazer_login(self):
        print("\n===== LOGIN REDIS =====")
        nome = input("Digite seu nome: ")

        if nome:
            token = str(uuid.uuid4())

            self.redis.setex(f"session:{token}", self.token_expiry, nome)

            self.current_token = token
            print(f"\nLogin realizado com sucesso! Token: {token}")
            print(f"O token expirará em {self.token_expiry} segundos.")
        else:
            print("Nome não pode ser vazio!")

    def validate_token(self):
        if not self.current_token:
            print("\nVocê não está logado! Faça login primeiro.")
            return False

        session = self.redis.get(f"session:{self.current_token}")
        if not session:
            print("\nSessão expirada ou inválida! Faça login novamente.")
            self.current_token = None
            return False

        return True

    def validar_sessao(self):
        print("\n===== VALIDAR SESSÃO =====")

        if self.validate_token():
            ttl = self.redis.ttl(f"session:{self.current_token}")
            user = self.redis.get(f"session:{self.current_token}")

            print(f"Sessão válida para o usuário: {user}")
            print(f"Tempo restante: {ttl} segundos")
        else:
            print("Sessão inválida ou expirada!")

    def menu_usuario(self):
        if not self.validate_token():
            return

        while True:
            print("\n===== MENU USUÁRIO REDIS =====")
            print("1. Visualizar Usuários")
            print("2. Atualizar Usuário")
            print("V. Voltar")

            opcao = input("\nDigite a opção desejada: ")

            if opcao.upper() == "V":
                break

            if opcao == "1":
                self.visualizar_usuarios()
            elif opcao == "2":
                self.atualizar_usuario()
            else:
                print("Opção inválida!")

    def visualizar_usuarios(self):
        print("\n===== USUÁRIOS NO REDIS =====")

        chaves = self.redis.keys("usuario:*")

        if not chaves:
            print("Nenhum usuário encontrado no Redis!")
            print("Deseja buscar usuários do MongoDB? (S/N)")
            opcao = input().upper()

            if opcao == "S":
                self.buscar_usuarios_mongo()
                chaves = self.redis.keys("usuario:*")
                if not chaves:
                    print("Nenhum usuário encontrado!")
                    return
            else:
                return

        print(f"Total de usuários: {len(chaves)}")
        print("\nLista de Usuários:")

        for i, chave in enumerate(chaves, 1):
            dados = self.redis.hgetall(chave)
            id_usuario = chave.split(":")[-1]
            nome = dados.get("nome", "N/A")
            cpf = dados.get("cpf", "N/A")

            print(f"{i}. ID: {id_usuario}, Nome: {nome}, CPF: {cpf}")

    def buscar_usuarios_mongo(self):
        print("\nBuscando usuários do MongoDB...")

        try:
            colecao_usuarios = self.mongo.get_collection("usuario")
            colecoes_disponiveis = self.mongo.get_database().list_collection_names()
            print(f"Coleções disponíveis no banco: {', '.join(colecoes_disponiveis)}")

            usuarios = list(colecao_usuarios.find())

            if not usuarios:
                print("A coleção 'usuario' existe mas está vazia.")
                count = colecao_usuarios.count_documents({})
                print(f"Número de documentos na coleção 'usuario': {count}")
                if count > 0:
                    print("Tentando acessar o primeiro documento:")
                    primeiro = colecao_usuarios.find_one()
                    print(f"Primeiro documento: {primeiro}")
                return

            existing_redis_keys = self.redis.keys("usuario:*")
            existing_redis_ids = {chave.split(":")[-1] for chave in existing_redis_keys}

            mongo_ids = set()

            contador = 0
            for usuario in usuarios:
                usuario_id = str(usuario["_id"])
                mongo_ids.add(usuario_id)
                print(f"Processando usuário: {usuario_id}")

                chave_redis = f"usuario:{usuario_id}"
                self.redis.delete(chave_redis)

                for campo, valor in usuario.items():
                    if campo == "_id":
                        continue

                    if isinstance(valor, (dict, list)):
                        import json

                        valor_str = json.dumps(valor)
                    else:
                        valor_str = str(valor)

                    print(f"  - Campo: {campo}, Valor: {valor_str}")
                    self.redis.hset(chave_redis, campo, valor_str)

                self.redis.hdel(chave_redis, "email")

                contador += 1

            redis_ids_to_remove = existing_redis_ids - mongo_ids
            for redis_id in redis_ids_to_remove:
                print(
                    f"Removendo usuário do Redis que não existe mais no MongoDB: {redis_id}"
                )
                self.redis.delete(f"usuario:{redis_id}")

            print(f"Dados transferidos com sucesso! {contador} usuários processados.")
            print(
                f"{len(redis_ids_to_remove)} usuários removidos do Redis por não existirem mais no MongoDB."
            )

            chaves = self.redis.keys("usuario:*")
            if chaves:
                print(f"Chaves Redis criadas: {', '.join(chaves)}")

                if len(chaves) > 0:
                    primeira_chave = chaves[0]
                    dados = self.redis.hgetall(primeira_chave)
                    print(f"Dados na chave {primeira_chave}: {dados}")

        except Exception as e:
            print(f"Erro ao acessar a coleção 'usuario': {str(e)}")
            try:
                colecoes_disponiveis = self.mongo.get_database().list_collection_names()
                print(
                    f"Coleções disponíveis no banco: {', '.join(colecoes_disponiveis)}"
                )
            except Exception as e2:
                print(f"Erro ao listar coleções: {str(e2)}")

    def atualizar_usuario(self):
        print("\n===== ATUALIZAR USUÁRIO NO REDIS =====")
        chaves = self.redis.keys("usuario:*")

        if not chaves:
            print("Nenhum usuário encontrado no Redis!")
            print("Deseja buscar usuários do MongoDB? (S/N)")
            opcao = input().upper()

            if opcao == "S":
                self.buscar_usuarios_mongo()
                chaves = self.redis.keys("usuario:*")
                if not chaves:
                    print("Nenhum usuário encontrado!")
                    return
            else:
                return

        print(f"Total de usuários: {len(chaves)}")
        print("\nLista de Usuários:")

        usuarios_lista = []
        for chave in chaves:
            dados = self.redis.hgetall(chave)
            id_usuario = chave.split(":")[-1]
            nome = dados.get("nome", "N/A")
            cpf = dados.get("cpf", "N/A")

            usuarios_lista.append(
                {
                    "chave": chave,
                    "id": id_usuario,
                    "nome": nome,
                    "cpf": cpf,
                    "dados": dados,
                }
            )

        for i, usuario in enumerate(usuarios_lista, 1):
            print(
                f"{i}. Nome: {usuario['nome']}, CPF: {usuario['cpf']}, ID: {usuario['id']}"
            )

        try:
            indice = int(input("\nDigite o NÚMERO do usuário que deseja atualizar: "))

            if indice < 1 or indice > len(usuarios_lista):
                print(f"Índice inválido! Escolha de 1 a {len(usuarios_lista)}")
                return
            usuario_selecionado = usuarios_lista[indice - 1]
            chave = usuario_selecionado["chave"]

            print(
                f"\nUsuário selecionado: {usuario_selecionado['nome']} (ID: {usuario_selecionado['id']})"
            )

            dados_atuais = usuario_selecionado["dados"]
            print("\nDados atuais:")
            for campo, valor in dados_atuais.items():
                print(f"{campo}: {valor}")

            print(
                "\nDigite os novos dados (deixe em branco para manter o valor atual):"
            )

            campos = ["nome", "sobrenome", "cpf"]

            novos_dados = {}
            for campo in campos:
                valor_atual = dados_atuais.get(campo, "")
                novo_valor = input(f"{campo} [{valor_atual}]: ")

                if novo_valor:
                    novos_dados[campo] = novo_valor

            print("\nEndereço atual:")
            endereco_atual = {}
            try:
                import json

                if "enderecos" in dados_atuais:
                    enderecos = json.loads(dados_atuais.get("enderecos", "[]"))
                    if enderecos and len(enderecos) > 0:
                        endereco_atual = enderecos[0]
                        for campo, valor in endereco_atual.items():
                            print(f"{campo}: {valor}")
            except:
                print("Não foi possível ler o endereço atual.")

            print(
                "\nDigite os novos dados de endereço (deixe em branco para manter o valor atual):"
            )

            campos_endereco = ["rua", "num", "bairro", "cidade", "estado", "cep"]
            novo_endereco = {}

            for campo in campos_endereco:
                valor_atual = endereco_atual.get(campo, "")
                novo_valor = input(f"{campo} [{valor_atual}]: ")

                if novo_valor:
                    novo_endereco[campo] = novo_valor
                elif valor_atual:
                    novo_endereco[campo] = valor_atual

            if novo_endereco:
                import json

                enderecos = []
                try:
                    if "enderecos" in dados_atuais:
                        enderecos = json.loads(dados_atuais.get("enderecos", "[]"))
                        if len(enderecos) > 0:
                            enderecos[0] = novo_endereco
                        else:
                            enderecos.append(novo_endereco)
                    else:
                        enderecos.append(novo_endereco)
                except:
                    enderecos = [novo_endereco]

                novos_dados["enderecos"] = json.dumps(enderecos)

            if novos_dados:
                for campo, valor in novos_dados.items():
                    self.redis.hset(chave, campo, valor)

                print("\nUsuário atualizado com sucesso!")
            else:
                print("\nNenhum dado foi alterado.")

        except ValueError:
            print("Entrada inválida! Digite um número.")
        except Exception as e:
            print(f"Erro ao atualizar usuário: {str(e)}")

    def menu_produto(self):
        if not self.validate_token():
            return

        while True:
            print("\n===== MENU PRODUTO REDIS =====")
            print("1. Visualizar Produtos")
            print("2. Atualizar Produto")
            print("V. Voltar")

            opcao = input("\nDigite a opção desejada: ")

            if opcao.upper() == "V":
                break

            if opcao == "1":
                self.visualizar_produtos()
            elif opcao == "2":
                self.atualizar_produto()
            else:
                print("Opção inválida!")

    def visualizar_produtos(self):
        print("\n===== PRODUTOS NO REDIS =====")

        chaves = self.redis.keys("produto:*")

        if not chaves:
            print("Nenhum produto encontrado no Redis!")
            print("Deseja buscar produtos do MongoDB? (S/N)")
            opcao = input().upper()

            if opcao == "S":
                self.buscar_produtos_mongo()
                chaves = self.redis.keys("produto:*")
                if not chaves:
                    print("Nenhum produto encontrado!")
                    return
            else:
                return

        print(f"Total de produtos: {len(chaves)}")
        print("\nLista de Produtos:")

        for i, chave in enumerate(chaves, 1):
            dados = self.redis.hgetall(chave)
            id_produto = chave.split(":")[-1]
            nome = dados.get("nome", "N/A")
            preco = dados.get("preco", "N/A")
            estoque = dados.get("estoque", "N/A")

            print(
                f"{i}. ID: {id_produto}, Nome: {nome}, Preço: R$ {preco}, Estoque: {estoque}"
            )

    def buscar_produtos_mongo(self):
        print("\nBuscando produtos do MongoDB...")

        try:
            colecao_produtos = self.mongo.get_collection("produto")
            colecoes_disponiveis = self.mongo.get_database().list_collection_names()
            print(f"Coleções disponíveis no banco: {', '.join(colecoes_disponiveis)}")

            produtos = list(colecao_produtos.find())

            if not produtos:
                print("A coleção 'produto' existe mas está vazia.")
                count = colecao_produtos.count_documents({})
                print(f"Número de documentos na coleção 'produto': {count}")
                if count > 0:
                    print("Tentando acessar o primeiro documento:")
                    primeiro = colecao_produtos.find_one()
                    print(f"Primeiro documento: {primeiro}")
                return

            # Get existing Redis keys for products
            existing_redis_keys = self.redis.keys("produto:*")
            existing_redis_ids = {chave.split(":")[-1] for chave in existing_redis_keys}

            mongo_ids = set()

            contador = 0
            for produto in produtos:
                produto_id = str(produto["_id"])
                mongo_ids.add(produto_id)
                print(f"Processando produto: {produto_id}")

                chave_redis = f"produto:{produto_id}"
                self.redis.delete(chave_redis)

                for campo, valor in produto.items():
                    if campo == "_id":
                        continue

                    if isinstance(valor, (dict, list)):
                        import json

                        valor_str = json.dumps(valor)
                    else:
                        valor_str = str(valor)

                    print(f"  - Campo: {campo}, Valor: {valor_str}")
                    self.redis.hset(chave_redis, campo, valor_str)

                contador += 1

            redis_ids_to_remove = existing_redis_ids - mongo_ids
            for redis_id in redis_ids_to_remove:
                print(
                    f"Removendo produto do Redis que não existe mais no MongoDB: {redis_id}"
                )
                self.redis.delete(f"produto:{redis_id}")

            print(f"Dados transferidos com sucesso! {contador} produtos processados.")
            print(
                f"{len(redis_ids_to_remove)} produtos removidos do Redis por não existirem mais no MongoDB."
            )

            chaves = self.redis.keys("produto:*")
            if chaves:
                print(f"Chaves Redis criadas: {', '.join(chaves)}")

                if len(chaves) > 0:
                    primeira_chave = chaves[0]
                    dados = self.redis.hgetall(primeira_chave)
                    print(f"Dados na chave {primeira_chave}: {dados}")

        except Exception as e:
            print(f"Erro ao acessar a coleção 'produto': {str(e)}")
            try:
                colecoes_disponiveis = self.mongo.get_database().list_collection_names()
                print(
                    f"Coleções disponíveis no banco: {', '.join(colecoes_disponiveis)}"
                )
            except Exception as e2:
                print(f"Erro ao listar coleções: {str(e2)}")

    def atualizar_produto(self):
        print("\n===== ATUALIZAR PRODUTO NO REDIS =====")

        chaves = self.redis.keys("produto:*")

        if not chaves:
            print("Nenhum produto encontrado no Redis!")
            print("Deseja buscar produtos do MongoDB? (S/N)")
            opcao = input().upper()

            if opcao == "S":
                self.buscar_produtos_mongo()
                chaves = self.redis.keys("produto:*")
                if not chaves:
                    print("Nenhum produto encontrado!")
                    return
            else:
                return

        print(f"Total de produtos: {len(chaves)}")
        print("\nLista de Produtos:")

        produtos_lista = []
        for chave in chaves:
            dados = self.redis.hgetall(chave)
            id_produto = chave.split(":")[-1]
            nome = dados.get("nome", "N/A")
            preco = dados.get("preco", "N/A")
            estoque = dados.get("estoque", "N/A")

            produtos_lista.append(
                {
                    "chave": chave,
                    "id": id_produto,
                    "nome": nome,
                    "preco": preco,
                    "estoque": estoque,
                    "dados": dados,
                }
            )

        for i, produto in enumerate(produtos_lista, 1):
            print(
                f"{i}. Nome: {produto['nome']}, Preço: R$ {produto['preco']}, Estoque: {produto['estoque']}"
            )

        try:
            indice = int(input("\nDigite o NÚMERO do produto que deseja atualizar: "))

            if indice < 1 or indice > len(produtos_lista):
                print(f"Índice inválido! Escolha de 1 a {len(produtos_lista)}")
                return

            produto_selecionado = produtos_lista[indice - 1]
            chave = produto_selecionado["chave"]

            print(
                f"\nProduto selecionado: {produto_selecionado['nome']} (ID: {produto_selecionado['id']})"
            )

            dados_atuais = produto_selecionado["dados"]
            print("\nDados atuais:")
            for campo, valor in dados_atuais.items():
                print(f"{campo}: {valor}")

            print(
                "\nDigite os novos dados (deixe em branco para manter o valor atual):"
            )

            campos = ["nome", "descricao", "preco", "estoque", "vendedor_id", "ativo"]

            novos_dados = {}
            for campo in campos:
                valor_atual = dados_atuais.get(campo, "")

                if campo == "ativo":
                    print(f"\n{campo} [{valor_atual}] (Digite 'true' ou 'false'): ")
                    novo_valor = input()
                    if novo_valor.lower() in ["true", "false"]:
                        novos_dados[campo] = novo_valor.lower()
                elif campo in ["preco", "estoque"]:
                    try:
                        novo_valor = input(f"{campo} [{valor_atual}]: ")
                        if novo_valor:
                            # Validar se é um número
                            float(novo_valor) if campo == "preco" else int(novo_valor)
                            novos_dados[campo] = novo_valor
                    except ValueError:
                        print(f"Valor inválido para {campo}. Mantendo valor atual.")
                else:
                    novo_valor = input(f"{campo} [{valor_atual}]: ")
                    if novo_valor:
                        novos_dados[campo] = novo_valor

            if novos_dados:
                for campo, valor in novos_dados.items():
                    self.redis.hset(chave, campo, valor)

                print("\nProduto atualizado com sucesso!")
            else:
                print("\nNenhum dado foi alterado.")

        except ValueError:
            print("Entrada inválida! Digite um número.")
        except Exception as e:
            print(f"Erro ao atualizar produto: {str(e)}")

    def enviar_para_mongo(self):
        if not self.validate_token():
            return

        print("\n===== ENVIAR DADOS REDIS -> MONGODB =====")
        print("Escolha o tipo de dados a enviar:")
        print("1. Usuários")
        print("2. Produtos")
        print("3. Ambos")

        opcao = input("\nDigite a opção desejada: ")

        if opcao == "1":
            self.enviar_usuarios_para_mongo()
        elif opcao == "2":
            self.enviar_produtos_para_mongo()
        elif opcao == "3":
            self.enviar_usuarios_para_mongo()
            self.enviar_produtos_para_mongo()
        else:
            print("Opção inválida!")

    def enviar_usuarios_para_mongo(self):
        print("\nEnviando usuários do Redis para o MongoDB...")

        chaves = self.redis.keys("usuario:*")

        if not chaves:
            print("Nenhum usuário encontrado no Redis!")
            return

        try:
            colecao_usuarios = self.mongo.get_collection("usuario")
            contador = 0

            for chave in chaves:
                dados_originais = self.redis.hgetall(chave)
                if dados_originais:
                    dados = {}
                    for campo, valor in dados_originais.items():
                        try:
                            import json

                            if (
                                campo in ["end", "favoritos", "compras", "carrinho"]
                                or valor.startswith("[")
                                or valor.startswith("{")
                            ):
                                try:
                                    dados[campo] = json.loads(valor)
                                except:
                                    dados[campo] = valor
                            else:
                                dados[campo] = valor
                        except:
                            dados[campo] = valor

                    usuario_id = chave.split(":")[-1]

                    try:
                        object_id = ObjectId(usuario_id)
                        resultado = colecao_usuarios.update_one(
                            {"_id": object_id},
                            {"$set": dados},
                            upsert=True,
                        )
                    except Exception as e:
                        print(f"Erro ao atualizar usuário {usuario_id}: {str(e)}")
                        resultado = colecao_usuarios.update_one(
                            {"_id": usuario_id},
                            {"$set": dados},
                            upsert=True,
                        )

                    if resultado.modified_count > 0 or resultado.upserted_id:
                        contador += 1

            print(
                f"Dados enviados com sucesso! {contador} usuários atualizados/inseridos no MongoDB."
            )
        except Exception as e:
            print(f"Erro ao acessar a coleção 'usuario': {str(e)}")

    def enviar_produtos_para_mongo(self):
        print("\nEnviando produtos do Redis para o MongoDB...")

        chaves = self.redis.keys("produto:*")

        if not chaves:
            print("Nenhum produto encontrado no Redis!")
            return

        try:
            colecao_produtos = self.mongo.get_collection("produto")
            contador = 0

            for chave in chaves:
                dados_originais = self.redis.hgetall(chave)
                if dados_originais:
                    dados = {}
                    for campo, valor in dados_originais.items():
                        try:
                            import json

                            if campo in ["nome", "descricao", "preco", "estoque"]:
                                dados[campo] = valor
                            else:
                                dados[campo] = valor
                        except:
                            dados[campo] = valor

                    produto_id = chave.split(":")[-1]

                    try:
                        object_id = ObjectId(produto_id)
                        resultado = colecao_produtos.update_one(
                            {"_id": object_id},
                            {"$set": dados},
                            upsert=True,
                        )
                    except Exception as e:
                        print(f"Erro ao atualizar produto {produto_id}: {str(e)}")
                        resultado = colecao_produtos.update_one(
                            {"_id": produto_id},
                            {"$set": dados},
                            upsert=True,
                        )

                    if resultado.modified_count > 0 or resultado.upserted_id:
                        contador += 1

            print(
                f"Dados enviados com sucesso! {contador} produtos atualizados/inseridos no MongoDB."
            )
        except Exception as e:
            print(f"Erro ao acessar a coleção 'produto': {str(e)}")

    def puxar_do_mongo(self):
        if not self.validate_token():
            return

        print("\n===== PUXAR DADOS MONGODB -> REDIS =====")
        print("Escolha o tipo de dados a puxar:")
        print("1. Usuários")
        print("2. Produtos")
        print("3. Ambos")

        opcao = input("\nDigite a opção desejada: ")

        if opcao == "1":
            self.buscar_usuarios_mongo()
        elif opcao == "2":
            self.buscar_produtos_mongo()
        elif opcao == "3":
            self.buscar_usuarios_mongo()
            self.buscar_produtos_mongo()
        else:
            print("Opção inválida!")

    def mongo_to_redis(self):
        print("\nTransferindo dados do MongoDB para o Redis...")
        colecao = input("Nome da coleção MongoDB: ")
        chave_prefixo = input("Prefixo da chave Redis: ")

        colecao_mongo = self.mongo.get_collection(colecao)
        documentos = colecao_mongo.find()

        contador = 0
        for doc in documentos:
            doc_id = str(doc["_id"])
            for campo, valor in doc.items():
                if campo != "_id":
                    self.redis.hset(f"{chave_prefixo}:{doc_id}", campo, str(valor))

            contador += 1

        print(f"Dados transferidos com sucesso! {contador} documentos processados.")

    def redis_to_mongo(self):
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
