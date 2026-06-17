from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from commands import *

app_marketplace = Marketplace("NEW Shopee API")

# Dados Iniciais (Mock)
vendedor_oficial = app_marketplace.registrar_usuario(
    "V01", "Vendedor Ricardo", "vendedor@email.com", "senha123", "vendedor", "NEW Shopee"
)
fw1 = FlyweightFactory.get_flyweight("Fone Bluetooth", "NEW Shopee", peso_kg=0.5)
fw2 = FlyweightFactory.get_flyweight("Ebook Python", "NEW Shopee")

p1 = ProdFisico("1", 100.00, 5, fw1)
p2 = ProdDigital("101", 45.00, 1000, fw2)
vendedor_oficial.loja.publicar_produto(p1)
vendedor_oficial.loja.publicar_produto(p2)

# Exige o header "X-User-Id" para identificar quem está fazendo a requisição
def get_sessao(x_user_id: str = Header(...)):
    usuario = app_marketplace.usuarios.get(x_user_id)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado. Faça login.")
    if not usuario.is_logado():
        raise HTTPException(status_code=401, detail="Usuário não está logado.")
    return SessaoAPI(app_marketplace, usuario)

api_app = FastAPI(title="NEW Shopee API", description="API usando Design Pattern Command")
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (great for local development)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers (Crucial for your "X-User-Id" header!)
)

@api_app.post("/auth/cadastro")
def cadastrar(dados: CadastroSchema):
    sessao_anonima = SessaoAPI(app_marketplace)
    novo_id = ("V" if dados.tipo == "3" else "U") + str(len(app_marketplace.usuarios) + 1)
    
    if dados.tipo == "3":
        user = app_marketplace.registrar_usuario(novo_id, dados.nome, f"{dados.nome}@email.com", dados.senha, "vendedor", dados.nome_loja)
    else:
        tipo_str = "vip" if dados.tipo == "2" else "normal"
        user = app_marketplace.registrar_usuario(novo_id, dados.nome, f"{dados.nome}@email.com", senha=dados.senha, tipo=tipo_str)
        
    user.login()
    return {"mensagem": "Cadastro realizado com sucesso", "x_user_id": user.id_usuario}

@api_app.post("/auth/login")
def login(dados: LoginSchema):
    usuario = app_marketplace.usuarios.get(dados.id_usuario)
    if usuario and usuario.senha == dados.senha:
        usuario.login()
        tipo = 0
        class_name = type(usuario).__name__
        if (class_name == 'Usuario'):
            tipo = 1
        if (class_name == 'UsuarioVIP'):
            tipo = 2
        if (class_name == 'UsuarioVendedor'):
            tipo = 3
        return {"mensagem": f"Bem vindo, {usuario.nome}", "x_user_id": usuario.id_usuario, 'type': str(tipo)}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

@api_app.get("/catalogo")
def ver_catalogo():
    # Catálogo é público, não exige header de usuário
    sessao_anonima = SessaoAPI(app_marketplace)
    comando = VerCatalogoCommand(sessao_anonima)
    return comando.executar()

@api_app.post("/carrinho")
def adicionar_ao_carrinho(dados: CompraSchema, sessao: SessaoAPI = Depends(get_sessao)):
    comando = ComprarCommand(sessao, dados)
    return comando.executar()

@api_app.get("/carrinho")
def listar_carrinho(sessao: SessaoAPI = Depends(get_sessao)):
    comando = VerCarrinhoCommand(sessao)
    return comando.executar()

@api_app.post("/checkout")
def finalizar_compra(sessao: SessaoAPI = Depends(get_sessao)):
    comando = FinalizarCompraCommand(sessao)
    return comando.executar()

@api_app.post("/vendedor/produto/fisico")
def publicar_produto_fisico(dados: ProdutoFisicoSchema, sessao: SessaoAPI = Depends(get_sessao)):
    comando = PublicarProdutoCommand(sessao, dados, tipo_produto="fisico")
    return comando.executar()

@api_app.post("/vendedor/produto/digital")
def publicar_produto_digital(dados: ProdutoDigitalSchema, sessao: SessaoAPI = Depends(get_sessao)):
    comando = PublicarProdutoCommand(sessao, dados, tipo_produto="digital")
    return comando.executar()

@api_app.put("/vendedor/produto/preco")
def simular_mudanca_preco(dados: MudancaPrecoSchema, sessao: SessaoAPI = Depends(get_sessao)):
    """Permite a um vendedor alterar o preço de um de seus produtos."""
    comando = SimularMudancaPrecoCommand(sessao, dados)
    return comando.executar()


@api_app.get("/usuario/historico")
def ver_historico_pedidos(sessao: SessaoAPI = Depends(get_sessao)):
    """Retorna a lista de compras concluídas do usuário logado."""
    comando = VerHistoricoCommand(sessao)
    return comando.executar()


@api_app.post("/vendedor/produto/clonar")
def clonar_produto(dados: ClonarProdutoSchema, sessao: SessaoAPI = Depends(get_sessao)):
    """Clona um produto existente na loja do vendedor utilizando Prototype."""
    comando = ClonarProdutoCommand(sessao, dados)
    return comando.executar()