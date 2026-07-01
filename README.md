# estudos-backend

Repositório de estudos de desenvolvimento backend com **Python**, reunindo APIs REST construídas com **FastAPI** para praticar CRUD, testes automatizados, mensageria e containerização com Docker.

## Projetos

| Projeto | Descrição | Banco de dados | Destaques |
|---|---|---|---|
| [`crud-api`](crud-api) | API de gerenciamento de produtos | PostgreSQL (SQLAlchemy 2) | CRUD completo, testes com SQLite in-memory, Docker Compose |
| [`produtos-api`](produtos-api) | API de catálogo de produtos de e-commerce | PostgreSQL real (via Docker) | Testes de integração contra banco real, cobertura de testes, isolamento por fixture |
| [`order-api`](order-api) | API de gerenciamento de pedidos | MongoDB | Mensageria assíncrona com RabbitMQ e Kafka, retry com backoff no startup |

Cada subprojeto é independente, com seu próprio `Dockerfile`, `docker-compose.yml` e `requirements.txt`. Consulte o README de cada pasta para instruções detalhadas de execução e testes.

## Tecnologias

- **FastAPI** — framework web para as APIs
- **SQLAlchemy** — ORM para PostgreSQL (`crud-api`, `produtos-api`)
- **PostgreSQL** — banco relacional
- **MongoDB** — banco de documentos (`order-api`)
- **RabbitMQ** e **Kafka** — mensageria assíncrona (`order-api`)
- **Docker** e **Docker Compose** — containerização e orquestração local
- **Pytest** — testes automatizados

## Como usar

Entre na pasta do projeto desejado e siga as instruções do respectivo README, por exemplo:

```bash
cd produtos-api
docker-compose up -d db_test
pip install -r requirements.txt
pytest -v
```

## Objetivo

Repositório pessoal de estudos, usado para praticar arquitetura de APIs REST, integração com bancos de dados, testes automatizados e mensageria entre serviços.
