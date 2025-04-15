from src.controllers.usuario_controller import UsuarioController
from src.controllers.vendedor_controller import VendedorController
from src.controllers.produto_controller import ProdutoController
from src.controllers.venda_controller import VendaController


def main():
    usuario_controller = UsuarioController()
    vendedor_controller = VendedorController()
    produto_controller = ProdutoController()
    venda_controller = VendaController()

    while True:
        print("\n===== MENU PRINCIPAL =====")
        print("1. Gerenciar Usuários")
        print("2. Gerenciar Vendedores")
        print("3. Gerenciar Produtos")
        print("4. Gerenciar Vendas")
        print("S. Sair")
        opcao = input("\nDigite a opção desejada: ")

        if opcao.upper() == "S":
            break

        if opcao == "1":
            print("\n===== MENU DE USUÁRIOS =====")
            print("1. Criar Usuário")
            print("2. Buscar Usuários")
            print("3. Atualizar Usuário")
            print("4. Deletar Usuário")
            print("5. Gerenciar Favoritos")
            print("V. Voltar")
            sub_opcao = input("\nDigite a opção desejada: ")

            if sub_opcao.upper() == "V":
                continue

            if sub_opcao == "1":
                usuario_controller.criar_usuario()
            elif sub_opcao == "2":
                usuario_controller.ler_usuario()
            elif sub_opcao == "3":
                usuario_controller.atualizar_usuario()
            elif sub_opcao == "4":
                usuario_controller.deletar_usuario()
            elif sub_opcao == "5":
                usuario_controller.gerenciar_favoritos()

        elif opcao == "2":
            print("\n===== MENU DE VENDEDORES =====")
            print("1. Criar Vendedor")
            print("2. Buscar Vendedores")
            print("3. Atualizar Vendedor")
            print("4. Deletar Vendedor")
            print("V. Voltar")
            sub_opcao = input("\nDigite a opção desejada: ")

            if sub_opcao.upper() == "V":
                continue

            if sub_opcao == "1":
                vendedor_controller.criar_vendedor()
            elif sub_opcao == "2":
                vendedor_controller.ler_vendedor()
            elif sub_opcao == "3":
                vendedor_controller.atualizar_vendedor()
            elif sub_opcao == "4":
                vendedor_controller.deletar_vendedor()

        elif opcao == "3":
            print("\n===== MENU DE PRODUTOS =====")
            print("1. Criar Produto")
            print("2. Buscar Produtos")
            print("3. Atualizar Produto")
            print("4. Deletar Produto")
            print("V. Voltar")
            sub_opcao = input("\nDigite a opção desejada: ")

            if sub_opcao.upper() == "V":
                continue

            if sub_opcao == "1":
                produto_controller.criar_produto()
            elif sub_opcao == "2":
                produto_controller.ler_produto()
            elif sub_opcao == "3":
                produto_controller.atualizar_produto()
            elif sub_opcao == "4":
                produto_controller.deletar_produto()

        elif opcao == "4":
            print("\n===== MENU DE VENDAS =====")
            print("1. Criar Venda")
            print("2. Buscar Vendas")
            print("3. Atualizar Status da Venda")
            print("4. Cancelar/Deletar Venda")
            print("V. Voltar")
            sub_opcao = input("\nDigite a opção desejada: ")

            if sub_opcao.upper() == "V":
                continue

            if sub_opcao == "1":
                venda_controller.criar_venda()
            elif sub_opcao == "2":
                venda_controller.ler_venda()
            elif sub_opcao == "3":
                venda_controller.atualizar_venda()
            elif sub_opcao == "4":
                venda_controller.deletar_venda()

    print("Sistema finalizado. Até mais!")


if __name__ == "__main__":
    main()
