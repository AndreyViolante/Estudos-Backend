from pydantic import BaseModel


class OrderCreate(BaseModel):
    nome_cliente: str
    nome_produto: str
    quantidade: int


class OrderResponse(BaseModel):
    id: str
    nome_cliente: str
    nome_produto: str
    quantidade: int
    status: str
