import { useState } from 'react';
import { api } from './api';

export default function Auth({ onAuthSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ id_usuario: '', senha: '', nome: '', tipo: '1', nome_loja: '' });

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isLogin) {
        const res = await api.login({ id_usuario: formData.id_usuario, senha: formData.senha });
        onAuthSuccess(res.x_user_id, res.type);
      } else {
        const payload = { ...formData, nome_loja: formData.tipo === '3' ? formData.nome_loja : null };
        const res = await api.cadastrar(payload);
        onAuthSuccess(res.x_user_id, formData.tipo);
      }
    } catch (error) { alert(error.message); }
  };

  return (
    <div className="card">
      <h2 style={{marginTop: 0}}>{isLogin ? "Acessar Conta" : "Criar Nova Conta"}</h2>
      <form onSubmit={handleSubmit}>
        {isLogin ? (
          <input name="id_usuario" placeholder="ID do Usuário" onChange={handleChange} required />
        ) : (
          <>
            <input name="nome" placeholder="Nome Completo" onChange={handleChange} required />
            <select name="tipo" onChange={handleChange} value={formData.tipo}>
              <option value="1">Cliente Normal</option>
              <option value="2">Cliente VIP</option>
              <option value="3">Vendedor</option>
            </select>
            {formData.tipo === '3' && (
              <input name="nome_loja" placeholder="Nome da sua Loja" onChange={handleChange} required />
            )}
          </>
        )}
        <input name="senha" type="password" placeholder="Sua Senha" onChange={handleChange} required />
        <button type="submit">{isLogin ? "Entrar" : "Cadastrar"}</button>
      </form>
      <button className="btn-outline" onClick={() => setIsLogin(!isLogin)} style={{ marginTop: '15px' }}>
        {isLogin ? "Ainda não tem conta? Cadastre-se" : "Já tenho conta. Fazer Login"}
      </button>
    </div>
  );
}