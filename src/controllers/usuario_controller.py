from src.models.usuario import Usuario
from src.models.produto import Produto
from bson.objectid import ObjectId


class UsuarioController:
    MSG_USUARIO_NAO_ENCONTRADO = "❌ Usuário não encontrado!"
    MSG_PRODUTO_NAO_ENCONTRADO = "❌ Produto não encontrado!"
    MSG_OPCAO_INVALIDA = "❌ Opção inválida!"

    def __init__(self):
        self.usuario_model = Usuario()
        self.produto_model = Produto()

    def _obter_dados_endereco(self):
        return {
            "rua": input("Rua: "),
            "num": input("Num: "),
            "bairro": input("Bairro: "),
            "cidade": input("Cidade: "),
            "estado": input("Estado: "),
            "cep": input("CEP: "),
        }

    def _solicitar_novo_endereco(self):
        enderecos = []
        while True:
            endereco = self._obter_dados_endereco()
            enderecos.append(endereco)
            if input("Deseja cadastrar outro endereço (S/N)? ").upper() != "S":
                break
        return enderecos

    def _exibir_enderecos(self, enderecos):
        for i, endereco in enumerate(enderecos, 1):
            print(
                f"{i}. {endereco['rua']}, {endereco['num']} - {endereco['cidade']}/{endereco['estado']}"
            )

    def criar_usuario(self):
        print("\nInserindo um novo usuário")
        nome = input("Nome: ")
        sobrenome = input("Sobrenome: ")
        cpf = input("CPF: ")

        enderecos = self._solicitar_novo_endereco()
        resultado = self.usuario_model.create(nome, sobrenome, cpf, enderecos)
        print("✓ Usuário inserido com ID", resultado.inserted_id)

    def _buscar_usuario_por_id(self, usuario_id):
        cursor = self.usuario_model.read(usuario_id=usuario_id)
        usuarios = list(cursor)
        return usuarios[0] if usuarios else None

    def _listar_todos_usuarios(self):
        cursor = self.usuario_model.read()
        return list(cursor)

    def _exibir_detalhes_usuario(self, usuario):
        print(
            f"ID: {usuario['_id']}, Nome: {usuario['nome']} {usuario['sobrenome']}, CPF: {usuario['cpf']}"
        )

        if "favoritos" in usuario and usuario["favoritos"]:
            print("  Produtos favoritos:", len(usuario["favoritos"]))

        print(f"  Endereços: {len(usuario['end'])}")
        self._exibir_enderecos(usuario["end"])
        print("-" * 40)

    def ler_usuario(self):
        print("\nBuscar usuário:")
        print("1. Por ID")
        print("2. Listar todos")
        opcao = input("Digite a opção desejada: ")

        resultados = []
        if opcao == "1":
            usuario_id = input("ID do usuário: ")
            usuario = self._buscar_usuario_por_id(usuario_id)
            if usuario:
                resultados = [usuario]
        elif opcao == "2":
            resultados = self._listar_todos_usuarios()
        else:
            print(self.MSG_OPCAO_INVALIDA)
            return

        print("\nUsuários encontrados:")
        if not resultados:
            print("Nenhum usuário encontrado.")
            return

        for usuario in resultados:
            self._exibir_detalhes_usuario(usuario)

    def _obter_dados_atualizacao(self):
        return {
            "nome": input("Novo nome (deixe em branco para manter): "),
            "sobrenome": input("Novo sobrenome (deixe em branco para manter): "),
            "cpf": input("Novo CPF (deixe em branco para manter): "),
        }

    def _atualizar_enderecos(self, usuario):
        print("\nEndereços atuais:")
        self._exibir_enderecos(usuario["end"])

        print("\n1. Adicionar novo endereço")
        print("2. Remover endereço existente")
        print("3. Substituir todos os endereços")
        sub_opcao = input("Digite a opção desejada: ")

        if sub_opcao == "1":
            enderecos = usuario["end"].copy()
            enderecos.extend(self._solicitar_novo_endereco())
            return enderecos
        elif sub_opcao == "2":
            try:
                idx = int(input("Índice do endereço a remover: ")) - 1
                enderecos = usuario["end"].copy()
                if 0 <= idx < len(enderecos):
                    del enderecos[idx]
                    return enderecos
                print("Índice inválido")
            except ValueError:
                print("Entrada inválida. Por favor, insira um número.")
        elif sub_opcao == "3":
            return self._solicitar_novo_endereco()
        else:
            print(self.MSG_OPCAO_INVALIDA)
        return None

    def atualizar_usuario(self):
        print("\nAtualizar usuário")
        identificador = input("ID do usuário a atualizar: ")

        usuario_data = self._buscar_usuario_por_id(identificador)
        if not usuario_data:
            print(self.MSG_USUARIO_NAO_ENCONTRADO)
            return

        dados_novos = {}
        dados_atualizacao = self._obter_dados_atualizacao()
        dados_novos.update({k: v for k, v in dados_atualizacao.items() if v})

        if input("Deseja atualizar endereços? (S/N): ").upper() == "S":
            enderecos = self._atualizar_enderecos(usuario_data)
            if enderecos is not None:
                dados_novos["end"] = enderecos

        if dados_novos:
            resultado = self.usuario_model.update(
                identificador, dados_novos, "usuario_id"
            )
            print(
                f"✓ Usuário atualizado: {resultado.modified_count} documento(s) modificado(s)"
            )
        else:
            print("Nenhuma atualização realizada")

    def deletar_usuario(self):
        print("\nDeletar usuário")
        identificador = input("ID do usuário a deletar: ")

        usuario_data = self._buscar_usuario_por_id(identificador)
        if not usuario_data:
            print(self.MSG_USUARIO_NAO_ENCONTRADO)
            return

        print(
            f"\nUsuário a ser deletado: {usuario_data['nome']} {usuario_data['sobrenome']} - CPF: {usuario_data['cpf']}"
        )
        if input("Tem certeza que deseja deletar este usuário? (S/N): ").upper() == "S":
            try:
                object_id = ObjectId(identificador)
                resultado = self.usuario_model.delete(object_id, "_id")
                print(
                    f"✓ Usuário deletado: {resultado.deleted_count} documento(s) removido(s)"
                )
            except Exception as e:
                print(f"❌ Erro ao deletar usuário: {str(e)}")
        else:
            print("Deleção cancelada.")

    def _exibir_favoritos(self, favoritos):
        if not favoritos:
            print("Nenhum produto favorito")
            return

        for i, produto_id_obj in enumerate(favoritos, 1):
            produto_id_str = str(produto_id_obj)
            produtos = list(self.produto_model.read(produto_id=produto_id_str))
            if produtos:
                produto = produtos[0]
                print(
                    f"{i}. {produto['nome']} - R$ {produto['preco']:.2f} (ID: {produto_id_str})"
                )
            else:
                print(f"{i}. Produto não encontrado (ID: {produto_id_str})")

    def gerenciar_favoritos(self):
        print("\n=== Gerenciar Favoritos ===")
        usuario_id = input("ID do usuário: ")

        usuario = self._buscar_usuario_por_id(usuario_id)
        if not usuario:
            print(self.MSG_USUARIO_NAO_ENCONTRADO)
            return

        favoritos = self.usuario_model.listar_favoritos(usuario_id)
        print("\nFavoritos atuais:")
        self._exibir_favoritos(favoritos)

        print("\n1. Adicionar favorito")
        print("2. Remover favorito")
        print("3. Voltar")
        opcao = input("Digite a opção desejada: ")

        if opcao == "1":
            produto_id = input("ID do produto a adicionar como favorito: ")
            produtos = list(self.produto_model.read(produto_id=produto_id))

            if not produtos:
                print(self.MSG_PRODUTO_NAO_ENCONTRADO)
                return

            produto = produtos[0]
            self.usuario_model.adicionar_favorito(usuario_id, produto["_id"])
            print(f"✓ Produto '{produto['nome']}' adicionado aos favoritos!")

        elif opcao == "2":
            if not favoritos:
                print("❌ Nenhum favorito para remover!")
                return
            try:
                idx = int(input("Número do favorito a remover: ")) - 1
                if 0 <= idx < len(favoritos):
                    self.usuario_model.remover_favorito(usuario_id, favoritos[idx])
                    print("✓ Produto removido dos favoritos!")
                else:
                    print("❌ Número inválido!")
            except ValueError:
                print("❌ Por favor, digite um número válido!")

        elif opcao == "3":
            return
        else:
            print(self.MSG_OPCAO_INVALIDA)
