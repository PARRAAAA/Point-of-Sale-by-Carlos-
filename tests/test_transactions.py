def create_product(client, name, price):
    return client.post("/products/", json={"name": name, "price": price}).json()


def test_create_transaction_single_item(client):
    product = create_product(client, "Leche", "3.00")
    res = client.post("/transactions/", json={"items": [{"product_id": product["id"], "quantity": 2}]})
    assert res.status_code == 201
    data = res.json()
    assert data["total"] == "6.00"
    assert len(data["items"]) == 1
    assert data["items"][0]["subtotal"] == "6.00"
    assert data["items"][0]["unit_price"] == "3.00"


def test_create_transaction_multiple_items(client):
    leche = create_product(client, "Leche", "3.00")
    pan = create_product(client, "Pan", "2.50")
    res = client.post("/transactions/", json={
        "items": [
            {"product_id": leche["id"], "quantity": 2},
            {"product_id": pan["id"], "quantity": 1},
        ]
    })
    assert res.status_code == 201
    data = res.json()
    assert data["total"] == "8.50"
    assert len(data["items"]) == 2


def test_transaction_stores_price_at_time_of_sale(client):
    product = create_product(client, "Leche", "3.00")
    client.post("/transactions/", json={"items": [{"product_id": product["id"], "quantity": 1}]})
    client.put(f"/products/{product['id']}", json={"price": "5.00"})
    transactions = client.get("/transactions/").json()
    assert transactions[0]["items"][0]["unit_price"] == "3.00"


def test_create_transaction_product_not_found(client):
    res = client.post("/transactions/", json={"items": [{"product_id": 999, "quantity": 1}]})
    assert res.status_code == 404


def test_get_transaction(client):
    product = create_product(client, "Leche", "3.00")
    created = client.post("/transactions/", json={"items": [{"product_id": product["id"], "quantity": 1}]}).json()
    res = client.get(f"/transactions/{created['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == created["id"]


def test_get_transaction_not_found(client):
    res = client.get("/transactions/999")
    assert res.status_code == 404


def test_list_transactions(client):
    product = create_product(client, "Leche", "3.00")
    client.post("/transactions/", json={"items": [{"product_id": product["id"], "quantity": 1}]})
    client.post("/transactions/", json={"items": [{"product_id": product["id"], "quantity": 2}]})
    res = client.get("/transactions/")
    assert res.status_code == 200
    assert len(res.json()) == 2
