# API de Gerenciamento de Pedidos

API REST construída com **FastAPI** e **MongoDB** para criação e consulta de pedidos, publicando cada pedido criado em **RabbitMQ** e **Kafka** para consumo assíncrono por outros serviços.

## Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| Framework web | FastAPI |
| Banco de dados | MongoDB (via Motor, driver assíncrono) |
| Mensageria | RabbitMQ (aio-pika) + Kafka (aiokafka) |
| Containerização | Docker + Docker Compose |

## Estrutura do Projeto

```
order-api/
├── app/
│   ├── main.py             # Configuração da aplicação e lifespan (conexões)
│   ├── database.py         # Cliente MongoDB (Motor)
│   ├── models.py           # Schemas Pydantic (OrderCreate, OrderResponse)
│   ├── messaging/
│   │   ├── rabbitmq.py     # Publisher RabbitMQ (fila "orders")
│   │   └── kafka_producer.py  # Publisher Kafka (tópico "orders")
│   └── routes/
│       └── orders.py       # Endpoints de pedidos
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
└── .env.example
```

## Endpoints

| Método | Rota | Descrição | Código de sucesso |
|--------|------|-----------|:-----------------:|
| `POST` | `/api/v1/orders` | Criar pedido (persiste no MongoDB e publica em RabbitMQ + Kafka) | 201 |
| `GET` | `/api/v1/orders` | Listar todos os pedidos | 200 |

## Fluxo de criação de um pedido

1. O pedido é persistido na coleção `orders` do MongoDB com status `PENDENTE`.
2. Uma mensagem é publicada na fila `orders` do RabbitMQ.
3. Um evento `ORDER_CREATED` é publicado no tópico `orders` do Kafka.

Se a conexão com RabbitMQ ou Kafka ainda não estiver pronta, a publicação é ignorada silenciosamente (o pedido continua sendo criado e persistido normalmente).

## Executando a Aplicação

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 1. (Opcional) Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite .env com suas preferências
```

### 2. Subir os containers

```bash
docker-compose up --build
```

Isso sobe MongoDB, RabbitMQ (com painel de gerenciamento), Zookeeper, Kafka e a API. No startup, a aplicação tenta se conectar a cada serviço com retry automático (até 15 tentativas, com espera de 3s entre elas), já que os brokers podem demorar mais para ficar prontos do que os healthchecks indicam.

A API ficará disponível em:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **RabbitMQ management**: http://localhost:15672 (usuário/senha padrão: `guest`/`guest`)

### 3. Parar os containers

```bash
docker-compose down          # mantém os dados
docker-compose down -v       # remove também os volumes
```

## Executando localmente (fora do Docker)

Requer MongoDB, RabbitMQ e Kafka acessíveis (ou os respectivos endereços configurados via variáveis de ambiente):

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Exemplos de Uso (curl)

```bash
# Criar pedido
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"nome_cliente":"Maria","nome_produto":"Teclado mecânico","quantidade":1}'

# Listar pedidos
curl http://localhost:8000/api/v1/orders
```

## Modelo de Dados

**Order**

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | string (UUID) | gerado automaticamente |
| `nome_cliente` | string | obrigatório |
| `nome_produto` | string | obrigatório |
| `quantidade` | integer | obrigatório |
| `status` | string | `PENDENTE` na criação |
