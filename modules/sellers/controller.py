from modules.sellers.models import Vendedor
from modules.sellers.service import VendedorService
from modules.users.models import Endereco
from typing import Optional


class VendedorController:
    def __init__(self, vendedor_service):
        self.vendedor_service = vendedor_service

    def criar_vendedor(self):
        print("\n===== CRIAR VENDEDOR =====")
        nome = input("Nome: ")
        sobrenome = input("Sobrenome: ")
        cpf = input("CPF: ")
        cnpj = input("CNPJ: ")

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

        vendedor = Vendedor(
            nome=nome, sobrenome=sobrenome, cpf=cpf, cnpj=cnpj, enderecos=[endereco]
        )

        vendedor_id = self.vendedor_service.criar_vendedor(vendedor)
        print(f"Vendedor criado com ID: {vendedor_id}")
        return vendedor_id

    def _selecionar_vendedor(self) -> Optional[str]:
        vendedores = self.vendedor_service.listar_todos_vendedores()

        if not vendedores:
            print("Nenhum vendedor cadastrado.")
            return None

        print("\nVendedores disponíveis:")
        for i, vendedor in enumerate(vendedores, 1):
            print(f"{i}. {vendedor.nome} {vendedor.sobrenome} - CNPJ: {vendedor.cnpj}")

        opcao_valida = False
        while not opcao_valida:
            try:
                opcao_str = input(
                    "\nSelecione o número do vendedor (0 para cancelar): "
                )
                opcao = int(opcao_str)

                if opcao == 0:
                    print("Operação cancelada.")
                    return None

                if 1 <= opcao <= len(vendedores):
                    opcao_valida = True
                    return str(vendedores[opcao - 1].id)
                else:
                    print("Opção inválida!")
            except:
                print("Digite um número válido!")

        return None

    def ler_vendedor(self):
        print("\n===== BUSCAR VENDEDOR =====")
        vendedores = self.vendedor_service.listar_todos_vendedores()

        if vendedores:
            for vendedor in vendedores:
                self._exibir_vendedor(vendedor)
                print("---")

            vendedor_id = self._selecionar_vendedor()
            if vendedor_id:
                vendedor = self.vendedor_service.buscar_vendedor_por_id(vendedor_id)
                if vendedor:
                    print("\nDetalhes completos do vendedor selecionado:")
                    self._exibir_vendedor(vendedor)
        else:
            print("Nenhum vendedor cadastrado.")

    def atualizar_vendedor(self):
        print("\n===== ATUALIZAR VENDEDOR =====")
        vendedor_id = self._selecionar_vendedor()
        if not vendedor_id:
            return False

        vendedor = self.vendedor_service.buscar_vendedor_por_id(vendedor_id)
        if not vendedor:
            print("Vendedor não encontrado.")
            return False

        print("\nVendedor encontrado:")
        self._exibir_vendedor(vendedor)

        print("\nDigite os novos dados (deixe em branco para manter o mesmo):")
        nome = input(f"Nome [{vendedor.nome}]: ") or vendedor.nome
        sobrenome = input(f"Sobrenome [{vendedor.sobrenome}]: ") or vendedor.sobrenome
        cnpj = input(f"CNPJ [{vendedor.cnpj}]: ") or vendedor.cnpj

        dados = {"nome": nome, "sobrenome": sobrenome, "cnpj": cnpj}

        sucesso = self.vendedor_service.atualizar_vendedor(vendedor_id, dados)
        if sucesso:
            print("Vendedor atualizado com sucesso!")
        else:
            print("Erro ao atualizar vendedor.")

        return sucesso

    def deletar_vendedor(self):
        print("\n===== DELETAR VENDEDOR =====")
        vendedor_id = self._selecionar_vendedor()
        if not vendedor_id:
            return False

        vendedor = self.vendedor_service.buscar_vendedor_por_id(vendedor_id)
        if not vendedor:
            print("Vendedor não encontrado.")
            return False

        print("\nVendedor a ser deletado:")
        self._exibir_vendedor(vendedor)

        confirmacao = input("\nTem certeza que deseja deletar este vendedor? (S/N): ")
        if confirmacao.upper() != "S":
            print("Operação cancelada.")
            return False

        sucesso = self.vendedor_service.deletar_vendedor(vendedor_id)
        if sucesso:
            print("Vendedor deletado com sucesso!")
        else:
            print("Erro ao deletar vendedor.")

        return sucesso

    def _exibir_vendedor(self, vendedor):
        print(f"\nID: {vendedor.id}")
        print(f"Nome: {vendedor.nome} {vendedor.sobrenome}")
        print(f"CPF: {vendedor.cpf}")
        print(f"CNPJ: {vendedor.cnpj}")
        print("Endereços:")
        for i, endereco in enumerate(vendedor.enderecos, 1):
            print(f"  Endereço {i}:")
            print(f"    Rua: {endereco.rua}, {endereco.num}")
            print(f"    Bairro: {endereco.bairro}")
            print(f"    Cidade: {endereco.cidade} - {endereco.estado}")
            print(f"    CEP: {endereco.cep}")
        if vendedor.produtos:
            print(f"Produtos: {len(vendedor.produtos)} cadastrados")
