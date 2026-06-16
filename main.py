from menu import *

if __name__ == "__main__":
    app = Marketplace("NEW Shopee")
    
    vendedor_oficial = app.registrar_usuario("V01", "Vendedor Ricardo", "vendedor@email.com", tipo="vendedor", nome_loja="NEW Shopee")
    fw1 = FlyweightFactory.get_flyweight("Fone Bluetooth", "NEW Shopee", peso_kg=0.5)
    fw2 = FlyweightFactory.get_flyweight("Ebook Python", "NEW Shopee")
    
    p1 = ProdFisico("1", 100.00, 5, fw1)
    p2 = ProdDigital("101", 45.00, 1000, fw2)
    vendedor_oficial.loja.publicar_produto(p1)
    vendedor_oficial.loja.publicar_produto(p2)

    usuario_inicial = app.registrar_usuario("U01", "Ricardo", "ricardo@email.com")
    usuario_inicial.login()

    # Criando o contexto (Sessão) e o Menu
    sessao = Sessao(app, usuario_inicial)
    menu = MenuInvoker()

    # Registrando os comandos de forma limpa
    menu.registrar("1", VerCatalogoCommand(sessao))
    menu.registrar("2", ComprarCommand(sessao))
    menu.registrar("3", VerCarrinhoCommand(sessao))
    menu.registrar("4", SimularMudancaPrecoCommand(sessao))
    menu.registrar("5", FinalizarCompraCommand(sessao))
    menu.registrar("6", VerHistoricoCommand(sessao))
    menu.registrar("7", PublicarProdutoCommand(sessao))
    menu.registrar("8", ClonarProdutoCommand(sessao))
    menu.registrar("9", GerenciarContaCommand(sessao))

    while True:
        # Acessamos o usuário atual sempre através da sessão, pois ele pode ter mudado no comando 9
        u_atual = sessao.usuario_atual
        if isinstance(u_atual, UsuarioVIP): tipo_u = "VIP"
        elif isinstance(u_atual, UsuarioVendedor): tipo_u = "VENDEDOR"
        else: tipo_u = "Normal"
            
        print(f"\n" + "="*50)
        print(f"USUÁRIO LOGADO: {u_atual.nome} ({tipo_u})")
        print("1 - Ver Catálogo | 2 - Comprar | 3 - Ver Carrinho")
        print("4 - Simular Mudança de Preço | 5 - Finalizar Compra | 6 - Histórico")
        print("7 - Publicar Produto | 8 - Clonar Produto (Apenas Vendedores)")
        print("9 - Gerenciar Conta (Trocar/Criar) | 0 - Sair")
        print("="*50)
        
        opcao = input("Opção: ")
        
        if opcao == "0": 
            break
        
        menu.executar(opcao)