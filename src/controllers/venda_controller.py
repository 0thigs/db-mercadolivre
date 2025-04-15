from src.models.venda import Venda
from src.models.usuario import Usuario
from src.models.produto import Produto


class VendaController:
    def __init__(self):
        self.venda_model = Venda()
        self.usuario_model = Usuario()
        self.produto_model = Produto()

    def criar_venda(self):
        print("\n=== Nova Venda ===")
        usuario_id = input("\nID do usuário: ")
        usuarios = list(self.usuario_model.read(usuario_id=usuario_id))
        if not usuarios:
            print("❌ Usuário não encontrado!")
            return
        usuario = usuarios[0]
        print(f"✓ Cliente: {usuario['nome']} {usuario['sobrenome']}")

        if not usuario["end"]:
            print("❌ Usuário não possui endereços cadastrados!")
            return

        print("\nEndereços disponíveis:")
        for i, endereco in enumerate(usuario["end"]):
            print(
                f"{i + 1}. {endereco['rua']}, {endereco['num']} - {endereco['cidade']}/{endereco['estado']}"
            )

        while True:
            try:
                idx = int(input("\nNúmero do endereço de entrega: ")) - 1
                if 0 <= idx < len(usuario["end"]):
                    endereco_entrega = usuario["end"][idx]
                    print(
                        f"✓ Endereço selecionado: {endereco_entrega['rua']}, {endereco_entrega['num']}"
                    )
                    break
                else:
                    print("❌ Número de endereço inválido!")
            except ValueError:
                print("❌ Por favor, digite um número válido!")

        produtos_venda = []
        total = 0
        print("\n=== Adicionar Produtos ===")
        print("(Pressione ENTER sem digitar nada para finalizar)")

        while True:
            produto_id = input("\nID do produto: ")
            if not produto_id:
                if not produtos_venda:
                    print("❌ Nenhum produto adicionado. Venda cancelada.")
                    return
                break

            produtos = list(self.produto_model.read(produto_id=produto_id))
            if not produtos:
                print("❌ Produto não encontrado!")
                continue

            produto = produtos[0]
            print(f"\nProduto: {produto['nome']}")
            print(f"Preço: R$ {produto['preco']:.2f}")
            print(f"Estoque: {produto['quantidade']} unidades")

            try:
                quantidade = int(input("Quantidade desejada: "))
                if quantidade <= 0:
                    print("❌ Quantidade deve ser maior que zero!")
                    continue
                if quantidade > produto["quantidade"]:
                    print(
                        f"❌ Quantidade indisponível! (máximo: {produto['quantidade']})"
                    )
                    continue

                subtotal = produto["preco"] * quantidade
                produtos_venda.append(
                    {
                        "produto_id": produto_id,
                        "nome": produto["nome"],
                        "quantidade": quantidade,
                        "preco_unitario": produto["preco"],
                        "subtotal": subtotal,
                    }
                )

                nova_quantidade = produto["quantidade"] - quantidade
                self.produto_model.update(produto_id, {"quantidade": nova_quantidade})

                total += subtotal
                print(f"✓ Produto adicionado! Total atual: R$ {total:.2f}")

            except ValueError:
                print("❌ Por favor, digite uma quantidade válida!")

        print("\n=== Forma de Pagamento ===")
        formas = {"1": "Cartão de Crédito", "2": "Pix", "3": "Boleto"}

        for key, valor in formas.items():
            print(f"{key}. {valor}")

        while True:
            opcao = input("\nEscolha a forma de pagamento: ")
            if opcao in formas:
                forma_pagamento = formas[opcao]
                break
            print("❌ Opção inválida!")

        print("\n=== Resumo da Venda ===")
        print(f"Cliente: {usuario['nome']} {usuario['sobrenome']}")
        print(
            f"Endereço: {endereco_entrega['rua']}, {endereco_entrega['num']} - {endereco_entrega['cidade']}/{endereco_entrega['estado']}"
        )
        print(f"Forma de pagamento: {forma_pagamento}")
        print("\nProdutos:")
        for p in produtos_venda:
            print(f"- {p['nome']} (x{p['quantidade']}) - R$ {p['subtotal']:.2f}")
        print(f"\nTotal: R$ {total:.2f}")

        if input("\nConfirmar venda? (S/N): ").upper() != "S":
            print("Venda cancelada!")
            for p in produtos_venda:
                produto = list(self.produto_model.read(produto_id=p["produto_id"]))[0]
                nova_quantidade = produto["quantidade"] + p["quantidade"]
                self.produto_model.update(
                    p["produto_id"], {"quantidade": nova_quantidade}
                )
            return

        resultado = self.venda_model.create(
            str(usuario["_id"]),
            produtos_venda[0].get("vendedor_id", ""),
            produtos_venda,
            total,
            forma_pagamento,
            endereco_entrega,
        )

        print("✓ Venda finalizada com sucesso!")
        print(f"ID da venda: {resultado.inserted_id}")

    def ler_venda(self):
        print("\n=== Consultar Vendas ===")
        print("1. Buscar por ID da venda")
        print("2. Listar todas as vendas")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            venda_id = input("ID da venda: ")
            resultados = self.venda_model.read(venda_id=venda_id)
        elif opcao == "2":
            resultados = self.venda_model.read()
        else:
            print("❌ Opção inválida!")
            return

        vendas = list(resultados)

        if not vendas:
            print("Nenhuma venda encontrada!")
            return

        for venda in vendas:
            print("\n" + "=" * 40)
            print(f"ID: {venda['_id']}")
            print(f"Data: {venda['data']}")
            print(f"Status: {venda['status']}")
            print(f"Total: R$ {venda['total']:.2f}")
            print(f"Forma de pagamento: {venda['forma_pagamento']}")
            print("\nProdutos:")
            for produto in venda["produtos"]:
                print(
                    f"- {produto['nome']} (x{produto['quantidade']}) - R$ {produto['subtotal']:.2f}"
                )
            print("=" * 40)

    def atualizar_venda(self):
        print("\n=== Atualizar Status da Venda ===")
        venda_id = input("ID da venda: ")

        vendas = list(self.venda_model.read(venda_id=venda_id))
        if not vendas:
            print("❌ Venda não encontrada!")
            return

        venda = vendas[0]
        print(f"\nStatus atual: {venda['status']}")

        status_opcoes = {
            "1": "pendente",
            "2": "enviado",
            "3": "entregue",
            "4": "cancelado",
        }

        print("\nNovos status disponíveis:")
        for num, status in status_opcoes.items():
            print(f"{num}. {status}")

        while True:
            opcao = input("\nEscolha o novo status: ")
            if opcao in status_opcoes:
                novo_status = status_opcoes[opcao]
                break
            print("❌ Opção inválida!")

        if novo_status == venda["status"]:
            print("❌ Este já é o status atual!")
            return

        resultado = self.venda_model.update(venda_id, {"status": novo_status})
        if resultado.modified_count > 0:
            print(f"✓ Status atualizado para: {novo_status}")
        else:
            print("❌ Erro ao atualizar status!")

    def deletar_venda(self):
        print("\n=== Cancelar/Deletar Venda ===")
        venda_id = input("ID da venda: ")

        vendas = list(self.venda_model.read(venda_id=venda_id))
        if not vendas:
            print("❌ Venda não encontrada!")
            return

        venda = vendas[0]
        print("\nDetalhes da venda:")
        print(f"Data: {venda['data']}")
        print(f"Status: {venda['status']}")
        print(f"Total: R$ {venda['total']:.2f}")
        print("\nProdutos:")
        for p in venda["produtos"]:
            print(f"- {p['nome']} (x{p['quantidade']})")

        if input("\nConfirmar cancelamento? (S/N): ").upper() != "S":
            print("Operação cancelada!")
            return

        for produto_venda in venda["produtos"]:
            produtos = list(
                self.produto_model.read(produto_id=produto_venda["produto_id"])
            )
            if produtos:
                produto = produtos[0]
                nova_quantidade = produto["quantidade"] + produto_venda["quantidade"]
                self.produto_model.update(
                    produto_venda["produto_id"], {"quantidade": nova_quantidade}
                )
                print(
                    f"✓ Estoque atualizado: {produto['nome']} (+{produto_venda['quantidade']})"
                )

        resultado = self.venda_model.delete(venda_id)
        if resultado.deleted_count > 0:
            print("✓ Venda cancelada com sucesso!")
        else:
            print("❌ Erro ao cancelar venda!")
