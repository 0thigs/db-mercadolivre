from modules.database.mongo_db import MongoDBConnection
from modules.database.redis_db import RedisConnection
from modules.database.controller import MongoRedisController
from modules.users.models import Usuario
from modules.users.service import UsuarioService
from modules.users.controller import UsuarioController
from modules.sellers.service import VendedorService
from modules.sellers.controller import VendedorController
from modules.products.service import ProdutoService
from modules.products.controller import ProdutoController
from modules.sales.service import PedidoService
from modules.sales.controller import PedidoController


def main():
    print("\n=== Sistema Iniciado ===\n")

    mongo_db = MongoDBConnection()
    RedisConnection.get_client()

    db_controller = MongoRedisController()

    usuario_service = UsuarioService()
    vendedor_service = VendedorService()
    produto_service = ProdutoService()
    pedido_service = PedidoService()

    usuario_controller = UsuarioController(usuario_service)
    vendedor_controller = VendedorController(vendedor_service)
    produto_controller = ProdutoController(produto_service, vendedor_service)
    pedido_controller = PedidoController(
        pedido_service, produto_service, usuario_service
    )

    while True:
        print("\n===== MENU PRINCIPAL =====")
        print("1. MongoDB - Sistema de Vendas")
        print("2. Redis - Sistema de Cache")
        print("S. Sair")

        opcao = input("\nDigite a opção desejada: ")

        if opcao.upper() == "S":
            print("\nSaindo do sistema...")
            break

        elif opcao == "1":
            menu_mongodb(
                usuario_controller,
                vendedor_controller,
                produto_controller,
                pedido_controller,
            )

        elif opcao == "2":
            db_controller.redis_main_menu()

        else:
            print("Opção inválida!")


def menu_mongodb(
    usuario_controller, vendedor_controller, produto_controller, pedido_controller
):
    while True:
        print("\n===== MENU MONGODB =====")
        print("1. Gerenciar Usuários")
        print("2. Gerenciar Vendedores")
        print("3. Gerenciar Produtos")
        print("4. Gerenciar Vendas")
        print("V. Voltar")

        opcao = input("\nDigite a opção desejada: ")

        if opcao.upper() == "V":
            break

        elif opcao == "1":
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
            print("5. Gerenciar Estoque")
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
            elif sub_opcao == "5":
                produto_controller.gerenciar_estoque()

        elif opcao == "4":
            print("\n===== MENU DE VENDAS =====")
            print("1. Criar Pedido")
            print("2. Listar Pedidos")
            print("3. Registrar Pagamento")
            print("4. Cancelar Pedido")
            print("V. Voltar")
            sub_opcao = input("\nDigite a opção desejada: ")

            if sub_opcao.upper() == "V":
                continue

            if sub_opcao == "1":
                pedido_controller.criar_pedido()
            elif sub_opcao == "2":
                pedido_controller.listar_pedidos()
            elif sub_opcao == "3":
                pedido_controller.registrar_pagamento()
            elif sub_opcao == "4":
                pedido_controller.cancelar_pedido()


if __name__ == "__main__":
    main()
