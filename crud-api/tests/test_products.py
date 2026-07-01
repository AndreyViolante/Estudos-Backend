def _create_product(client, **overrides):
    payload = {
        "name": "Notebook",
        "description": "i7 16GB",
        "price": 4500.00,
        "stock": 10,
    }
    payload.update(overrides)
    return client.post("/products/", json=payload)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_product(client):
    response = _create_product(client)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Notebook"
    assert data["price"] == 4500.00
    assert data["stock"] == 10
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_product_without_description(client):
    response = _create_product(client, description=None)
    assert response.status_code == 201
    assert response.json()["description"] is None


def test_create_product_invalid_price(client):
    response = _create_product(client, price=-10)
    assert response.status_code == 422


def test_create_product_missing_required_fields(client):
    response = client.post("/products/", json={"description": "sem nome nem preço"})
    assert response.status_code == 422


def test_list_products_empty(client):
    response = client.get("/products/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_products(client):
    _create_product(client, name="Notebook")
    _create_product(client, name="Mouse")
    response = client.get("/products/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_products_pagination(client):
    for i in range(5):
        _create_product(client, name=f"Produto {i}")
    response = client.get("/products/?skip=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_product(client):
    created = _create_product(client).json()
    response = client.get(f"/products/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_product_not_found(client):
    response = client.get("/products/999")
    assert response.status_code == 404


def test_update_product(client):
    created = _create_product(client).json()
    response = client.put(
        f"/products/{created['id']}",
        json={"name": "Notebook Pro", "price": 5200.00, "stock": 3},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Notebook Pro"
    assert data["price"] == 5200.00
    assert data["stock"] == 3


def test_update_product_partial(client):
    created = _create_product(client).json()
    response = client.put(f"/products/{created['id']}", json={"price": 4200.00})
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 4200.00
    assert data["name"] == created["name"]


def test_update_product_not_found(client):
    response = client.put("/products/999", json={"price": 100.00})
    assert response.status_code == 404


def test_update_product_invalid_price(client):
    created = _create_product(client).json()
    response = client.put(f"/products/{created['id']}", json={"price": -1})
    assert response.status_code == 422


def test_delete_product(client):
    created = _create_product(client).json()
    response = client.delete(f"/products/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/products/{created['id']}").status_code == 404


def test_delete_product_not_found(client):
    response = client.delete("/products/999")
    assert response.status_code == 404
