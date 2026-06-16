from abc import ABC, abstractmethod
from projeto import *

# Contexto global para armazenar o estado atual do sistema
class Sessao:
    def __init__(self, app: Marketplace, usuario_atual: Usuario):
        self.app = app
        self.usuario_atual = usuario_atual

# Interface do Command
class Command(ABC):
    def __init__(self, sessao: Sessao):
        self.sessao = sessao

    @abstractmethod
    def executar(self):
        pass

# Invoker (O menu que aciona os comandos)
class MenuInvoker:
    def __init__(self):
        self._comandos = {}

    def registrar(self, opcao: str, comando: Command):
        self._comandos[opcao] = comando

    def executar(self, opcao: str):
        if opcao in self._comandos:
            self._comandos[opcao].executar()
        else:
            print("Opção inválida.")

class VerCatalogoCommand(Command):
    def executar(self):
        print("\n--- CATÁLOGO ---")
        tem_produto = False
        for loja in self.sessao.app.lojas.values():
            for p in loja.catalogo: 
                print(f"Loja '{loja.nome_loja}': {p}")
                tem_produto = True
        if not tem_produto: print("Nenhum produto cadastrado.")

class ComprarCommand(Command):
    def executar(self):
        id_p = input("ID do produto: ")
        try:
            qtd = int(input("Quantidade: "))
            prod = next((p for loja in self.sessao.app.lojas.values() for p in loja.catalogo if p.id_produto == id_p), None)
            if prod: print(self.sessao.usuario_atual.carrinho.adicionar(prod, qtd))
            else: print("Não encontrado.")
        except ValueError: print("Erro: Quantidade deve ser um número.")

class VerCarrinhoCommand(Command):
    def executar(self):
        print("\n--- SEU CARRINHO ---")
        if not self.sessao.usuario_atual.carrinho.itens: print("Vazio.")
        else:
            for i in self.sessao.usuario_atual.carrinho.itens: 
                print(f"- {i.quantidade}x {i.produto.nome} (Adicionado por: R${i.preco_adicionado:.2f})")

class SimularMudancaPrecoCommand(Command):
    def executar(self):
        id_p = input("ID do produto para alterar preço no sistema: ")
        try:
            novo_p = float(input("Novo preço: "))
            prod = next((p for loja in self.sessao.app.lojas.values() for p in loja.catalogo if p.id_produto == id_p), None)
            if prod: 
                prod.alterar_preco(novo_p)
                print(f"Preço do '{prod.nome}' atualizado para R${novo_p:.2f} no catálogo!")
            else: print("Produto não encontrado.")
        except ValueError: print("Erro: Valor inválido.")

class FinalizarCompraCommand(Command):
    def executar(self):
        resultado = self.sessao.app.finalizar_compra(self.sessao.usuario_atual.id_usuario)
        print(resultado)
        if "DIVERGÊNCIA DE PREÇO" in resultado:
            limpar = input("\nDeseja esvaziar seu carrinho para atualizar os preços? (s/n): ")
            if limpar.lower() == 's':
                self.sessao.usuario_atual.carrinho.limpar()
                print("Carrinho esvaziado com sucesso!")

class VerHistoricoCommand(Command):
    def executar(self):
        print("\n--- MEUS PEDIDOS ---")
        if not self.sessao.usuario_atual.historico_pedidos: print("Nenhum pedido.")
        for ped in self.sessao.usuario_atual.historico_pedidos: print(ped)

class PublicarProdutoCommand(Command):
    def executar(self):
        print("\n--- PUBLICAR PRODUTO ---")
        if not isinstance(self.sessao.usuario_atual, UsuarioVendedor):
            print("Erro: Acesso Negado. Você precisa estar logado em uma conta de Vendedor.")
            return

        tipo_prod = input("Tipo do Produto [1] Físico | [2] Digital: ")
        id_prod = input("ID do Produto (Ex: 3): ")
        nome_prod = input("Nome: ")
        try:
            preco_prod = float(input("Preço (Ex: 50.00): "))
            estq_prod = int(input("Quantidade em estoque: "))
            
            if tipo_prod == "1":
                peso = float(input("Peso em KG (Ex: 1.5): "))
                fw = FlyweightFactory.get_flyweight(nome_prod, self.sessao.usuario_atual.loja.nome_loja, peso)
                novo_prod = ProdFisico(id_prod, preco_prod, estq_prod, fw)
            else:
                fw = FlyweightFactory.get_flyweight(nome_prod, self.sessao.usuario_atual.loja.nome_loja)
                novo_prod = ProdDigital(id_prod, preco_prod, estq_prod, fw)
                
            self.sessao.usuario_atual.loja.publicar_produto(novo_prod)
            print(f"Produto '{nome_prod}' publicado com sucesso na sua loja '{self.sessao.usuario_atual.loja.nome_loja}'!")
        except ValueError:
            print("Erro: Valores inválidos para preço, estoque ou peso.")

