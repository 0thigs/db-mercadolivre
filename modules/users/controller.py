from modules.users.models import Usuario, Endereco
from modules.users.service import UsuarioService
from typing import Optional


class UsuarioController:
    def __init__(self, usuario_service, vendedor_service=None):
        self.usuario_service = usuario_service
        self.vendedor_service = vendedor_service

    def criar_usuario(self):
        print("\n===== CRIAR USUÁRIO =====")
        nome = input("Nome: ")
        sobrenome = input("Sobrenome: ")
        cpf = input("CPF: ")

        print("\nEndereço:")
        rua = input("Rua: ")
        num = input("Número: ")
        bairro = input("Bairro: ")
        cidade = input("Cidade: ")
        estado = input("Estado: ")
        cep = input("CEP: ")

        endereco = Endereco(
            rua=rua, num=num, bairro=bairro, cidade=cidade, estado=estado, cep=cep
        )

        usuario = Usuario(nome=nome, sobrenome=sobrenome, cpf=cpf, enderecos=[endereco])

        usuario_id = self.usuario_service.criar_usuario(usuario)
        print(f"Usuário criado com ID: {usuario_id}")
        return usuario_id

    def ler_usuario(self):
        print("\n===== BUSCAR USUÁRIO =====")
        usuarios = self.usuario_service.listar_todos_usuarios()

        if usuarios:
            for usuario in usuarios:
                self._exibir_usuario(usuario)
                print("---")

            usuario_id = self._selecionar_usuario()
            if usuario_id:
                usuario = self.usuario_service.buscar_usuario_por_id(usuario_id)
                if usuario:
                    print("\nDetalhes completos do usuário selecionado:")
                    self._exibir_usuario(usuario)
        else:
            print("Nenhum usuário cadastrado.")

    def atualizar_usuario(self):
        print("\n===== ATUALIZAR USUÁRIO =====")
        usuario_id = self._selecionar_usuario()
        if not usuario_id:
            return False

        usuario = self.usuario_service.buscar_usuario_por_id(usuario_id)
        if not usuario:
            print("Usuário não encontrado.")
            return False

        print("\nUsuário encontrado:")
        self._exibir_usuario(usuario)

        print("\nDigite os novos dados (deixe em branco para manter o mesmo):")
        nome = input(f"Nome [{usuario.nome}]: ") or usuario.nome
        sobrenome = input(f"Sobrenome [{usuario.sobrenome}]: ") or usuario.sobrenome

        dados = {"nome": nome, "sobrenome": sobrenome}

        sucesso = self.usuario_service.atualizar_usuario(usuario_id, dados)
        if sucesso:
            print("Usuário atualizado com sucesso!")
        else:
            print("Erro ao atualizar usuário.")

        return sucesso

    def deletar_usuario(self):
        print("\n===== DELETAR USUÁRIO =====")
        usuario_id = self._selecionar_usuario()
        if not usuario_id:
            return False

        usuario = self.usuario_service.buscar_usuario_por_id(usuario_id)
        if not usuario:
            print("Usuário não encontrado.")
            return False

        print("\nUsuário a ser deletado:")
        self._exibir_usuario(usuario)

        confirmacao = input("\nTem certeza que deseja deletar este usuário? (S/N): ")
        if confirmacao.upper() != "S":
            print("Operação cancelada.")
            return False

        sucesso = self.usuario_service.deletar_usuario(usuario_id)
        if sucesso:
            print("Usuário deletado com sucesso!")
        else:
            print("Erro ao deletar usuário.")

        return sucesso

    def gerenciar_favoritos(self):
        print("\n===== GERENCIAR FAVORITOS =====")
        usuario_id = self._selecionar_usuario()
        if not usuario_id:
            return False

        usuario = self.usuario_service.buscar_usuario_por_id(usuario_id)
        if not usuario:
            print("Usuário não encontrado.")
            return False

        print("\n1. Adicionar produto aos favoritos")
        print("2. Remover produto dos favoritos")
        print("3. Listar produtos favoritos")
        print("V. Voltar")

        opcao = input("\nDigite a opção desejada: ")

        if opcao.upper() == "V":
            return False

        if opcao == "1":
            from modules.products.service import ProdutoService

            produto_service = ProdutoService()
            produtos = produto_service.listar_todos_produtos()

            if not produtos:
                print("Nenhum produto cadastrado.")
                return False

            print("\nProdutos disponíveis:")
            for i, produto in enumerate(produtos, 1):
                print(f"{i}. {produto.nome} - R$ {produto.preco:.2f}")

            try:
                indice = int(input("\nDigite o número do produto: "))
                if 1 <= indice <= len(produtos):
                    produto_id = str(produtos[indice - 1].id)
                    sucesso = self.usuario_service.adicionar_favorito(
                        usuario_id, produto_id
                    )
                    if sucesso:
                        print("Produto adicionado aos favoritos com sucesso!")
                    else:
                        print("Erro ao adicionar produto aos favoritos.")
                else:
                    print("Índice inválido!")
            except ValueError:
                print("Digite um número válido!")

        elif opcao == "2":
            favoritos = self.usuario_service.listar_favoritos(usuario_id)

            if not favoritos:
                print("Nenhum produto favorito encontrado.")
                return False

            print("\nFavoritos disponíveis:")
            from modules.products.service import ProdutoService

            produto_service = ProdutoService()

            for i, produto_id in enumerate(favoritos, 1):
                produto = produto_service.buscar_produto_por_id(str(produto_id))
                if produto:
                    print(
                        f"{i}. {produto.nome} - R$ {produto.preco:.2f} - ID: {produto_id}"
                    )
                else:
                    print(f"{i}. ID: {produto_id} (Produto não encontrado)")

            try:
                indice = int(input("\nDigite o número do favorito a remover: "))
                if 1 <= indice <= len(favoritos):
                    produto_id = str(favoritos[indice - 1])
                    sucesso = self.usuario_service.remover_favorito(
                        usuario_id, produto_id
                    )
                    if sucesso:
                        print("Produto removido dos favoritos com sucesso!")
                    else:
                        print("Erro ao remover produto dos favoritos.")
                else:
                    print("Índice inválido!")
            except ValueError:
                print("Digite um número válido!")

        elif opcao == "3":
            favoritos = self.usuario_service.listar_favoritos(usuario_id)
            if favoritos:
                print("\nProdutos favoritos:")
                from modules.products.service import ProdutoService

                produto_service = ProdutoService()

                for i, produto_id in enumerate(favoritos, 1):
                    produto = produto_service.buscar_produto_por_id(str(produto_id))
                    if produto:
                        print(
                            f"{i}. {produto.nome} - R$ {produto.preco:.2f} - ID: {produto_id}"
                        )
                    else:
                        print(f"{i}. ID: {produto_id} (Produto não encontrado)")
            else:
                print("Nenhum produto favorito encontrado.")

    def _exibir_usuario(self, usuario):
        print(f"\nID: {usuario.id}")
        print(f"Nome: {usuario.nome} {usuario.sobrenome}")
        print(f"CPF: {usuario.cpf}")
        print("Endereços:")
        for i, endereco in enumerate(usuario.enderecos, 1):
            print(f"  Endereço {i}:")
            print(f"    Rua: {endereco.rua}, {endereco.num}")
            print(f"    Bairro: {endereco.bairro}")
            print(f"    Cidade: {endereco.cidade} - {endereco.estado}")
            print(f"    CEP: {endereco.cep}")
        if usuario.favoritos:
            print(f"Favoritos: {len(usuario.favoritos)} produtos")

    def _selecionar_usuario(self) -> Optional[str]:
        usuarios = self.usuario_service.listar_todos_usuarios()

        if not usuarios:
            print("Nenhum usuário cadastrado.")
            return None

        print("\nUsuários disponíveis:")
        for i, usuario in enumerate(usuarios, 1):
            print(f"{i}. {usuario.nome} {usuario.sobrenome} - CPF: {usuario.cpf}")

        opcao_valida = False
        while not opcao_valida:
            try:
                opcao_str = input("\nSelecione o número do usuário (0 para cancelar): ")
                opcao = int(opcao_str)

                if opcao == 0:
                    print("Operação cancelada.")
                    return None

                if 1 <= opcao <= len(usuarios):
                    opcao_valida = True
                    return str(usuarios[opcao - 1].id)
                else:
                    print("Opção inválida!")
            except:
                print("Digite um número válido!")

        return None
