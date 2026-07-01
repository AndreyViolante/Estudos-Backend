# API de Gerenciamento de Produtos

API REST construída com **FastAPI** + **SQLAlchemy** para gerenciar o catálogo
de produtos de um e-commerce, com suíte de testes em **Pytest** que roda
contra um **PostgreSQL real** provisionado via **Docker**.

## Estrutura do projeto

```
.
├── main.py              # API: modelos, schemas, endpoints
├── conftest.py           # Fixtures de teste (client, produto_existente, db_session)
├── requirements.txt
├── docker-compose.yml    # db_dev (5432), db_test (5433) e api
├── Dockerfile
├── pytest.ini
├── README.md
└── tests/
    ├── __init__.py
    └── test_produtos.py
```

## Pré-requisitos

- Docker e Docker Compose
- Python 3.12+

## 1. Subindo o banco de teste

Os testes precisam do container `db_test` (PostgreSQL na porta **5433**) de
pé e saudável antes de rodar:

```bash
docker-compose up -d db_test
```

Confirme que ele ficou `healthy` (pode levar alguns segundos):

```bash
docker-compose ps
```

> Se quiser rodar a aplicação completa (não só os testes), suba tudo com
> `docker-compose up -d`, o que também levanta `db_dev` (porta 5432) e a
> própria API (porta 8000).

## 2. Instalando as dependências

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Executando os testes

Comando exato:

```bash
pytest --cov=main --cov-report=term-missing -v
```

(Sem cobertura, `pytest -v` também funciona — a configuração de descoberta
de testes já está no `pytest.ini`.)

Por padrão, os testes se conectam em
`postgresql://postgres:postgres@localhost:5433/produtos_test_db`, exatamente
o que o serviço `db_test` do `docker-compose.yml` expõe. Para usar outra
URL, defina a variável de ambiente `TEST_DATABASE_URL` antes de rodar o
pytest.

### Saída esperada do pytest

Capturada rodando a suíte contra um PostgreSQL real (mesmo princípio do
`db_test`, apenas em outra porta durante a validação local):

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.0, pluggy-1.6.0
rootdir: /produtos-api
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.14.0, cov-7.1.0
collecting ... collected 18 items

tests/test_produtos.py::test_listar_produtos_quando_banco_vazio PASSED   [  5%]
tests/test_produtos.py::test_criar_produto_retorna_201_com_dados_corretos PASSED [ 11%]
tests/test_produtos.py::test_criar_produto_usa_valores_padrao_quando_omitidos PASSED [ 16%]
tests/test_produtos.py::test_criar_produto_persiste_no_banco PASSED      [ 22%]
tests/test_produtos.py::test_criar_produto_aparece_na_listagem PASSED    [ 27%]
tests/test_produtos.py::test_buscar_produto_por_id_sucesso PASSED        [ 33%]
tests/test_produtos.py::test_buscar_produto_com_id_inexistente_retorna_404 PASSED [ 38%]
tests/test_produtos.py::test_deletar_produto_retorna_204 PASSED          [ 44%]
tests/test_produtos.py::test_deletar_produto_remove_do_banco_confirmado_via_get PASSED [ 50%]
tests/test_produtos.py::test_deletar_produto_inexistente_retorna_404 PASSED [ 55%]
tests/test_produtos.py::test_criar_produto_com_payload_invalido_retorna_422[payload0] PASSED [ 61%]
tests/test_produtos.py::test_criar_produto_com_payload_invalido_retorna_422[payload1] PASSED [ 66%]
tests/test_produtos.py::test_criar_produto_com_payload_invalido_retorna_422[payload2] PASSED [ 72%]
tests/test_produtos.py::test_criar_produto_com_payload_invalido_retorna_422[payload3] PASSED [ 77%]
tests/test_produtos.py::test_criar_produto_com_payload_invalido_retorna_422[payload4] PASSED [ 83%]
tests/test_produtos.py::test_criar_produto_com_payload_invalido_retorna_422[payload5] PASSED [ 88%]
tests/test_produtos.py::test_criar_produto_com_payload_invalido_retorna_422[payload6] PASSED [ 94%]
tests/test_produtos.py::test_isolamento_entre_execucoes_banco_comeca_vazio PASSED [100%]

================================ tests coverage ================================
_______________ coverage: platform linux, python 3.12.3-final-0 ________________

Name      Stmts   Miss  Cover   Missing
---------------------------------------
main.py      64      4    94%   83-87
---------------------------------------
TOTAL        64      4    94%
============================== 18 passed in 0.61s ==============================
```

18 itens porque o teste parametrizado de payloads inválidos expande em 7
casos (`payload0` a `payload6`); somando aos outros 11, dá os 18 itens
coletados a partir das 12 funções de teste do arquivo. As linhas 83-87
("Missing") são o corpo da função `get_db()` de produção — ela nunca roda
durante os testes porque é justamente isso que `app.dependency_overrides`
garante: a sessão real é trocada pela sessão de teste. Ou seja, essa
"lacuna" de cobertura é, na prática, a prova de que o override está
funcionando.

## Como o isolamento entre testes funciona

A fixture `client` (em `conftest.py`) tem escopo de **função**, que é o
padrão do Pytest — ou seja, ela roda do zero para cada `test_*`:

1. **Setup**: `Base.metadata.create_all(bind=engine_teste)` cria todas as
   tabelas no banco de teste.
2. `app.dependency_overrides[get_db] = _override_get_db` faz a API usar a
   sessão do banco de teste em vez da sessão de produção.
3. **yield** de um `TestClient` já pronto para o teste fazer requisições.
4. **Teardown**: depois que o teste termina (passando ou falhando),
   `Base.metadata.drop_all(bind=engine_teste)` apaga todas as tabelas.

Como esse ciclo se repete a cada função de teste, nenhum dado criado em um
teste sobrevive para o próximo — cada teste começa com um banco
completamente vazio, mesmo que o teste anterior tenha criado dezenas de
produtos. O teste `test_isolamento_entre_execucoes_banco_comeca_vazio`
verifica isso explicitamente, e por estar posicionado depois de várias
outras funções que criam produtos, ele comprova o isolamento na prática
(não só na teoria).

## Modelo de dados — Produto

| Campo     | Tipo    | Regra                                   |
| --------- | ------- | ---------------------------------------- |
| `id`      | Integer | Chave primária, gerada pelo banco         |
| `nome`    | String  | Obrigatório, não pode ser vazio           |
| `preco`   | Float   | Obrigatório, deve ser maior que zero      |
| `estoque` | Integer | Padrão: 0, não pode ser negativo          |
| `ativo`   | Boolean | Padrão: True                              |

As mesmas regras de `preco > 0` e `estoque >= 0` também existem como
`CheckConstraint` no PostgreSQL (ver `main.py`), reforçando a validação do
Pydantic com uma garantia no próprio banco.

## Endpoints

| Método | Rota             | Status  | Comportamento                          |
| ------ | ---------------- | ------- | --------------------------------------- |
| GET    | `/produtos`       | 200     | Lista todos os produtos                 |
| POST   | `/produtos`       | 201     | Cria um produto e retorna com `id`      |
| GET    | `/produtos/{id}`  | 200/404 | Busca por id ou 404 se não existir      |
| DELETE | `/produtos/{id}`  | 204/404 | Remove o produto ou 404 se não existir  |

## Rodando a API localmente (fora do Docker)

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/produtos_db"
uvicorn main:app --reload
```

A documentação interativa fica em `http://localhost:8000/docs`.
