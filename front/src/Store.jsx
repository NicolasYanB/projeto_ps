import { useState, useEffect } from 'react';
import { api } from './api';

export default function Store({ userId }) {
  const [catalogo, setCatalogo] = useState([]);
  const [carrinho, setCarrinho] = useState(null);

  const carregarDados = async () => {
    try {
      const catRes = await api.getCatalogo();
      setCatalogo(catRes.catalogo);
      if (userId) {
        const carRes = await api.getCarrinho(userId);
        setCarrinho(carRes);
      }
    } catch (error) { console.error(error); }
  };

  useEffect(() => { carregarDados(); }, [userId]);

  const comprar = async (id_produto) => {
    try {
      await api.addCarrinho(userId, { id_produto, quantidade: 1 });
      carregarDados();
    } catch (error) { alert(error.message); }
  };

  const finalizar = async () => {
    try {
      const res = await api.checkout(userId);
      alert(res.mensagem);
      carregarDados();
    } catch (error) { alert(error.message); }
  };

  return (
    <div className="store-layout">
      <div style={{ flex: 1 }}>
        <h2>Produtos em Destaque</h2>
        <div className="catalog-grid">
          {catalogo.map(p => (
            <div key={p.id} className="product-card">
              <h3>{p.nome}</h3>
              <div className="product-price">R$ {p.preco.toFixed(2)}</div>
              <div className="product-meta">
                Vendido por: <strong>{p.loja}</strong><br/>
                Em estoque: {p.estoque} unid.
              </div>
              {userId ? (
                <button onClick={() => comprar(p.id)}>Adicionar ao Carrinho</button>
              ) : (
                <button className="btn-outline" disabled>Faça login para comprar</button>
              )}
            </div>
          ))}
        </div>
      </div>

      {userId && carrinho && (
        <div className="cart-panel">
          <h2 style={{ marginTop: 0 }}>Meu Carrinho</h2>
          <p style={{ color: 'var(--text-muted)' }}>{carrinho.total_itens} item(s) selecionado(s)</p>
          
          <div style={{ marginBottom: '20px' }}>
            {carrinho.itens.map((item, idx) => (
              <div key={idx} className="cart-item">
                <span>{item.quantidade}x {item.produto}</span>
                <strong>R$ {item.subtotal.toFixed(2)}</strong>
              </div>
            ))}
          </div>

          {carrinho.total_itens > 0 ? (
            <button className="btn-success" onClick={finalizar}>Finalizar Compra</button>
          ) : (
            <p style={{ textAlign: 'center', fontSize: '14px' }}>Seu carrinho está vazio.</p>
          )}
        </div>
      )}
    </div>
  );
}