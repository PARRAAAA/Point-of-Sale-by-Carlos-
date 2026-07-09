def test_create_product(client):
    res = client.post("/products/", json={"name": "Leche", "price": "3.00", "category": "Lácteos"})
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Leche"
    assert data["price"] == "3.00"
    assert data["id"] is not None


def test_list_products(client):
    client.post("/products/", json={"name": "Leche", "price": "3.00"})
    client.post("/products/", json={"name": "Pan", "price": "2.50"})
    res = client.get("/products/")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_search_products(client):
    client.post("/products/", json={"name": "Leche", "price": "3.00"})
    client.post("/products/", json={"name": "Pan", "price": "2.50"})
    res = client.get("/products/?search=lech")
    assert res.status_code == 200
    results = res.json()
    assert len(results) == 1
    assert results[0]["name"] == "Leche"


def test_update_product(client):
    created = client.post("/products/", json={"name": "Leche", "price": "3.00"}).json()
    res = client.put(f"/products/{created['id']}", json={"price": "3.50"})
    assert res.status_code == 200
    assert res.json()["price"] == "3.50"


def test_delete_product(client):
    created = client.post("/products/", json={"name": "Leche", "price": "3.00"}).json()
    res = client.delete(f"/products/{created['id']}")
    assert res.status_code == 204
    assert client.get("/products/").json() == []


def test_get_product(client):
    created = client.post("/products/", json={"name": "Leche", "price": "3.00", "category": "Lácteos"}).json()
    res = client.get(f"/products/{created['id']}")
    assert res.status_code == 200
    assert res.json()["name"] == "Leche"


def test_get_nonexistent_product(client):
    res = client.get("/products/999")
    assert res.status_code == 404


def test_update_nonexistent_product(client):
    res = client.put("/products/999", json={"price": "3.50"})
    assert res.status_code == 404


def test_delete_nonexistent_product(client):
    res = client.delete("/products/999")
    assert res.status_code == 404
