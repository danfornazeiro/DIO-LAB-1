from flask import Blueprint, jsonify, request
from extensions import db
from models import Cart, Order, OrderItem

orders_bp = Blueprint("orders", __name__)

VALID_STATUSES = {"pending", "processing", "shipped", "delivered", "cancelled"}


@orders_bp.route("/", methods=["GET"])
def list_orders():
    session_id = request.args.get("session_id")
    query = Order.query
    if session_id:
        query = query.filter_by(session_id=session_id)
    orders = query.order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders]), 200


@orders_bp.route("/<int:order_id>", methods=["GET"])
def get_order(order_id):
    order = db.get_or_404(Order, order_id)
    return jsonify(order.to_dict()), 200


@orders_bp.route("/", methods=["POST"])
def create_order():
    data = request.get_json()
    if not data or not data.get("session_id"):
        return jsonify({"error": "session_id is required"}), 400

    session_id = data["session_id"]
    cart = Cart.query.filter_by(session_id=session_id).first()
    if not cart or not cart.items:
        return jsonify({"error": "cart is empty"}), 400

    for item in cart.items:
        if item.product.stock < item.quantity:
            return jsonify(
                {"error": f"insufficient stock for product '{item.product.name}'"}
            ), 400

    total = sum(item.subtotal() for item in cart.items)
    order = Order(session_id=session_id, total=total)
    db.session.add(order)

    for item in cart.items:
        order_item = OrderItem(
            order=order,
            product_id=item.product_id,
            product_name=item.product.name,
            price=item.product.price,
            quantity=item.quantity,
        )
        db.session.add(order_item)
        item.product.stock -= item.quantity
        db.session.delete(item)

    db.session.commit()
    return jsonify(order.to_dict()), 201


@orders_bp.route("/<int:order_id>/status", methods=["PATCH"])
def update_order_status(order_id):
    order = db.get_or_404(Order, order_id)
    data = request.get_json()
    if not data or not data.get("status"):
        return jsonify({"error": "status is required"}), 400

    status = data["status"]
    if status not in VALID_STATUSES:
        return jsonify({"error": f"invalid status, must be one of: {', '.join(sorted(VALID_STATUSES))}"}), 400

    order.status = status
    db.session.commit()
    return jsonify(order.to_dict()), 200
