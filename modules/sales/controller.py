from typing import List, Optional, Dict
from decimal import Decimal
from bson import ObjectId
from modules.sales.models import Pedido, ItemPedido, Pagamento, StatusPedido
from modules.sales.service import PedidoService
from modules.products.service import ProdutoService
from modules.users.service import UsuarioService
from modules.users.models import Endereco


class PedidoController:
    def __init__(self, pedido_service=None, produto_service=None, usuario_service=None):
        self.pedido_service = pedido_service or PedidoService()
        self.produto_service = produto_service or ProdutoService()
        self.usuario_service = usuario_service or UsuarioService()

    def criar_pedido(self):
        print("\n===== CRIAR PEDIDO =====")

        usuario_id = self._selecionar_usuario()
        if not usuario_id:
            return None

        itens_carrinho = self._montar_carrinho()
        if not itens_carrinho:
            print("Carrinho vazio. Operação cancelada.")
            return None

        endereco_entrega = self._coletar_endereco_entrega()
        if not endereco_entrega:
            return None

        frete_str = input("Valor do frete (ex: 15.90): ")
        try:
            frete = Decimal(frete_str)
        except:
            print("Valor de frete inválido. Usando 0.00")
            frete = Decimal("0.00")

        print("\n===== RESUMO DO PEDIDO =====")
        print(f"Cliente: {self._obter_nome_usuario(usuario_id)}")

        print("\nItens:")
        total_itens = Decimal("0.00")
        for item in itens_carrinho:
            produto = self.produto_service.buscar_produto_por_id(item["produto_id"])
            if produto:
                subtotal = produto.preco * item["quantidade"]
                total_itens += subtotal
                print(f"- {produto.nome} x {item['quantidade']} = R$ {subtotal:.2f}")

        print(f"\nSubtotal: R$ {total_itens:.2f}")
        print(f"Frete: R$ {frete:.2f}")
        print(f"Total: R$ {(total_itens + frete):.2f}")

        print("\nEndereço de entrega:")
        for chave, valor in endereco_entrega.items():
            print(f"{chave}: {valor}")

        confirmar = input("\nConfirmar pedido? (S/N): ")
        if confirmar.upper() != "S":
            print("Pedido cancelado.")
            return None

        try:
            pedido_id = self.pedido_service.criar_pedido_por_carrinho(
                usuario_id=usuario_id,
                itens_carrinho=itens_carrinho,
                endereco_entrega=endereco_entrega,
                frete=frete,
            )
            print(f"Pedido criado com sucesso! ID: {pedido_id}")

            self._registrar_pagamento(str(pedido_id))

            return pedido_id
        except Exception as e:
            print(f"Erro ao criar pedido: {str(e)}")
            return None

    def listar_pedidos(self):
        print("\n===== BUSCAR PEDIDOS =====")
        pedidos = self.pedido_service.buscar_todos_pedidos()

        if pedidos:
            self._exibir_lista_pedidos(pedidos)

            pedido_id = self._selecionar_pedido()
            if pedido_id:
                pedido = self.pedido_service.buscar_pedido_por_id(pedido_id)
                if pedido:
                    print("\nDetalhes completos do pedido selecionado:")
                    self._exibir_pedido(pedido)
        else:
            print("Nenhum pedido cadastrado.")

    def registrar_pagamento(self):
        print("\n===== REGISTRAR PAGAMENTO =====")

        pedido_id = self._selecionar_pedido()
        if not pedido_id:
            return False

        return self._registrar_pagamento(pedido_id)

    def _registrar_pagamento(self, pedido_id: str) -> bool:
        pedido = self.pedido_service.buscar_pedido_por_id(pedido_id)
        if not pedido:
            print("Pedido não encontrado.")
            return False

        if (
            pedido.status != StatusPedido.AGUARDANDO_PAGAMENTO
            and pedido.status != StatusPedido.PENDENTE
        ):
            print(
                f"Pedido não está em um status que permite pagamento. Status atual: {pedido.status.value}"
            )
            return False

        print(f"\nValor total do pedido: R$ {pedido.total:.2f}")
        confirmar = input("\nConfirmar pagamento? (S/N): ")

        if confirmar.upper() != "S":
            print("Pagamento cancelado.")
            return False

        try:
            sucesso = self.pedido_service.registrar_pagamento(
                pedido_id=pedido_id,
                metodo="sistema",
                valor=pedido.total,
                detalhes={"observacao": "Pagamento simplificado"},
            )

            if sucesso:
                print("Pagamento confirmado com sucesso!")
                return True
            else:
                print("Erro ao registrar pagamento.")
                return False
        except Exception as e:
            print(f"Erro: {str(e)}")
            return False

    def cancelar_pedido(self):
        print("\n===== CANCELAR PEDIDO =====")

        pedido_id = self._selecionar_pedido()
        if not pedido_id:
            return False

        pedido = self.pedido_service.buscar_pedido_por_id(pedido_id)
        if not pedido:
            print("Pedido não encontrado.")
            return False

        print("\nPedido encontrado:")
        self._exibir_pedido(pedido)

        if pedido.status in [
            StatusPedido.ENVIADO,
            StatusPedido.ENTREGUE,
            StatusPedido.CANCELADO,
        ]:
            print(
                f"Não é possível cancelar este pedido. Status atual: {pedido.status.value}"
            )
            return False

        confirmacao = input(
            "\nTem certeza que deseja excluir permanentemente este pedido? (S/N): "
        )
        if confirmacao.upper() != "S":
            print("Operação cancelada.")
            return False

        try:
            sucesso = self.pedido_service.cancelar_pedido(pedido_id)
            if sucesso:
                print("Pedido excluído com sucesso!")
                return True
            else:
                print("Erro ao excluir pedido.")
                return False
        except Exception as e:
            print(f"Erro: {str(e)}")
            return False

    def _selecionar_usuario(self) -> Optional[str]:
        print("\nSelecione um usuário:")
        usuarios = self.usuario_service.listar_todos_usuarios()

        if not usuarios:
            print("Nenhum usuário cadastrado. Cadastre um usuário primeiro.")
            return None

        print("\nUsuários disponíveis:")
        for i, usuario in enumerate(usuarios, 1):
            print(f"{i}. {usuario.nome} {usuario.sobrenome} (CPF: {usuario.cpf})")

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

    def _montar_carrinho(self) -> List[Dict]:
        carrinho = []

        print("\nSelecione produtos para o carrinho (0 para finalizar):")

        while True:
            produtos = self.produto_service.listar_todos_produtos()

            if not produtos:
                print("Nenhum produto cadastrado. Cadastre produtos primeiro.")
                return []

            print("\nProdutos disponíveis:")
            for i, produto in enumerate(produtos, 1):
                print(
                    f"{i}. {produto.nome} - R$ {produto.preco:.2f} - Estoque: {produto.estoque}"
                )

            try:
                opcao_str = input(
                    "\nSelecione o número do produto (0 para finalizar): "
                )
                opcao = int(opcao_str)

                if opcao == 0:
                    break

                if 1 <= opcao <= len(produtos):
                    produto = produtos[opcao - 1]

                    produto_no_carrinho = False
                    for item in carrinho:
                        if item["produto_id"] == str(produto.id):
                            produto_no_carrinho = True
                            nova_quantidade_str = input(
                                f"Produto já no carrinho. Quantidade atual: {item['quantidade']}. Nova quantidade: "
                            )
                            try:
                                nova_quantidade = int(nova_quantidade_str)
                                if nova_quantidade <= 0:
                                    print("Removendo produto do carrinho.")
                                    carrinho.remove(item)
                                elif nova_quantidade > produto.estoque:
                                    print(
                                        f"Estoque insuficiente. Disponível: {produto.estoque}"
                                    )
                                else:
                                    item["quantidade"] = nova_quantidade
                                    print(f"Quantidade atualizada: {nova_quantidade}")
                            except:
                                print(
                                    "Quantidade inválida. Mantendo a quantidade atual."
                                )
                            break

                    if not produto_no_carrinho:
                        quantidade_str = input("Quantidade: ")
                        try:
                            quantidade = int(quantidade_str)
                            if quantidade <= 0:
                                print("Quantidade inválida.")
                            elif quantidade > produto.estoque:
                                print(
                                    f"Estoque insuficiente. Disponível: {produto.estoque}"
                                )
                            else:
                                carrinho.append(
                                    {
                                        "produto_id": str(produto.id),
                                        "quantidade": quantidade,
                                    }
                                )
                                print(
                                    f"Produto adicionado ao carrinho: {produto.nome} x {quantidade}"
                                )
                        except:
                            print("Quantidade inválida.")
                else:
                    print("Opção inválida!")
            except:
                print("Digite um número válido!")

            if carrinho:
                print("\nCarrinho atual:")
                total = Decimal("0.00")
                for item in carrinho:
                    produto = self.produto_service.buscar_produto_por_id(
                        item["produto_id"]
                    )
                    if produto:
                        subtotal = produto.preco * item["quantidade"]
                        total += subtotal
                        print(
                            f"- {produto.nome} x {item['quantidade']} = R$ {subtotal:.2f}"
                        )
                print(f"Total: R$ {total:.2f}")
            else:
                print("\nCarrinho vazio.")

        return carrinho

    def _coletar_endereco_entrega(self) -> Dict[str, str]:
        print("\n===== ENDEREÇO DE ENTREGA =====")

        usar_endereco_existente = input(
            "Deseja usar um endereço existente de um usuário? (S/N): "
        )

        if usar_endereco_existente.upper() == "S":
            usuario_id = self._selecionar_usuario()
            if usuario_id:
                usuario = self.usuario_service.buscar_usuario_por_id(usuario_id)
                if usuario and usuario.enderecos:
                    print("\nEndereços disponíveis:")
                    for i, endereco in enumerate(usuario.enderecos, 1):
                        print(
                            f"{i}. {endereco.rua}, {endereco.num} - {endereco.bairro}, {endereco.cidade}/{endereco.estado}"
                        )

                    try:
                        opcao_str = input("\nSelecione o número do endereço: ")
                        opcao = int(opcao_str)

                        if 1 <= opcao <= len(usuario.enderecos):
                            endereco = usuario.enderecos[opcao - 1]
                            return {
                                "rua": endereco.rua,
                                "numero": endereco.num,
                                "bairro": endereco.bairro,
                                "cidade": endereco.cidade,
                                "estado": endereco.estado,
                                "cep": endereco.cep,
                            }
                    except:
                        print("Opção inválida. Solicitando novo endereço.")
                else:
                    print(
                        "Usuário sem endereços cadastrados. Solicitando novo endereço."
                    )

        endereco = {
            "rua": input("Rua: "),
            "numero": input("Número: "),
            "complemento": input("Complemento (opcional): "),
            "bairro": input("Bairro: "),
            "cidade": input("Cidade: "),
            "estado": input("Estado: "),
            "cep": input("CEP: "),
        }

        return endereco

    def _obter_nome_usuario(self, usuario_id: str) -> str:
        usuario = self.usuario_service.buscar_usuario_por_id(usuario_id)
        if usuario:
            return f"{usuario.nome} {usuario.sobrenome}"
        return f"Usuário ID: {usuario_id}"

    def _exibir_pedido(self, pedido: Pedido):
        print(f"\nID do Pedido: {pedido.id}")
        print(f"Cliente: {self._obter_nome_usuario(str(pedido.usuario_id))}")
        print(f"Status: {pedido.status.value}")
        print(f"Data de Criação: {pedido.data_criacao}")
        print(f"Última Atualização: {pedido.data_atualizacao}")

        print("\nItens:")
        for item in pedido.itens:
            print(
                f"- {item.nome_produto} x {item.quantidade} = R$ {item.total_item:.2f}"
            )

        print(f"\nSubtotal: R$ {(pedido.total - pedido.frete):.2f}")
        print(f"Frete: R$ {pedido.frete:.2f}")
        print(f"Total: R$ {pedido.total:.2f}")

        print("\nEndereço de Entrega:")
        for chave, valor in pedido.endereco_entrega.items():
            if valor:
                print(f"{chave}: {valor}")

        if pedido.pagamento:
            print("\nPagamento:")
            print(f"Método: {pedido.pagamento.metodo}")
            print(f"Status: {pedido.pagamento.status}")
            print(f"Valor: R$ {pedido.pagamento.valor:.2f}")
            print(f"Data: {pedido.pagamento.data}")

            if pedido.pagamento.detalhes:
                print("Detalhes:")
                for chave, valor in pedido.pagamento.detalhes.items():
                    print(f"  {chave}: {valor}")

    def _exibir_lista_pedidos(self, pedidos: List[Pedido]):
        if not pedidos:
            print("Nenhum pedido encontrado.")
            return

        print(f"\nForam encontrados {len(pedidos)} pedidos:")

        for pedido in pedidos:
            print(f"\n--- Pedido {pedido.id} ---")
            print(f"Cliente: {self._obter_nome_usuario(str(pedido.usuario_id))}")
            print(f"Data: {pedido.data_criacao}")
            print(f"Status: {pedido.status.value}")
            print(f"Total: R$ {pedido.total:.2f}")
            print(f"Itens: {len(pedido.itens)} produtos")

            mostrar_mais = input("Mostrar detalhes completos? (S/N): ")
            if mostrar_mais.upper() == "S":
                self._exibir_pedido(pedido)

    def _selecionar_pedido(self) -> Optional[str]:
        pedidos = self.pedido_service.buscar_todos_pedidos()

        if not pedidos:
            print("Nenhum pedido cadastrado.")
            return None

        print("\nPedidos disponíveis:")
        for i, pedido in enumerate(pedidos, 1):
            usuario_nome = self._obter_nome_usuario(pedido.usuario_id)
            print(
                f"{i}. Pedido #{pedido.id} - Cliente: {usuario_nome} - Status: {pedido.status.value} - Valor: R$ {pedido.total:.2f}"
            )

        opcao_valida = False
        while not opcao_valida:
            try:
                opcao_str = input("\nSelecione o número do pedido (0 para cancelar): ")
                opcao = int(opcao_str)

                if opcao == 0:
                    print("Operação cancelada.")
                    return None

                if 1 <= opcao <= len(pedidos):
                    opcao_valida = True
                    return str(pedidos[opcao - 1].id)
                else:
                    print("Opção inválida!")
            except:
                print("Digite um número válido!")

        return None
