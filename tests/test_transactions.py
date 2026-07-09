def create_product(client, name, price, stock=10):
    return client.post("/products/", json={"name": name, "price": price, "stock": stock}).json()


def make_tx(client, items, method="cash", amount_tendered="100.00"):
    return client.post("/transactions/", json={
        "items": items,
        "payment": {"method": method, "amount_tendered": amount_tendered},
    })


def test_create_transaction_single_item(client):
    product = create_product(client, "Leche", "3.00")
    res = make_tx(client, [{"product_id": product["id"], "quantity": 2}], amount_tendered="10.00")
    assert res.status_code == 201
    data = res.json()
    assert data["total"] == "6.00"
    assert len(data["items"]) == 1
    assert data["items"][0]["subtotal"] == "6.00"
    assert data["items"][0]["unit_price"] == "3.00"


def test_create_transaction_multiple_items(client):
    leche = create_product(client, "Leche", "3.00")
    pan = create_product(client, "Pan", "2.50")
    res = make_tx(client, [
        {"product_id": leche["id"], "quantity": 2},
        {"product_id": pan["id"], "quantity": 1},
    ], amount_tendered="10.00")
    assert res.status_code == 201
    assert res.json()["total"] == "8.50"
    assert len(res.json()["items"]) == 2


def test_transaction_stores_price_at_time_of_sale(client):
    product = create_product(client, "Leche", "3.00")
    make_tx(client, [{"product_id": product["id"], "quantity": 1}], amount_tendered="5.00")
    client.put(f"/products/{product['id']}", json={"price": "5.00"})
    transactions = client.get("/transactions/").json()
    assert transactions[0]["items"][0]["unit_price"] == "3.00"


def test_create_transaction_product_not_found(client):
    res = make_tx(client, [{"product_id": 999, "quantity": 1}])
    assert res.status_code == 404


def test_get_transaction(client):
    product = create_product(client, "Leche", "3.00")
    created = make_tx(client, [{"product_id": product["id"], "quantity": 1}], amount_tendered="5.00").json()
    res = client.get(f"/transactions/{created['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == created["id"]


def test_get_transaction_not_found(client):
    res = client.get("/transactions/999")
    assert res.status_code == 404


def test_list_transactions(client):
    product = create_product(client, "Leche", "3.00")
    make_tx(client, [{"product_id": product["id"], "quantity": 1}], amount_tendered="5.00")
    make_tx(client, [{"product_id": product["id"], "quantity": 2}], amount_tendered="10.00")
    res = client.get("/transactions/")
    assert res.status_code == 200
    assert len(res.json()) == 2


# --- Payment-specific tests ---

def test_cash_payment_change_calculated(client):
    product = create_product(client, "Leche", "3.00")
    res = make_tx(client, [{"product_id": product["id"], "quantity": 2}], method="cash", amount_tendered="10.00")
    assert res.status_code == 201
    payment = res.json()["payment"]
    assert payment["method"] == "cash"
    assert payment["amount_tendered"] == "10.00"
    assert payment["change_given"] == "4.00"


def test_card_payment_no_change(client):
    product = create_product(client, "Leche", "3.00")
    res = make_tx(client, [{"product_id": product["id"], "quantity": 2}], method="card", amount_tendered="6.00")
    assert res.status_code == 201
    payment = res.json()["payment"]
    assert payment["method"] == "card"
    assert payment["change_given"] == "0.00"


def test_underpayment_rejected(client):
    product = create_product(client, "Leche", "3.00")
    res = make_tx(client, [{"product_id": product["id"], "quantity": 2}], method="cash", amount_tendered="5.00")
    assert res.status_code == 400


def test_exact_payment_accepted(client):
    product = create_product(client, "Leche", "3.00")
    res = make_tx(client, [{"product_id": product["id"], "quantity": 2}], method="cash", amount_tendered="6.00")
    assert res.status_code == 201
    assert res.json()["payment"]["change_given"] == "0.00"
