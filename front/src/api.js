const API_URL = "http://localhost:8000";

const request = async (endpoint, method = "GET", body = null, userId = null) => {
  const headers = { "Content-Type": "application/json" };
  if (userId) headers["X-User-Id"] = userId;

  const config = { method, headers };
  if (body) config.body = JSON.stringify(body);

  const response = await fetch(`${API_URL}${endpoint}`, config);
  const data = await response.json();
  
  if (!response.ok) throw new Error(data.detail || "Erro na requisição");
  return data;
};

export const api = {
  // Autenticação
  login: (dados) => request("/auth/login", "POST", dados),
  cadastrar: (dados) => request("/auth/cadastro", "POST", dados),
  
  // Públicas
  getCatalogo: () => request("/catalogo", "GET"),
  
  // Cliente (Exige userId)
  getHistorico: (userId) => request("/usuario/historico", "GET", null, userId),
  getCarrinho: (userId) => request("/carrinho", "GET", null, userId),
  addCarrinho: (userId, dados) => request("/carrinho", "POST", dados, userId),
  checkout: (userId) => request("/checkout", "POST", null, userId),
  
  // Vendedor (Exige userId)
  publicarFisico: (userId, dados) => request("/vendedor/produto/fisico", "POST", dados, userId),
  publicarDigital: (userId, dados) => request("/vendedor/produto/digital", "POST", dados, userId),
  alterarPreco: (userId, dados) => request("/vendedor/produto/preco", "PUT", dados, userId),
  clonarProduto: (userId, dados) => request("/vendedor/produto/clonar", "POST", dados, userId)
};