from flask import Blueprint, jsonify, request
from extensions import db
from models import Cart, CartItem, Product

cart_bp = Blueprint("cart", __name__)


def get_or_create_cart(session_id):
    cart = Cart.query.filter_by(session_id=session_id).first()
    if not cart:
        cart = Cart(session_id=session_id)
        db.session.add(cart)
        db.session.commit()
    return cart


@cart_bp.route("/<session_id>", methods=["GET"])
def get_cart(session_id):
    cart = get_or_create_cart(session_id)
    return jsonify(cart.to_dict()), 200


@cart_bp.route("/<session_id>/items", methods=["POST"])
def add_item(session_id):
    data = request.get_json()
    if not data or not data.get("product_id") or not data.get("quantity"):
        return jsonify({"error": "product_id and quantity are required"}), 400

    quantity = data["quantity"]
    if quantity <= 0:
        return jsonify({"error": "quantity must be positive"}), 400

    product = db.get_or_404(Product, data["product_id"])
    if product.stock < quantity:
        return jsonify({"error": "insufficient stock"}), 400

    cart = get_or_create_cart(session_id)
    item = CartItem.query.filter_by(
        cart_id=cart.id, product_id=product.id
    ).first()
    if item:
        if product.stock < item.quantity + quantity:
            return jsonify({"error": "insufficient stock"}), 400
        item.quantity += quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity)
        db.session.add(item)

    db.session.commit()
    return jsonify(cart.to_dict()), 200


@cart_bp.route("/<session_id>/items/<int:item_id>", methods=["PUT"])
def update_item(session_id, item_id):
    cart = Cart.query.filter_by(session_id=session_id).first_or_404()
    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first_or_404()

    data = request.get_json()
    if not data or "quantity" not in data:
        return jsonify({"error": "quantity is required"}), 400

    quantity = data["quantity"]
    if quantity <= 0:
        db.session.delete(item)
    else:
        if item.product.stock < quantity:
            return jsonify({"error": "insufficient stock"}), 400
        item.quantity = quantity

    db.session.commit()
    return jsonify(cart.to_dict()), 200


@cart_bp.route("/<session_id>/items/<int:item_id>", methods=["DELETE"])
def remove_item(session_id, item_id):
    cart = Cart.query.filter_by(session_id=session_id).first_or_404()
    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify(cart.to_dict()), 200


@cart_bp.route("/<session_id>", methods=["DELETE"])
def clear_cart(session_id):
    cart = Cart.query.filter_by(session_id=session_id).first_or_404()
    for item in cart.items:
        db.session.delete(item)
    db.session.commit()
    return jsonify(cart.to_dict()), 200
