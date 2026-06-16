from datetime import datetime
from abc import ABC, abstractmethod

class ProdutoFlyweight:
    def __init__(self, nome, loja_nome, peso_kg=None):
        self._nome = nome
        self._loja_nome = loja_nome
        self._peso_kg = peso_kg

    @property
    def nome(self):
        return self._nome

    @property
    def loja_nome(self):
        return self._loja_nome
        
    @property
    def peso_kg(self):
        return self._peso_kg


class FlyweightFactory:
    _flyweights = {}

    @classmethod
    def get_flyweight(cls, nome, loja_nome, peso_kg=None):
        # A chave de cache é a combinação dos atributos intrínsecos
        chave = (nome, loja_nome, peso_kg)
        if chave not in cls._flyweights:
            cls._flyweights[chave] = ProdutoFlyweight(nome, loja_nome, peso_kg)
        return cls._flyweights[chave]

    @classmethod
    def contar_flyweights(cls):
        return len(cls._flyweights)

class Produto(ABC):
    def __init__(self, id_produto, preco, estoque, flyweight: ProdutoFlyweight):
        self.id_produto = id_produto
        self.flyweight = flyweight  # Referência ao estado intrínseco
        
        # Encapsulamento: Atributos privados (Estado Extrínseco)
        self.__preco = preco
        self.__estoque = estoque

    # Propriedades para acessar o estado compartilhado (Flyweight) de forma transparente
    @property
    def nome(self):
        return self.flyweight.nome
        
    @property
    def loja_nome(self):
        return self.flyweight.loja_nome
        
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

    # Contratos Obrigatórios
    @abstractmethod
    def processar_entrega(self):
        pass

    @abstractmethod
    def clone(self, novo_id_produto, novo_nome=None):
        pass

    def __str__(self):
        status = "Disponível" if self.__estoque > 0 else "Indisponível"
        return f"[{self.id_produto}] {self.nome} - R${self.__preco:.2f} ({status}: {self.__estoque} un.)"


class ProdFisico(Produto):
    def __init__(self, id_produto, preco, estoque, flyweight: ProdutoFlyweight):
        super().__init__(id_produto, preco, estoque, flyweight) 
        
    @property
    def peso_kg(self):
        return self.flyweight.peso_kg
        
    def calcular_frete(self):
        return self.peso_kg * 10.00 

    def processar_entrega(self):
        return f"Saída para transportadora. Frete: R${self.calcular_frete():.2f}"

    def clone(self, novo_id_produto, novo_nome=None):
        fw_usado = self.flyweight
        # Se alterou o nome durante o clone, precisamos de um novo flyweight (ou reaproveitar outro existente)
        if novo_nome:
            fw_usado = FlyweightFactory.get_flyweight(novo_nome, self.loja_nome, self.peso_kg)
            
        return ProdFisico(
            id_produto=novo_id_produto,
            preco=self.get_preco(),
            estoque=self.get_estoque(),
            flyweight=fw_usado
        )

    def __str__(self):
        return super().__str__() + f" [Peso: {self.peso_kg}kg]"


class ProdDigital(Produto):
    def __init__(self, id_produto, preco, estoque, flyweight: ProdutoFlyweight):
        super().__init__(id_produto, preco, estoque, flyweight)
        
    def gerar_link(self): 
        nome_url = self.nome.lower().replace(" ", "-")
        return f"https://newshopee.com.br/arquivos/{self.id_produto}/{nome_url}"

    def processar_entrega(self):
        return f"Link para download liberado: {self.gerar_link()}"

    def clone(self, novo_id_produto, novo_nome=None):
        fw_usado = self.flyweight
        if novo_nome:
            fw_usado = FlyweightFactory.get_flyweight(novo_nome, self.loja_nome)

        return ProdDigital(
            id_produto=novo_id_produto,
            preco=self.get_preco(),
            estoque=self.get_estoque(),
            flyweight=fw_usado
        )

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


class Loja:
    def __init__(self, nome_loja, vendedor_nome):
        self.nome_loja = nome_loja
        self.vendedor_nome = vendedor_nome
        self.catalogo = []
        
    def publicar_produto(self, produto):
        self.catalogo.append(produto)
        return produto


class UsuarioVendedor(Usuario):
    def __init__(self, id_usuario, nome, email, nome_loja):
        super().__init__(id_usuario, nome, email)
        self.loja = Loja(nome_loja, self.nome)


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