from flask import Blueprint, jsonify, request
from extensions import db
from models import Product

products_bp = Blueprint("products", __name__)


@products_bp.route("/", methods=["GET"])
def list_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products]), 200


@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = db.get_or_404(Product, product_id)
    return jsonify(product.to_dict()), 200


@products_bp.route("/", methods=["POST"])
def create_product():
    data = request.get_json()
    if not data or not data.get("name") or data.get("price") is None:
        return jsonify({"error": "name and price are required"}), 400

    if data["price"] < 0:
        return jsonify({"error": "price must be non-negative"}), 400

    stock = data.get("stock", 0)
    if stock < 0:
        return jsonify({"error": "stock must be non-negative"}), 400

    product = Product(
        name=data["name"],
        description=data.get("description"),
        price=data["price"],
        stock=stock,
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201


@products_bp.route("/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    product = db.get_or_404(Product, product_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data provided"}), 400

    if "name" in data:
        product.name = data["name"]
    if "description" in data:
        product.description = data["description"]
    if "price" in data:
        if data["price"] < 0:
            return jsonify({"error": "price must be non-negative"}), 400
        product.price = data["price"]
    if "stock" in data:
        if data["stock"] < 0:
            return jsonify({"error": "stock must be non-negative"}), 400
        product.stock = data["stock"]

    db.session.commit()
    return jsonify(product.to_dict()), 200


@products_bp.route("/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = db.get_or_404(Product, product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "product deleted"}), 200
