# API de Gerenciamento de Produtos

API REST completa para gerenciamento de produtos, desenvolvida com **FastAPI**, **PostgreSQL** e **Docker**.

## Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| Framework web | FastAPI |
| Banco de dados | PostgreSQL 15 |
| ORM | SQLAlchemy 2 |
| Containerização | Docker + Docker Compose |
| Testes | Pytest + httpx |

## Estrutura do Projeto

```
crud-api/
├── app/
│   ├── main.py          # Configuração e startup da aplicação
│   ├── database.py      # Engine e sessão do SQLAlchemy
│   ├── models.py        # Modelo Product (tabela products)
│   ├── schemas.py       # Schemas Pydantic (request/response)
│   └── routers/
│       └── products.py  # Endpoints CRUD de produtos
├── tests/
│   ├── conftest.py      # Fixtures (banco SQLite in-test)
│   └── test_products.py # Testes de todas as operações CRUD
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
└── .env.example
```

## Endpoints

| Método | Rota | Descrição | Código de sucesso |
|--------|------|-----------|:-----------------:|
| `POST` | `/products/` | Criar produto | 201 |
| `GET` | `/products/` | Listar produtos (paginado) | 200 |
| `GET` | `/products/{id}` | Buscar produto por ID | 200 |
| `PUT` | `/products/{id}` | Atualizar produto (parcial) | 200 |
| `DELETE` | `/products/{id}` | Remover produto | 204 |
| `GET` | `/health` | Status da API | 200 |

## Executando a Aplicação

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Clonar o repositório

```bash
git clone https://github.com/<seu-usuario>/crud-api.git
cd crud-api
```

### 2. (Opcional) Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite .env com suas preferências
```

### 3. Subir os containers

```bash
docker-compose up --build
```

A API ficará disponível em:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. Parar os containers

```bash
docker-compose down          # mantém os dados
docker-compose down -v       # remove também o volume do banco
```

## Executando os Testes

Os testes usam SQLite em memória, **sem necessidade de Docker ou PostgreSQL**.

### Pré-requisitos

- Python 3.11+

### 1. Instalar dependências de teste

Os testes usam SQLite em memória, portanto **não é necessário um servidor PostgreSQL** para rodá-los.
Use o arquivo `requirements-test.txt`, uma versão mais enxuta de `requirements.txt`:

```bash
pip install -r requirements-test.txt
```

### 2. Executar os testes

```bash
pytest
```

### 3. Com saída detalhada

```bash
pytest -v
```

Exemplo de saída esperada:

```
tests/test_products.py::test_create_product               PASSED
tests/test_products.py::test_create_product_without_description PASSED
tests/test_products.py::test_create_product_invalid_price PASSED
tests/test_products.py::test_create_product_missing_required_fields PASSED
tests/test_products.py::test_list_products_empty          PASSED
tests/test_products.py::test_list_products                PASSED
tests/test_products.py::test_list_products_pagination     PASSED
tests/test_products.py::test_get_product                  PASSED
tests/test_products.py::test_get_product_not_found        PASSED
tests/test_products.py::test_update_product               PASSED
tests/test_products.py::test_update_product_partial       PASSED
tests/test_products.py::test_update_product_not_found     PASSED
tests/test_products.py::test_update_product_invalid_price PASSED
tests/test_products.py::test_delete_product               PASSED
tests/test_products.py::test_delete_product_not_found     PASSED
tests/test_products.py::test_health_check                 PASSED

16 passed in X.XXs
```

## Exemplos de Uso (curl)

```bash
# Criar produto
curl -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Notebook","description":"i7 16GB","price":4500.00,"stock":10}'

# Listar produtos
curl http://localhost:8000/products/

# Buscar por ID
curl http://localhost:8000/products/1

# Atualizar (parcial — só os campos enviados são alterados)
curl -X PUT http://localhost:8000/products/1 \
  -H "Content-Type: application/json" \
  -d '{"price":4200.00,"stock":8}'

# Remover
curl -X DELETE http://localhost:8000/products/1
```

## Modelo de Dados

**Product**

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | integer | PK, auto-incremento |
| `name` | string | obrigatório, max 255 |
| `description` | string | opcional |
| `price` | float | obrigatório, > 0 |
| `stock` | integer | padrão 0, >= 0 |
| `created_at` | datetime | preenchido automaticamente |
| `updated_at` | datetime | atualizado automaticamente |
