from abc import ABC, abstractmethod
from fastapi import HTTPException

from projeto import *
from schemas import *

class SessaoAPI:
    def __init__(self, app: Marketplace, usuario_atual: Usuario = None):
        self.app = app
        self.usuario_atual = usuario_atual

class CommandAPI(ABC):
    def __init__(self, sessao: SessaoAPI):
        self.sessao = sessao

    @abstractmethod
    def executar(self) -> dict:
        pass

class VerCatalogoCommand(CommandAPI):
    def executar(self):
        catalogo = []
        for loja in self.sessao.app.lojas.values():
            for p in loja.catalogo:
                catalogo.append({"loja": loja.nome_loja, "id": p.id_produto, "nome": p.nome, "preco": p.get_preco(), "estoque": p.get_estoque()})
        return {"catalogo": catalogo}

class ComprarCommand(CommandAPI):
    def __init__(self, sessao: SessaoAPI, dados_compra: CompraSchema):
        super().__init__(sessao)
        self.dados = dados_compra

    def executar(self):
        prod = next((p for loja in self.sessao.app.lojas.values() for p in loja.catalogo if p.id_produto == self.dados.id_produto), None)
        if not prod:
            raise HTTPException(status_code=404, detail="Produto não encontrado.")
        
        msg = self.sessao.usuario_atual.carrinho.adicionar(prod, self.dados.quantidade)
        if "Erro" in msg:
            raise HTTPException(status_code=400, detail=msg)
        return {"mensagem": msg}

class VerCarrinhoCommand(CommandAPI):
    def executar(self):
        itens = []
        for i in self.sessao.usuario_atual.carrinho.itens:
            itens.append({"produto": i.produto.nome, "quantidade": i.quantidade, "subtotal": i.get_subtotal()})
        return {"itens": itens, "total_itens": len(itens)}

class FinalizarCompraCommand(CommandAPI):
    def executar(self):
        resultado = self.sessao.app.finalizar_compra(self.sessao.usuario_atual.id_usuario)
        if "Erro" in resultado or "BLOQUEIO" in resultado or "DIVERGÊNCIA" in resultado:
            raise HTTPException(status_code=400, detail=resultado)
        return {"mensagem": resultado}

class PublicarProdutoCommand(CommandAPI):
    def __init__(self, sessao: SessaoAPI, dados, tipo_produto: str):
        super().__init__(sessao)
        self.dados = dados
        self.tipo_produto = tipo_produto

    def executar(self):
        if not isinstance(self.sessao.usuario_atual, UsuarioVendedor):
            raise HTTPException(status_code=403, detail="Acesso restrito para vendedores.")

        fw = FlyweightFactory.get_flyweight(self.dados.nome, self.sessao.usuario_atual.loja.nome_loja, getattr(self.dados, 'peso', None))
        
        if self.tipo_produto == "fisico":
            novo_prod = ProdFisico(self.dados.id_produto, self.dados.preco, self.dados.estoque, fw)
        else:
            novo_prod = ProdDigital(self.dados.id_produto, self.dados.preco, self.dados.estoque, fw)
            
        self.sessao.usuario_atual.loja.publicar_produto(novo_prod)
        return {"mensagem": f"Produto '{self.dados.nome}' publicado com sucesso!"}
    

class SimularMudancaPrecoCommand(CommandAPI):
    def __init__(self, sessao: SessaoAPI, dados: MudancaPrecoSchema):
        super().__init__(sessao)
        self.dados = dados

    def executar(self):
        # Apenas vendedores podem alterar preços de produtos de sua própria loja
        if not isinstance(self.sessao.usuario_atual, UsuarioVendedor):
            raise HTTPException(status_code=403, detail="Acesso restrito para vendedores.")
        
        # Busca o produto no catálogo da loja do vendedor atual
        prod = next((p for p in self.sessao.usuario_atual.loja.catalogo if p.id_produto == self.dados.id_produto), None)
        
        if not prod:
            raise HTTPException(status_code=404, detail="Produto não encontrado na sua loja.")
            
        preco_antigo = prod.get_preco()
        prod.set_preco(self.dados.novo_preco)
        
        return {
            "mensagem": f"Preço do produto '{prod.nome}' alterado com sucesso.",
            "produto_id": prod.id_produto,
            "preco_antigo": preco_antigo,
            "preco_novo": prod.get_preco()
        }


class VerHistoricoCommand(CommandAPI):
    def executar(self):
        # Retorna o histórico de pedidos do usuário atual formatado em JSON
        historico_pedidos = []
        for pedido in self.sessao.usuario_atual.historico_pedidos:
            itens_pedido = []
            for item in pedido.itens:
                itens_pedido.append({
                    "produto": item.produto.nome,
                    "quantidade": item.quantidade,
                    "preco_unitario": item.preco_adicionado
                })
            
            historico_pedidos.append({
                "id_pedido": pedido.id_pedido,
                "data": pedido.data.strftime("%Y-%m-%d %H:%M:%S"),
                "itens": itens_pedido,
                "total": pedido.total
            })
            
        return {
            "usuario": self.sessao.usuario_atual.nome,
            "total_pedidos": len(historico_pedidos),
            "historico": historico_pedidos
        }


class ClonarProdutoCommand(CommandAPI):
    def __init__(self, sessao: SessaoAPI, dados: ClonarProdutoSchema):
        super().__init__(sessao)
        self.dados = dados

    def executar(self):
        if not isinstance(self.sessao.usuario_atual, UsuarioVendedor):
            raise HTTPException(status_code=403, detail="Acesso restrito para vendedores.")
            
        loja = self.sessao.usuario_atual.loja
        
        # Encontra o produto original para clonar
        prod_original = next((p for p in loja.catalogo if p.id_produto == self.dados.id_origem), None)
        if not prod_original:
            raise HTTPException(status_code=404, detail="Produto original não encontrado na sua loja.")
            
        # Verifica se o novo ID já está em uso na loja
        if any(p.id_produto == self.dados.novo_id for p in loja.catalogo):
            raise HTTPException(status_code=400, detail="O novo ID informado já está em uso.")
            
        # Executa o padrão Prototype (.clone()) existente em seu projeto.py
        try:
            clone_prod = prod_original.clone(self.dados.novo_id)
            if self.dados.novo_nome:
                # Se um novo nome foi enviado, atualiza usando o FlyweightFactory
                fw_atualizado = FlyweightFactory.get_flyweight(
                    self.dados.novo_nome, 
                    loja.nome_loja, 
                    getattr(prod_original.flyweight, 'peso_kg', None)
                )
                clone_prod.flyweight = fw_atualizado
                
            loja.publicar_produto(clone_prod)
            return {
                "mensagem": f"Produto clonado com sucesso através do padrão Prototype.",
                "original": {"id": prod_original.id_produto, "nome": prod_original.nome},
                "clone": {"id": clone_prod.id_produto, "nome": clone_prod.nome, "preco": clone_prod.get_preco()}
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao clonar o produto: {str(e)}")