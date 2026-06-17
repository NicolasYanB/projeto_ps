import { useState } from 'react';
import { api } from './api';

export default function SellerDashboard({ userId }) {
  const [form, setForm] = useState({
    id_produto: '', nome: '', preco: '', estoque: '', peso: '', tipo: 'fisico',
    id_origem: '', novo_id: '', novo_nome: '', novo_preco: ''
  });

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const publicarProduto = async () => {
    try {
      const payload = {
        id_produto: form.id_produto, nome: form.nome, 
        preco: parseFloat(form.preco), estoque: parseInt(form.estoque)
      };
      if (form.tipo === 'fisico') {
        payload.peso = parseFloat(form.peso);
        await api.publicarFisico(userId, payload);
      } else {
        await api.publicarDigital(userId, payload);
      }
      alert("Produto publicado com sucesso!");
    } catch (e) { alert(e.message); }
  };

  const clonarProduto = async () => {
    try {
      await api.clonarProduto(userId, { id_origem: form.id_origem, novo_id: form.novo_id, novo_nome: form.novo_nome || undefined });
      alert("Produto clonado com sucesso!");
    } catch (e) { alert(e.message); }
  };

  const alterarPreco = async () => {
    try {
      await api.alterarPreco(userId, { id_produto: form.id_produto, novo_preco: parseFloat(form.novo_preco) });
      alert("Preço atualizado!");
    } catch (e) { alert(e.message); }
  };

  return (
    <div className="card seller-dashboard">
      <h2 style={{ marginTop: 0 }}>Gestão da Loja (Vendedor)</h2>
      
      <div className="dashboard-grid">
        <div className="dashboard-section">
          <h3>Publicar Produto</h3>
          <select name="tipo" onChange={handleChange} value={form.tipo}>
            <option value="fisico">Produto Físico</option>
            <option value="digital">Produto Digital</option>
          </select>
          <input name="id_produto" placeholder="ID Produto (ex: P01)" onChange={handleChange} />
          <input name="nome" placeholder="Nome do Produto" onChange={handleChange} />
          <input name="preco" type="number" placeholder="Preço (R$)" onChange={handleChange} />
          <input name="estoque" type="number" placeholder="Estoque Inicial" onChange={handleChange} />
          {form.tipo === 'fisico' && <input name="peso" type="number" placeholder="Peso (kg)" onChange={handleChange} />}
          <button onClick={publicarProduto}>Publicar Catálogo</button>
        </div>

        <div className="dashboard-section">
          <h3>Clonar Produto (Prototype)</h3>
          <input name="id_origem" placeholder="ID do Produto Origem" onChange={handleChange} />
          <input name="novo_id" placeholder="Novo ID" onChange={handleChange} />
          <input name="novo_nome" placeholder="Novo Nome (Opcional)" onChange={handleChange} />
          <button className="btn-outline" onClick={clonarProduto}>Clonar via Prototype</button>
        </div>

        <div className="dashboard-section">
          <h3>Gestão de Preço</h3>
          <input name="id_produto" placeholder="ID do Produto" onChange={handleChange} />
          <input name="novo_preco" type="number" placeholder="Novo Preço (R$)" onChange={handleChange} />
          <button className="btn-outline" onClick={alterarPreco}>Atualizar Preço</button>
        </div>
      </div>
    </div>
  );
}