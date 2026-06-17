from pydantic import BaseModel
from typing import Optional, List

class LoginSchema(BaseModel):
    id_usuario: str
    senha: str

class CadastroSchema(BaseModel):
    nome: str
    senha: str
    tipo: str # "1" (Normal), "2" (VIP), "3" (Vendedor)
    nome_loja: Optional[str] = None

class CompraSchema(BaseModel):
    id_produto: str
    quantidade: int

class ProdutoFisicoSchema(BaseModel):
    id_produto: str
    nome: str
    preco: float
    estoque: int
    peso: float

class ProdutoDigitalSchema(BaseModel):
    id_produto: str
    nome: str
    preco: float
    estoque: int

class ClonarProdutoSchema(BaseModel):
    id_origem: str
    novo_id: str
    novo_nome: Optional[str] = None

class MudancaPrecoSchema(BaseModel):
    id_produto: str
    novo_preco: float