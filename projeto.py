from datetime import datetime
from abc import ABC, abstractmethod  

# Produto agora herda de ABC (Abstract Base Class)
class Produto(ABC):
    def __init__(self, id_produto, nome, preco, estoque, loja_nome):
        self.id_produto = id_produto
        self.nome = nome
        self.loja_nome = loja_nome
        # Encapsulamento: Atributos privados
        self.__preco = preco
        self.__estoque = estoque
        
    def get_preco(self):
        return self.__preco
        
    def get_estoque(self):
        return self.__estoque

    def is_disponivel(self, quantidade=1):
        return self.__estoque >= quantidade
    
    def reduzir_estoque(self, quantidade):
        if self.is_disponivel(quantidade):
            self.__estoque -= quantidade
            return True
        return False 

    def alterar_preco(self, novo_preco):
        if novo_preco > 0:
            self.__preco = novo_preco
        else:
            print("Erro: O preço não pode ser negativo!")

    # Contrato Obrigatório
    @abstractmethod
    def processar_entrega(self):
        pass

    def __str__(self):
        status = "Disponível" if self.__estoque > 0 else "Indisponível"
        return f"[{self.id_produto}] {self.nome} - R${self.__preco:.2f} ({status}: {self.__estoque} un.)"

class ProdFisico(Produto):
    def __init__(self, id_produto, nome, preco, estoque, loja_nome, peso_kg):
        super().__init__(id_produto, nome, preco, estoque, loja_nome) 
        self.peso_kg = peso_kg 
        
    def calcular_frete(self):
        return self.peso_kg * 10.00 

    def processar_entrega(self):
        return f"Saída para transportadora. Frete: R${self.calcular_frete():.2f}"

    def __str__(self):
        return super().__str__() + f" [Peso: {self.peso_kg}kg]"

class ProdDigital(Produto):
    def __init__(self, id_produto, nome, preco, estoque, loja_nome):
        super().__init__(id_produto, nome, preco, estoque, loja_nome)
        
    def gerar_link(self): 
        nome_url = self.nome.lower().replace(" ", "-")
        return f"https://newshopee.com.br/arquivos/{self.id_produto}/{nome_url}"

    def processar_entrega(self):
        return f"Link para download liberado: {self.gerar_link()}"

    def __str__(self):
        return super().__str__() + " [PRODUTO DIGITAL]"

class ItemCarrinho:
    def __init__(self, produto: Produto, quantidade: int):
        self.produto = produto
        self.quantidade = quantidade
        self.preco_adicionado = produto.get_preco() 
        
    def get_subtotal(self):
        return self.preco_adicionado * self.quantidade

class Carrinho:
    def __init__(self):
        self.itens = []
        
    def adicionar(self, produto: Produto, quantidade: int):
        for item in self.itens:
            if item.produto.id_produto == produto.id_produto:
                nova_qtd_total = item.quantidade + quantidade
                if not produto.is_disponivel(nova_qtd_total):
                    return f"Erro: Estoque insuficiente. Você já tem {item.quantidade} no carrinho e tentou adicionar mais {quantidade}."
                
                item.quantidade = nova_qtd_total
                return f"Quantidade atualizada: Agora você tem {item.quantidade}x {produto.nome} no carrinho."

        if not produto.is_disponivel(quantidade):
            return f"Erro: Estoque insuficiente para {produto.nome}."
            
        item = ItemCarrinho(produto, quantidade)
        self.itens.append(item)
        return f"{quantidade}x {produto.nome} adicionado ao carrinho por R${produto.get_preco():.2f} cada."

    def limpar(self):
        self.itens.clear()

class Pedido:
    def __init__(self, id_pedido, itens, total):
        self.id_pedido = id_pedido
        self.itens = itens
        self.total = total
        self.data = datetime.now()
        self.status = "confirmado"

    def __str__(self):
        return f"Pedido #{self.id_pedido} ({self.data.strftime('%d/%m/%Y %H:%M')}) - Total Final: R${self.total:.2f}"

class Usuario:
    def __init__(self, id_usuario, nome, email):
        self.id_usuario = id_usuario
        self.nome = nome
        self.email = email
        self.__logado = False
        self.carrinho = Carrinho()
        self.historico_pedidos = []
        
    def login(self):
        self.__logado = True
        
    def is_logado(self):
        return self.__logado

class UsuarioVIP(Usuario):
    def __init__(self, id_usuario, nome, email):
        super().__init__(id_usuario, nome, email)
        self.taxa_desconto = 0.10 

    def aplicar_desconto(self, valor_total):
        return valor_total * (1 - self.taxa_desconto)

class UsuarioVendedor(Usuario):
    def __init__(self, id_usuario, nome, email, nome_loja):
        super().__init__(id_usuario, nome, email)
        self.loja = Loja(nome_loja, self.nome)

class Loja:
    def __init__(self, nome_loja, vendedor_nome):
        self.nome_loja = nome_loja
        self.vendedor_nome = vendedor_nome
        self.catalogo = []
        
    def publicar_produto(self, produto):
        self.catalogo.append(produto)
        return produto

