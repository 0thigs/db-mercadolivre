from typing import List, Optional
from decimal import Decimal
from bson import ObjectId
from modules.products.models import Produto
from modules.products.service import ProdutoService
from modules.sellers.service import VendedorService


class ProdutoController:
    def __init__(self, produto_service, vendedor_service=None):
        self.produto_service = produto_service
        self.vendedor_service = vendedor_service or VendedorService()

    def criar_produto(self):
        print("\n===== CRIAR PRODUTO =====")

        vendedor_id = self._selecionar_vendedor()
        if not vendedor_id:
            return None

        nome = input("Nome do produto: ")
        descricao = input("Descrição: ")

        preco_valido = False
        while not preco_valido:
            try:
                preco_str = input("Preço (ex: 99.90): ")
                preco = Decimal(preco_str)
                preco_valido = True
            except:
                print("Preço inválido! Use o formato: 99.90")

        estoque_valido = False
        while not estoque_valido:
            try:
                estoque_str = input("Quantidade em estoque: ")
                estoque = int(estoque_str)
                estoque_valido = True
            except:
                print("Estoque inválido! Digite um número inteiro.")

        categorias = []
        while True:
            categoria = input("Categoria (deixe em branco para finalizar): ")
            if not categoria:
                break
            categorias.append(categoria)

        especificacoes = {}
        print("\nEspecificações do produto (deixe em branco para finalizar)")
        while True:
            chave = input("Característica: ")
            if not chave:
                break
            valor = input(f"Valor para {chave}: ")
            especificacoes[chave] = valor

        imagens = []
        print("\nImagens do produto (deixe em branco para finalizar)")
        while True:
            url = input("URL da imagem: ")
            if not url:
                break
            imagens.append(url)

        produto = Produto(
            nome=nome,
            descricao=descricao,
            preco=preco,
            estoque=estoque,
            categorias=categorias,
            vendedor_id=ObjectId(vendedor_id),
            imagens=imagens,
            especificacoes=especificacoes,
        )

        produto_id = self.produto_service.criar_produto(produto)
        print(f"Produto criado com ID: {produto_id}")
        return produto_id

    def ler_produto(self):
        print("\n===== BUSCAR PRODUTO =====")
        produtos = self.produto_service.listar_todos_produtos()

        if produtos:
            for produto in produtos:
                self._exibir_produto(produto)
                print("---")

            produto_id = self._selecionar_produto()
            if produto_id:
                produto = self.produto_service.buscar_produto_por_id(produto_id)
                if produto:
                    print("\nDetalhes completos do produto selecionado:")
                    self._exibir_produto(produto)
        else:
            print("Nenhum produto cadastrado.")

    def atualizar_produto(self):
        print("\n===== ATUALIZAR PRODUTO =====")
        produto_id = self._selecionar_produto()
        if not produto_id:
            return False

        produto = self.produto_service.buscar_produto_por_id(produto_id)
        if not produto:
            print("Produto não encontrado.")
            return False

        print("\nProduto encontrado:")
        self._exibir_produto(produto)

        print("\nDigite os novos dados (deixe em branco para manter o mesmo):")
        nome = input(f"Nome [{produto.nome}]: ") or produto.nome
        descricao = input(f"Descrição [{produto.descricao}]: ") or produto.descricao

        preco = produto.preco
        preco_str = input(f"Preço [{produto.preco}]: ")
        if preco_str:
            try:
                preco = Decimal(preco_str)
            except:
                print("Preço inválido! Mantendo o valor atual.")

        estoque = produto.estoque
        estoque_str = input(f"Estoque [{produto.estoque}]: ")
        if estoque_str:
            try:
                estoque = int(estoque_str)
            except:
                print("Estoque inválido! Mantendo o valor atual.")

        print("\nDeseja atualizar as categorias? (S/N)")
        if input().upper() == "S":
            categorias = []
            print("Digite as novas categorias (deixe em branco para finalizar):")
            while True:
                categoria = input("Categoria: ")
                if not categoria:
                    break
                categorias.append(categoria)
        else:
            categorias = produto.categorias

        print("\nDeseja atualizar as especificações? (S/N)")
        if input().upper() == "S":
            especificacoes = {}
            print("Digite as novas especificações (deixe em branco para finalizar):")
            while True:
                chave = input("Característica: ")
                if not chave:
                    break
                valor = input(f"Valor para {chave}: ")
                especificacoes[chave] = valor
        else:
            especificacoes = produto.especificacoes

        dados = {
            "nome": nome,
            "descricao": descricao,
            "preco": preco,
            "estoque": estoque,
            "categorias": categorias,
            "especificacoes": especificacoes,
        }

        sucesso = self.produto_service.atualizar_produto(produto_id, dados)
        if sucesso:
            print("Produto atualizado com sucesso!")
        else:
            print("Erro ao atualizar produto.")

        return sucesso

    def deletar_produto(self):
        print("\n===== DELETAR PRODUTO =====")
        produto_id = self._selecionar_produto()
        if not produto_id:
            return False

        produto = self.produto_service.buscar_produto_por_id(produto_id)
        if not produto:
            print("Produto não encontrado.")
            return False

        print("\nProduto a ser deletado:")
        self._exibir_produto(produto)

        confirmacao = input("\nTem certeza que deseja deletar este produto? (S/N): ")
        if confirmacao.upper() != "S":
            print("Operação cancelada.")
            return False

        sucesso = self.produto_service.deletar_produto(produto_id)
        if sucesso:
            print("Produto marcado como inativo com sucesso!")
        else:
            print("Erro ao deletar produto.")

        return sucesso

    def gerenciar_estoque(self):
        print("\n===== GERENCIAR ESTOQUE =====")
        produto_id = self._selecionar_produto()
        if not produto_id:
            return False

        produto = self.produto_service.buscar_produto_por_id(produto_id)
        if not produto:
            print("Produto não encontrado.")
            return False

        print(f"\nProduto: {produto.nome}")
        print(f"Estoque atual: {produto.estoque}")

        print("\n1. Adicionar ao estoque")
        print("2. Remover do estoque")
        print("V. Voltar")

        opcao = input("\nDigite a opção desejada: ")

        if opcao.upper() == "V":
            return False

        quantidade_valida = False
        while not quantidade_valida:
            try:
                quantidade_str = input("Quantidade: ")
                quantidade = int(quantidade_str)
                if quantidade <= 0:
                    print("A quantidade deve ser maior que zero.")
                    continue
                quantidade_valida = True
            except:
                print("Quantidade inválida! Digite um número inteiro.")

        if opcao == "1":
            sucesso = self.produto_service.atualizar_estoque(produto_id, quantidade)
            if sucesso:
                print(f"Estoque atualizado: +{quantidade} unidades")
            else:
                print("Erro ao atualizar estoque.")

        elif opcao == "2":
            if quantidade > produto.estoque:
                print(
                    f"Erro: A quantidade a remover ({quantidade}) é maior que o estoque atual ({produto.estoque})."
                )
                return False

            sucesso = self.produto_service.atualizar_estoque(produto_id, -quantidade)
            if sucesso:
                print(f"Estoque atualizado: -{quantidade} unidades")
            else:
                print("Erro ao atualizar estoque.")

        return True

    def gerenciar_avaliacoes(self):
        print("\n===== AVALIAR PRODUTO =====")
        produto_id = input("ID do produto: ")

        produto = self.produto_service.buscar_produto_por_id(produto_id)
        if not produto:
            print("Produto não encontrado.")
            return False

        print(f"\nProduto: {produto.nome}")

        print("\n1. Adicionar avaliação")
        print("2. Ver avaliações")
        print("V. Voltar")

        opcao = input("\nDigite a opção desejada: ")

        if opcao.upper() == "V":
            return False

        if opcao == "1":
            usuario_id = input("ID do usuário avaliador: ")
            try:
                usuario_id_obj = ObjectId(usuario_id)
            except:
                print("ID de usuário inválido.")
                return False

            nota_valida = False
            while not nota_valida:
                try:
                    nota_str = input("Nota (1 a 5): ")
                    nota = int(nota_str)
                    if nota < 1 or nota > 5:
                        print("A nota deve ser entre 1 e 5.")
                        continue
                    nota_valida = True
                except:
                    print("Nota inválida! Digite um número de 1 a 5.")

            comentario = input("Comentário: ")

            try:
                self.produto_service.adicionar_avaliacao(
                    produto_id=ObjectId(produto_id),
                    usuario_id=usuario_id_obj,
                    nota=nota,
                    comentario=comentario,
                )
                print("Avaliação adicionada com sucesso!")
            except Exception as e:
                print(f"Erro ao adicionar avaliação: {str(e)}")

        elif opcao == "2":
            avaliacoes = self.produto_service.buscar_avaliacoes(produto_id)
            if avaliacoes:
                print(
                    f"\nAvaliações do produto (média: {produto.avaliacao_media:.1f}/5):"
                )
                for i, avaliacao in enumerate(avaliacoes, 1):
                    print(f"\n--- Avaliação {i} ---")
                    print(f"Usuário: {avaliacao.usuario_id}")
                    print(f"Nota: {avaliacao.nota}/5")
                    print(f"Data: {avaliacao.data}")
                    print(f"Comentário: {avaliacao.comentario}")
            else:
                print("Nenhuma avaliação encontrada para este produto.")

        return True

    def _selecionar_vendedor(self) -> Optional[str]:
        print("\nSelecione um vendedor para o produto:")
        vendedores = self.vendedor_service.listar_todos_vendedores()

        if not vendedores:
            print("Nenhum vendedor cadastrado. Cadastre um vendedor primeiro.")
            return None

        print("\nVendedores disponíveis:")
        for i, vendedor in enumerate(vendedores, 1):
            print(f"{i}. {vendedor.nome} {vendedor.sobrenome} (CNPJ: {vendedor.cnpj})")

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

    def _selecionar_produto(self) -> Optional[str]:
        produtos = self.produto_service.listar_todos_produtos()

        if not produtos:
            print("Nenhum produto cadastrado.")
            return None

        print("\nProdutos disponíveis:")
        for i, produto in enumerate(produtos, 1):
            print(
                f"{i}. {produto.nome} - R$ {produto.preco:.2f} - Estoque: {produto.estoque}"
            )

        opcao_valida = False
        while not opcao_valida:
            try:
                opcao_str = input("\nSelecione o número do produto (0 para cancelar): ")
                opcao = int(opcao_str)

                if opcao == 0:
                    print("Operação cancelada.")
                    return None

                if 1 <= opcao <= len(produtos):
                    opcao_valida = True
                    return str(produtos[opcao - 1].id)
                else:
                    print("Opção inválida!")
            except:
                print("Digite um número válido!")

        return None

    def _exibir_produto(self, produto):
        print(f"\nID: {produto.id}")
        print(f"Nome: {produto.nome}")
        print(f"Descrição: {produto.descricao}")
        print(f"Preço: R$ {produto.preco:.2f}")
        print(f"Estoque: {produto.estoque} unidades")
        print(f"Categorias: {', '.join(produto.categorias)}")

        if produto.especificacoes:
            print("Especificações:")
            for chave, valor in produto.especificacoes.items():
                print(f"  {chave}: {valor}")

        if produto.imagens:
            print("Imagens:")
            for url in produto.imagens:
                print(f"  {url}")

        try:
            vendedor = self.vendedor_service.buscar_vendedor_por_id(
                str(produto.vendedor_id)
            )
            if vendedor:
                print(f"Vendedor: {vendedor.nome} {vendedor.sobrenome}")
            else:
                print(f"Vendedor ID: {produto.vendedor_id}")
        except:
            print(f"Vendedor ID: {produto.vendedor_id}")

    def _exibir_lista_produtos(self, produtos):
        if produtos:
            print(f"\nForam encontrados {len(produtos)} produtos:")
            for produto in produtos:
                self._exibir_produto(produto)
                print("---")
        else:
            print("Nenhum produto encontrado.")