class ClonarProdutoCommand(Command):
    def executar(self):
        print("\n--- CLONAR PRODUTO ---")
        if not isinstance(self.sessao.usuario_atual, UsuarioVendedor):
            print("Erro: Acesso Negado. Você precisa estar logado em uma conta de Vendedor.")
            return

        id_origem = input("Digite o ID do produto que deseja clonar: ")
        prod_origem = next((p for p in self.sessao.usuario_atual.loja.catalogo if p.id_produto == id_origem), None)

        if prod_origem:
            novo_id = input("Qual será o ID do novo produto? ")
            novo_nome = input(f"Novo nome (Deixe vazio para manter o mesmo): ")
            novo_nome = novo_nome.strip() if novo_nome.strip() else None

            prod_clonado = prod_origem.clone(novo_id, novo_nome)
            self.sessao.usuario_atual.loja.publicar_produto(prod_clonado)
            print(f"Sucesso! O produto '{prod_clonado.nome}' foi clonado e já está no catálogo.")
        else:
            print("Erro: O produto informado não existe no seu catálogo.")

class GerenciarContaCommand(Command):
    def executar(self):
        print("\n--- GERENCIAR CONTA ---")
        print("[1] Fazer Login (Trocar de Usuário)")
        print("[2] Criar Nova Conta")
        acao_conta = input("Escolha a opção (1 ou 2): ")

        if acao_conta == "1":
            print("\n--- USUÁRIOS CADASTRADOS ---")
            for u in self.sessao.app.usuarios.values():
                t_str = "VIP" if isinstance(u, UsuarioVIP) else ("Vendedor" if isinstance(u, UsuarioVendedor) else "Normal")
                print(f"ID: {u.id_usuario} | Nome: {u.nome} | Tipo: {t_str}")
            
            id_escolhido = input("\nDigite o ID do usuário para fazer login (Ex: U01, V01): ")
            if id_escolhido in self.sessao.app.usuarios:
                self.sessao.usuario_atual = self.sessao.app.usuarios[id_escolhido]
                self.sessao.usuario_atual.login()
                print(f"Login realizado com sucesso! Bem-vindo de volta, {self.sessao.usuario_atual.nome}.")
            else:
                print("Erro: Usuário não encontrado no sistema.")

        elif acao_conta == "2":
            print("\n--- CADASTRO DE NOVO USUÁRIO ---")
            print("Tipos de Conta:\n[1] Comprador Normal\n[2] Comprador VIP (10% Desconto)\n[3] Vendedor (Pode publicar produtos)")
            tipo_escolha = input("Escolha o tipo (1/2/3): ")
            
            nome_u = input("Nome do novo usuário: ")
            novo_id = "U" + str(len(self.sessao.app.usuarios) + 1)
            
            if tipo_escolha == "2":
                self.sessao.usuario_atual = self.sessao.app.registrar_usuario(novo_id, nome_u, f"{nome_u.lower()}@email.com", tipo="vip")
            elif tipo_escolha == "3":
                novo_id = "V" + str(len(self.sessao.app.usuarios) + 1)
                nome_loja = input("Nome da sua Loja: ")
                self.sessao.usuario_atual = self.sessao.app.registrar_usuario(novo_id, nome_u, f"{nome_u.lower()}@email.com", tipo="vendedor", nome_loja=nome_loja)
            else:
                self.sessao.usuario_atual = self.sessao.app.registrar_usuario(novo_id, nome_u, f"{nome_u.lower()}@email.com", tipo="normal")
                
            self.sessao.usuario_atual.login()
            print(f"Conta criada! Você está logado automaticamente como: {self.sessao.usuario_atual.nome}")
        else:
            print("Opção inválida.")