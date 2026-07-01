import os

# Define antes de importar main para que o engine aponte para o banco de teste
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/produtos_test_db",
)
os.environ.setdefault("DATABASE_URL", TEST_DATABASE_URL)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from main import Base, app, get_db  # noqa: E402

engine_teste = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_teste)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Cria as tabelas, substitui get_db e destrói tudo ao fim de cada teste."""
    Base.metadata.create_all(bind=engine_teste)
    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine_teste)


@pytest.fixture
def produto_existente(client):
    """Cria um produto no banco antes do teste rodar."""
    payload = {"nome": "Produto Existente", "preco": 99.90, "estoque": 5, "ativo": True}
    resposta = client.post("/produtos", json=payload)
    return resposta.json()


@pytest.fixture
def db_session():
    """Sessão direta ao banco de teste, para verificar persistência sem passar pela API."""
    sessao = TestingSessionLocal()
    try:
        yield sessao
    finally:
        sessao.close()