class Marketplace:
    def __init__(self, nome):
        self.nome = nome
        self.usuarios = {}
        self.lojas = {}
        self.__contador_pedidos = 1000
        
    def registrar_usuario(self, id_user, nome, email, tipo="normal", nome_loja=""):
        if tipo == "vip":
            user = UsuarioVIP(id_user, nome, email)
        elif tipo == "vendedor":
            user = UsuarioVendedor(id_user, nome, email, nome_loja)
            self.lojas[nome_loja] = user.loja
        else:
            user = Usuario(id_user, nome, email)
            
        self.usuarios[id_user] = user
        return user

    def finalizar_compra(self, id_usuario):
        usuario = self.usuarios.get(id_usuario)
        if not usuario or not usuario.is_logado():
            return "Erro: Usuário precisa estar logado."
        if not usuario.carrinho.itens:
            return "Erro: Carrinho vazio."

        total_pedido = 0
        for item in usuario.carrinho.itens:
            if not item.produto.is_disponivel(item.quantidade):
                return f"BLOQUEIO: O produto '{item.produto.nome}' ficou sem estoque."
            if item.preco_adicionado != item.produto.get_preco(): 
                return f"DIVERGÊNCIA DE PREÇO: O valor de '{item.produto.nome}' mudou no sistema."
            
            total_pedido += item.get_subtotal()

        resumo_vip = ""
        if isinstance(usuario, UsuarioVIP):
            total_pedido = usuario.aplicar_desconto(total_pedido)
            resumo_vip = "\nBENEFÍCIO VIP: 10% de desconto aplicado!"

        detalhes_entrega = "\n--- INFORMAÇÕES DE ENVIO ---"
        for item in usuario.carrinho.itens:
            item.produto.reduzir_estoque(item.quantidade)
            detalhes_entrega += f"\n* {item.produto.nome}: {item.produto.processar_entrega()}"

        novo_pedido = Pedido(self.__contador_pedidos, list(usuario.carrinho.itens), total_pedido)
        usuario.historico_pedidos.append(novo_pedido)
        self.__contador_pedidos += 1
        usuario.carrinho.limpar()
        
        return f"Sucesso! {novo_pedido}{resumo_vip}{detalhes_entrega}"

