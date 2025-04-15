from src.models.vendedor import Vendedor


class VendedorController:
    def __init__(self):
        self.vendedor_model = Vendedor()

    def criar_vendedor(self):
        print("\nInserindo um novo vendedor")
        nome = input("Nome: ")
        sobrenome = input("Sobrenome: ")
        cpf = input("CPF: ")
        cnpj = input("CNPJ: ")
        enderecos = []

        while True:
            rua = input("Rua: ")
            num = input("Num: ")
            bairro = input("Bairro: ")
            cidade = input("Cidade: ")
            estado = input("Estado: ")
            cep = input("CEP: ")

            endereco = {
                "rua": rua,
                "num": num,
                "bairro": bairro,
                "cidade": cidade,
                "estado": estado,
                "cep": cep,
            }
            enderecos.append(endereco)

            if input("Deseja cadastrar um novo endereço (S/N)? ").upper() != "S":
                break

        resultado = self.vendedor_model.create(nome, sobrenome, cpf, cnpj, enderecos)
        print("Vendedor inserido com ID", resultado.inserted_id)

    def ler_vendedor(self):
        print("\nBuscar vendedor:")
        print("1. Por nome")
        print("2. Por CNPJ")
        print("3. Listar todos")
        opcao = input("Digite a opção desejada: ")

        if opcao == "1":
            nome = input("Nome do vendedor: ")
            resultados = self.vendedor_model.read(nome=nome)
        elif opcao == "2":
            cnpj = input("CNPJ do vendedor: ")
            resultados = self.vendedor_model.read(cnpj=cnpj)
        else:
            resultados = self.vendedor_model.read()

        print("\nVendedores encontrados:")
        for vendedor in resultados:
            print(
                f"Nome: {vendedor['nome']} {vendedor['sobrenome']}, CNPJ: {vendedor['cnpj']}"
            )

    def atualizar_vendedor(self):
        print("\nAtualizar vendedor")
        print("1. Buscar por nome")
        print("2. Buscar por CNPJ")
        opcao = input("Digite a opção desejada: ")

        id_tipo = "nome"
        if opcao == "1":
            identificador = input("Nome do vendedor: ")
        else:
            identificador = input("CNPJ do vendedor: ")
            id_tipo = "cnpj"

        vendedores = list(self.vendedor_model.read(**{id_tipo: identificador}))
        if not vendedores:
            print("Vendedor não encontrado!")
            return

        print("Dados atuais:", vendedores[0])

        novo_nome = input("Novo nome (deixe em branco para manter): ")
        novo_sobrenome = input("Novo sobrenome (deixe em branco para manter): ")
        novo_cpf = input("Novo CPF (deixe em branco para manter): ")
        novo_cnpj = input("Novo CNPJ (deixe em branco para manter): ")

        dados_novos = {}
        if novo_nome:
            dados_novos["nome"] = novo_nome
        if novo_sobrenome:
            dados_novos["sobrenome"] = novo_sobrenome
        if novo_cpf:
            dados_novos["cpf"] = novo_cpf
        if novo_cnpj:
            dados_novos["cnpj"] = novo_cnpj

        if dados_novos:
            resultado = self.vendedor_model.update(identificador, dados_novos, id_tipo)
            print(
                f"Vendedor atualizado: {resultado.modified_count} documento(s) modificado(s)"
            )
        else:
            print("Nenhuma atualização realizada")

    def deletar_vendedor(self):
        print("\nDeletar vendedor")
        print("1. Por nome")
        print("2. Por CNPJ")
        opcao = input("Digite a opção desejada: ")

        id_tipo = "nome"
        if opcao == "1":
            identificador = input("Nome do vendedor a ser deletado: ")
        else:
            identificador = input("CNPJ do vendedor a ser deletado: ")
            id_tipo = "cnpj"

        confirmacao = input(
            f"Tem certeza que deseja deletar o vendedor com {id_tipo} '{identificador}'? (S/N): "
        )
        if confirmacao.upper() == "S":
            resultado = self.vendedor_model.delete(identificador, id_tipo)
            print(
                f"Vendedor deletado: {resultado.deleted_count} documento(s) removido(s)"
            )
