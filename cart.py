"""
Cart Routes  (auth required for all)
GET    /api/cart/           - view cart
POST   /api/cart/add        - add item
PUT    /api/cart/<id>       - update quantity
DELETE /api/cart/<id>       - remove item
DELETE /api/cart/clear      - clear entire cart
POST   /api/cart/checkout   - place order from cart
"""
from flask import Blueprint, request, jsonify, g
from database import db
from models import CartItem, Product, Order, OrderItem
from utils.auth_helpers import token_required

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/", methods=["GET"])
@token_required
def view_cart():
    items = CartItem.query.filter_by(user_id=g.current_user.id).all()
    total = round(sum(i.product.price * i.quantity for i in items), 2)
    return jsonify({
        "items":        [i.to_dict() for i in items],
        "item_count":   sum(i.quantity for i in items),
        "total":        total,
    }), 200


@cart_bp.route("/add", methods=["POST"])
@token_required
def add_to_cart():
    data       = request.get_json()
    product_id = data.get("product_id")
    quantity   = int(data.get("quantity", 1))
    size       = data.get("size")
    color      = data.get("color")

    if not product_id:
        return jsonify({"error": "product_id required"}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    if product.stock < quantity:
        return jsonify({"error": "Insufficient stock"}), 400

    # Check if already in cart (same product + size + color)
    existing = CartItem.query.filter_by(
        user_id=g.current_user.id,
        product_id=product_id,
        size=size,
        color=color
    ).first()

    if existing:
        existing.quantity += quantity
    else:
        item = CartItem(
            user_id=g.current_user.id,
            product_id=product_id,
            quantity=quantity,
            size=size,
            color=color,
        )
        db.session.add(item)

    db.session.commit()
    return jsonify({"message": "Added to cart"}), 201


@cart_bp.route("/<int:item_id>", methods=["PUT"])
@token_required
def update_cart_item(item_id):
    item = CartItem.query.filter_by(id=item_id, user_id=g.current_user.id).first()
    if not item:
        return jsonify({"error": "Cart item not found"}), 404

    data     = request.get_json()
    quantity = int(data.get("quantity", 1))
    if quantity < 1:
        db.session.delete(item)
    else:
        item.quantity = quantity
    db.session.commit()
    return jsonify({"message": "Cart updated"}), 200


@cart_bp.route("/<int:item_id>", methods=["DELETE"])
@token_required
def remove_cart_item(item_id):
    item = CartItem.query.filter_by(id=item_id, user_id=g.current_user.id).first()
    if not item:
        return jsonify({"error": "Cart item not found"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item removed"}), 200


@cart_bp.route("/clear", methods=["DELETE"])
@token_required
def clear_cart():
    CartItem.query.filter_by(user_id=g.current_user.id).delete()
    db.session.commit()
    return jsonify({"message": "Cart cleared"}), 200


@cart_bp.route("/checkout", methods=["POST"])
@token_required
def checkout():
    data    = request.get_json()
    address = data.get("address", "")
    payment = data.get("payment_mode", "COD")

    items = CartItem.query.filter_by(user_id=g.current_user.id).all()
    if not items:
        return jsonify({"error": "Cart is empty"}), 400

    total = round(sum(i.product.price * i.quantity for i in items), 2)

    order = Order(
        user_id      = g.current_user.id,
        total_amount = total,
        status       = "confirmed",
        payment_mode = payment,
        address      = address,
    )
    db.session.add(order)
    db.session.flush()   # get order.id

    for cart_item in items:
        order_item = OrderItem(
            order_id   = order.id,
            product_id = cart_item.product_id,
            quantity   = cart_item.quantity,
            unit_price = cart_item.product.price,
        )
        db.session.add(order_item)
        # Reduce stock
        cart_item.product.stock = max(0, cart_item.product.stock - cart_item.quantity)

    # Clear cart
    CartItem.query.filter_by(user_id=g.current_user.id).delete()
    db.session.commit()

    return jsonify({
        "message": "Order placed successfully!",
        "order":   order.to_dict(),
    }), 201