if __name__ == "__main__":
    app = Marketplace("NEW Shopee")
    
    # Criando o Vendedor Inicial do Sistema
    vendedor_oficial = app.registrar_usuario("V01", "Vendedor Ricardo", "vendedor@email.com", tipo="vendedor", nome_loja="NEW Shopee")
    
    # Produtos Iniciais
    p1 = ProdFisico("1", "Fone Bluetooth", 100.00, 5, "NEW Shopee", 0.5)
    p2 = ProdDigital("101", "Ebook Python", 45.00, 1000, "NEW Shopee")
    vendedor_oficial.loja.publicar_produto(p1)
    vendedor_oficial.loja.publicar_produto(p2)

    # Início com Usuário Normal (Comprador)
    usuario_atual = app.registrar_usuario("U01", "Ricardo", "ricardo@email.com")
    usuario_atual.login()

    while True:
        if isinstance(usuario_atual, UsuarioVIP): tipo_u = "VIP"
        elif isinstance(usuario_atual, UsuarioVendedor): tipo_u = "VENDEDOR"
        else: tipo_u = "Normal"
            
        print(f"\n" + "="*50)
        print(f"USUÁRIO LOGADO: {usuario_atual.nome} ({tipo_u})")
        print("1 - Ver Catálogo | 2 - Comprar | 3 - Ver Carrinho")
        print("4 - Simular Mudança de Preço | 5 - Finalizar Compra | 6 - Histórico")
        print("7 - Publicar Produto (Apenas Vendedores)")
        print("9 - Gerenciar Conta (Trocar/Criar) | 0 - Sair")
        print("="*50)
        
        opcao = input("Opção: ")
        
        if opcao == "0": break
            
        elif opcao == "1":
            print("\n--- CATÁLOGO ---")
            tem_produto = False
            for loja in app.lojas.values():
                for p in loja.catalogo: 
                    print(f"Loja '{loja.nome_loja}': {p}")
                    tem_produto = True
            if not tem_produto: print("Nenhum produto cadastrado.")
                
        elif opcao == "2":
            id_p = input("ID do produto: ")
            try:
                qtd = int(input("Quantidade: "))
                prod = next((p for loja in app.lojas.values() for p in loja.catalogo if p.id_produto == id_p), None)
                if prod: print(usuario_atual.carrinho.adicionar(prod, qtd))
                else: print("Não encontrado.")
            except ValueError: print("Erro: Quantidade deve ser um número.")
                
        elif opcao == "3":
            print("\n--- SEU CARRINHO ---")
            if not usuario_atual.carrinho.itens: print("Vazio.")
            else:
                for i in usuario_atual.carrinho.itens: 
                    print(f"- {i.quantidade}x {i.produto.nome} (Adicionado por: R${i.preco_adicionado:.2f})")
                    
        elif opcao == "4":
            id_p = input("ID do produto para alterar preço no sistema: ")
            try:
                novo_p = float(input("Novo preço: "))
                prod = next((p for loja in app.lojas.values() for p in loja.catalogo if p.id_produto == id_p), None)
                if prod: 
                    prod.alterar_preco(novo_p)
                    print(f"Preço do '{prod.nome}' atualizado para R${novo_p:.2f} no catálogo!")
                else: print("Produto não encontrado.")
            except ValueError: print("Erro: Valor inválido.")
                
        elif opcao == "5":
            resultado = app.finalizar_compra(usuario_atual.id_usuario)
            print(resultado)
            if "DIVERGÊNCIA DE PREÇO" in resultado:
                limpar = input("\nDeseja esvaziar seu carrinho para atualizar os preços? (s/n): ")
                if limpar.lower() == 's':
                    usuario_atual.carrinho.limpar()
                    print("Carrinho esvaziado com sucesso!")
            
        elif opcao == "6":
            print("\n--- MEUS PEDIDOS ---")
            if not usuario_atual.historico_pedidos: print("Nenhum pedido.")
            for ped in usuario_atual.historico_pedidos: print(ped)
            
        elif opcao == "7":
            print("\n--- PUBLICAR PRODUTO ---")
            if not isinstance(usuario_atual, UsuarioVendedor):
                print("Erro: Acesso Negado. Você precisa estar logado em uma conta de Vendedor.")
            else:
                tipo_prod = input("Tipo do Produto [1] Físico | [2] Digital: ")
                id_prod = input("ID do Produto (Ex: 3): ")
                nome_prod = input("Nome: ")
                try:
                    preco_prod = float(input("Preço (Ex: 50.00): "))
                    estq_prod = int(input("Quantidade em estoque: "))
                    
                    if tipo_prod == "1":
                        peso = float(input("Peso em KG (Ex: 1.5): "))
                        novo_prod = ProdFisico(id_prod, nome_prod, preco_prod, estq_prod, usuario_atual.loja.nome_loja, peso)
                    else:
                        novo_prod = ProdDigital(id_prod, nome_prod, preco_prod, estq_prod, usuario_atual.loja.nome_loja)
                        
                    usuario_atual.loja.publicar_produto(novo_prod)
                    print(f"Produto '{nome_prod}' publicado com sucesso na sua loja '{usuario_atual.loja.nome_loja}'!")
                except ValueError:
                    print("Erro: Valores inválidos para preço, estoque ou peso.")

        elif opcao == "9":
            print("\n--- GERENCIAR CONTA ---")
            print("[1] Fazer Login (Trocar de Usuário)")
            print("[2] Criar Nova Conta")
            acao_conta = input("Escolha a opção (1 ou 2): ")

            if acao_conta == "1":
                print("\n--- USUÁRIOS CADASTRADOS ---")
                for u in app.usuarios.values():
                    t_str = "VIP" if isinstance(u, UsuarioVIP) else ("Vendedor" if isinstance(u, UsuarioVendedor) else "Normal")
                    print(f"ID: {u.id_usuario} | Nome: {u.nome} | Tipo: {t_str}")
                
                id_escolhido = input("\nDigite o ID do usuário para fazer login (Ex: U01, V01): ")
                if id_escolhido in app.usuarios:
                    usuario_atual = app.usuarios[id_escolhido]
                    usuario_atual.login()
                    print(f"Login realizado com sucesso! Bem-vindo de volta, {usuario_atual.nome}.")
                else:
                    print("Erro: Usuário não encontrado no sistema.")

            elif acao_conta == "2":
                print("\n--- CADASTRO DE NOVO USUÁRIO ---")
                print("Tipos de Conta:")
                print("[1] Comprador Normal")
                print("[2] Comprador VIP (10% Desconto)")
                print("[3] Vendedor (Pode publicar produtos)")
                tipo_escolha = input("Escolha o tipo (1/2/3): ")
                
                nome_u = input("Nome do novo usuário: ")
                novo_id = "U" + str(len(app.usuarios) + 1)
                
                if tipo_escolha == "2":
                    usuario_atual = app.registrar_usuario(novo_id, nome_u, f"{nome_u.lower()}@email.com", tipo="vip")
                elif tipo_escolha == "3":
                    novo_id = "V" + str(len(app.usuarios) + 1)
                    nome_loja = input("Nome da sua Loja: ")
                    usuario_atual = app.registrar_usuario(novo_id, nome_u, f"{nome_u.lower()}@email.com", tipo="vendedor", nome_loja=nome_loja)
                else:
                    usuario_atual = app.registrar_usuario(novo_id, nome_u, f"{nome_u.lower()}@email.com", tipo="normal")
                    
                usuario_atual.login()
                print(f"Conta criada! Você está logado automaticamente como: {usuario_atual.nome}")
            
            else:
                print("Opção inválida.")
