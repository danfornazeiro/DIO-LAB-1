import json


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


# --- Products ---

def test_create_product(client):
    resp = client.post(
        "/products/",
        data=json.dumps({"name": "Widget", "price": 9.99, "stock": 10}),
        content_type="application/json",
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Widget"
    assert data["price"] == 9.99
    assert data["stock"] == 10


def test_create_product_missing_fields(client):
    resp = client.post(
        "/products/",
        data=json.dumps({"name": "Widget"}),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_create_product_negative_price(client):
    resp = client.post(
        "/products/",
        data=json.dumps({"name": "Widget", "price": -1}),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_list_products(client):
    client.post(
        "/products/",
        data=json.dumps({"name": "A", "price": 1.0}),
        content_type="application/json",
    )
    resp = client.get("/products/")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_get_product(client):
    created = client.post(
        "/products/",
        data=json.dumps({"name": "B", "price": 2.0}),
        content_type="application/json",
    ).get_json()
    resp = client.get(f"/products/{created['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "B"


def test_get_product_not_found(client):
    resp = client.get("/products/999")
    assert resp.status_code == 404


def test_update_product(client):
    created = client.post(
        "/products/",
        data=json.dumps({"name": "C", "price": 3.0, "stock": 5}),
        content_type="application/json",
    ).get_json()
    resp = client.put(
        f"/products/{created['id']}",
        data=json.dumps({"price": 4.0}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.get_json()["price"] == 4.0


def test_delete_product(client):
    created = client.post(
        "/products/",
        data=json.dumps({"name": "D", "price": 1.0}),
        content_type="application/json",
    ).get_json()
    resp = client.delete(f"/products/{created['id']}")
    assert resp.status_code == 200
    assert client.get(f"/products/{created['id']}").status_code == 404


# --- Cart ---

def _create_product(client, name="Prod", price=10.0, stock=20):
    return client.post(
        "/products/",
        data=json.dumps({"name": name, "price": price, "stock": stock}),
        content_type="application/json",
    ).get_json()


def test_get_empty_cart(client):
    resp = client.get("/cart/session-1")
    assert resp.status_code == 200
    assert resp.get_json()["items"] == []
    assert resp.get_json()["total"] == 0


def test_add_item_to_cart(client):
    product = _create_product(client)
    resp = client.post(
        "/cart/session-1/items",
        data=json.dumps({"product_id": product["id"], "quantity": 2}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    cart = resp.get_json()
    assert len(cart["items"]) == 1
    assert cart["items"][0]["quantity"] == 2
    assert cart["total"] == 20.0


def test_add_item_insufficient_stock(client):
    product = _create_product(client, stock=1)
    resp = client.post(
        "/cart/session-1/items",
        data=json.dumps({"product_id": product["id"], "quantity": 5}),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_remove_item_from_cart(client):
    product = _create_product(client)
    cart = client.post(
        "/cart/session-1/items",
        data=json.dumps({"product_id": product["id"], "quantity": 1}),
        content_type="application/json",
    ).get_json()
    item_id = cart["items"][0]["id"]
    resp = client.delete(f"/cart/session-1/items/{item_id}")
    assert resp.status_code == 200
    assert resp.get_json()["items"] == []


def test_clear_cart(client):
    product = _create_product(client)
    client.post(
        "/cart/session-1/items",
        data=json.dumps({"product_id": product["id"], "quantity": 1}),
        content_type="application/json",
    )
    resp = client.delete("/cart/session-1")
    assert resp.status_code == 200
    assert resp.get_json()["items"] == []


# --- Orders ---

def test_create_order(client):
    product = _create_product(client, stock=10)
    client.post(
        "/cart/session-2/items",
        data=json.dumps({"product_id": product["id"], "quantity": 3}),
        content_type="application/json",
    )
    resp = client.post(
        "/orders/",
        data=json.dumps({"session_id": "session-2"}),
        content_type="application/json",
    )
    assert resp.status_code == 201
    order = resp.get_json()
    assert order["total"] == 30.0
    assert order["status"] == "pending"
    assert len(order["items"]) == 1


def test_create_order_empty_cart(client):
    resp = client.post(
        "/orders/",
        data=json.dumps({"session_id": "session-empty"}),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_list_orders(client):
    product = _create_product(client, stock=10)
    client.post(
        "/cart/session-3/items",
        data=json.dumps({"product_id": product["id"], "quantity": 1}),
        content_type="application/json",
    )
    client.post(
        "/orders/",
        data=json.dumps({"session_id": "session-3"}),
        content_type="application/json",
    )
    resp = client.get("/orders/?session_id=session-3")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_update_order_status(client):
    product = _create_product(client, stock=5)
    client.post(
        "/cart/session-4/items",
        data=json.dumps({"product_id": product["id"], "quantity": 1}),
        content_type="application/json",
    )
    order = client.post(
        "/orders/",
        data=json.dumps({"session_id": "session-4"}),
        content_type="application/json",
    ).get_json()
    resp = client.patch(
        f"/orders/{order['id']}/status",
        data=json.dumps({"status": "shipped"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "shipped"


def test_update_order_invalid_status(client):
    product = _create_product(client, stock=5)
    client.post(
        "/cart/session-5/items",
        data=json.dumps({"product_id": product["id"], "quantity": 1}),
        content_type="application/json",
    )
    order = client.post(
        "/orders/",
        data=json.dumps({"session_id": "session-5"}),
        content_type="application/json",
    ).get_json()
    resp = client.patch(
        f"/orders/{order['id']}/status",
        data=json.dumps({"status": "flying"}),
        content_type="application/json",
    )
    assert resp.status_code == 400
