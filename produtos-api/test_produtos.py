import pytest

from main import Produto


def test_listar_produtos_quando_banco_vazio(client):
    resposta = client.get("/produtos")

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_criar_produto_retorna_201_com_dados_corretos(client):
    payload = {"nome": "Teclado Mecânico", "preco": 250.0, "estoque": 10, "ativo": True}

    resposta = client.post("/produtos", json=payload)

    assert resposta.status_code == 201
    dados = resposta.json()
    assert isinstance(dados["id"], int)
    assert dados["nome"] == payload["nome"]
    assert dados["preco"] == payload["preco"]
    assert dados["estoque"] == payload["estoque"]
    assert dados["ativo"] == payload["ativo"]


def test_criar_produto_usa_valores_padrao_quando_omitidos(client):
    payload = {"nome": "Produto Padrão", "preco": 25.0}

    resposta = client.post("/produtos", json=payload)

    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["estoque"] == 0
    assert dados["ativo"] is True


def test_criar_produto_persiste_no_banco(client, db_session):
    payload = {"nome": "Mouse Sem Fio", "preco": 89.5, "estoque": 12, "ativo": True}

    resposta = client.post("/produtos", json=payload)
    produto_id = resposta.json()["id"]

    produto_no_banco = db_session.query(Produto).filter(Produto.id == produto_id).first()
    assert produto_no_banco is not None
    assert produto_no_banco.nome == payload["nome"]
    assert produto_no_banco.preco == payload["preco"]
    assert produto_no_banco.estoque == payload["estoque"]
    assert produto_no_banco.ativo == payload["ativo"]


def test_criar_produto_aparece_na_listagem(client):
    payload = {"nome": "Monitor 27 polegadas", "preco": 1200.0, "estoque": 3, "ativo": True}
    client.post("/produtos", json=payload)

    resposta = client.get("/produtos")

    assert resposta.status_code == 200
    nomes_listados = [produto["nome"] for produto in resposta.json()]
    assert payload["nome"] in nomes_listados


def test_buscar_produto_por_id_sucesso(client, produto_existente):
    produto_id = produto_existente["id"]

    resposta = client.get(f"/produtos/{produto_id}")

    assert resposta.status_code == 200
    assert resposta.json()["id"] == produto_id
    assert resposta.json()["nome"] == produto_existente["nome"]


def test_buscar_produto_com_id_inexistente_retorna_404(client):
    resposta = client.get("/produtos/999999")

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Produto não encontrado"


def test_deletar_produto_retorna_204(client, produto_existente):
    produto_id = produto_existente["id"]

    resposta = client.delete(f"/produtos/{produto_id}")

    assert resposta.status_code == 204
    assert resposta.content == b""


def test_deletar_produto_remove_do_banco_confirmado_via_get(client, produto_existente):
    produto_id = produto_existente["id"]
    client.delete(f"/produtos/{produto_id}")

    resposta = client.get(f"/produtos/{produto_id}")

    assert resposta.status_code == 404


def test_deletar_produto_inexistente_retorna_404(client):
    resposta = client.delete("/produtos/999999")

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Produto não encontrado"


@pytest.mark.parametrize(
    "payload",
    [
        {"nome": "", "preco": 10.0},              # nome vazio
        {"preco": 10.0},                           # nome ausente
        {"nome": "Sem preço"},                     # preco ausente
        {"nome": "Preço negativo", "preco": -5.0}, # preco <= 0
        {"nome": "Preço zero", "preco": 0},        # preco <= 0
        {"nome": "Estoque negativo", "preco": 10.0, "estoque": -1},  # estoque < 0
        {"nome": "Preço como texto", "preco": "caro"},               # tipo inválido
    ],
)
def test_criar_produto_com_payload_invalido_retorna_422(client, payload):
    resposta = client.post("/produtos", json=payload)

    assert resposta.status_code == 422


def test_isolamento_entre_execucoes_banco_comeca_vazio(client):
    """Cada teste recebe um banco zerado — sem vazamento de estado entre execuções."""
    resposta_inicial = client.get("/produtos")
    assert resposta_inicial.status_code == 200
    assert resposta_inicial.json() == []

    client.post("/produtos", json={"nome": "Produto Isolado", "preco": 50.0})

    resposta_apos_criacao = client.get("/produtos")
    assert len(resposta_apos_criacao.json()) == 1
