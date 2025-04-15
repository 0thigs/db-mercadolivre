from src.models.produto import Produto
from src.models.vendedor import Vendedor


class ProdutoController:
    def __init__(self):
        self.produto_model = Produto()
        self.vendedor_model = Vendedor()

    def criar_produto(self):
        print("\nInserindo um novo produto")

        print("\nIdentificar vendedor:")
        print("1. Por nome")
        print("2. Por CNPJ")
        opcao = input("Digite a opção desejada: ")

        vendedor_id = None
        if opcao == "1":
            nome = input("Nome do vendedor: ")
            vendedores = list(self.vendedor_model.read(nome=nome))
        else:
            cnpj = input("CNPJ do vendedor: ")
            vendedores = list(self.vendedor_model.read(cnpj=cnpj))

        if not vendedores:
            print("Vendedor não encontrado. Produto não pode ser cadastrado.")
            return
        elif len(vendedores) > 1:
            print("Múltiplos vendedores encontrados. Selecione um pelo índice:")
            for i, v in enumerate(vendedores):
                print(f"{i + 1}. {v['nome']} {v['sobrenome']} - CNPJ: {v['cnpj']}")
            idx = int(input("Índice do vendedor: ")) - 1
            vendedor_id = str(vendedores[idx]["_id"])
        else:
            vendedor_id = str(vendedores[0]["_id"])

        nome = input("Nome do produto: ")
        descricao = input("Descrição: ")
        preco = float(input("Preço: "))
        quantidade = int(input("Quantidade em estoque: "))

        categorias = []
        while True:
            categoria = input("Categoria (deixe em branco para finalizar): ")
            if not categoria:
                break
            categorias.append(categoria)

        resultado = self.produto_model.create(
            nome, descricao, preco, quantidade, categorias, vendedor_id
        )
        print("Produto inserido com ID", resultado.inserted_id)

    def ler_produto(self):
        print("\nBuscar produto:")
        print("1. Por ID")
        print("2. Por nome")
        print("3. Por categoria")
        print("4. Por vendedor")
        print("5. Listar todos")
        opcao = input("Digite a opção desejada: ")

        if opcao == "1":
            produto_id = input("ID do produto: ")
            resultados = self.produto_model.read(produto_id=produto_id)
        elif opcao == "2":
            nome = input("Nome do produto (parcial): ")
            resultados = self.produto_model.read(nome=nome)
        elif opcao == "3":
            categoria = input("Categoria: ")
            resultados = self.produto_model.read(categoria=categoria)
        elif opcao == "4":
            vendedor_id = input("ID do vendedor: ")
            resultados = self.produto_model.read(vendedor_id=vendedor_id)
        else:
            resultados = self.produto_model.read()

        print("\nProdutos encontrados:")
        for produto in resultados:
            print(
                f"ID: {produto['_id']}, Nome: {produto['nome']}, Preço: R${produto['preco']:.2f}, Estoque: {produto['quantidade']}"
            )
            print(f"  Descrição: {produto['descricao']}")
            print(f"  Categorias: {', '.join(produto['categorias'])}")
            print(f"  Vendedor ID: {produto['vendedor_id']}")
            print("-" * 40)

    def atualizar_produto(self):
        print("\nAtualizar produto")
        produto_id = input("ID do produto: ")

        produtos = list(self.produto_model.read(produto_id=produto_id))
        if not produtos:
            print("Produto não encontrado!")
            return

        print("Dados atuais:", produtos[0])

        novo_nome = input("Novo nome (deixe em branco para manter): ")
        nova_descricao = input("Nova descrição (deixe em branco para manter): ")
        novo_preco = input("Novo preço (deixe em branco para manter): ")
        nova_quantidade = input("Nova quantidade (deixe em branco para manter): ")

        dados_novos = {}
        if novo_nome:
            dados_novos["nome"] = novo_nome
        if nova_descricao:
            dados_novos["descricao"] = nova_descricao
        if novo_preco:
            dados_novos["preco"] = float(novo_preco)
        if nova_quantidade:
            dados_novos["quantidade"] = int(nova_quantidade)

        if input("Deseja atualizar as categorias? (S/N): ").upper() == "S":
            categorias = []
            while True:
                categoria = input("Categoria (deixe em branco para finalizar): ")
                if not categoria:
                    break
                categorias.append(categoria)
            dados_novos["categorias"] = categorias

        if dados_novos:
            resultado = self.produto_model.update(produto_id, dados_novos)
            print(
                f"Produto atualizado: {resultado.modified_count} documento(s) modificado(s)"
            )
        else:
            print("Nenhuma atualização realizada")

    def deletar_produto(self):
        print("\nDeletar produto")
        produto_id = input("ID do produto a ser deletado: ")

        produtos = list(self.produto_model.read(produto_id=produto_id))
        if not produtos:
            print("Produto não encontrado!")
            return

        print("Produto a ser deletado:", produtos[0])

        confirmacao = input("Tem certeza que deseja deletar este produto? (S/N): ")
        if confirmacao.upper() == "S":
            resultado = self.produto_model.delete(produto_id)
            print(
                f"Produto deletado: {resultado.deleted_count} documento(s) removido(s)"
            )
