"""
Wishlist Routes  (auth required)
GET    /api/wishlist/         - view wishlist
POST   /api/wishlist/add      - add product
DELETE /api/wishlist/<id>     - remove item
POST   /api/wishlist/move-to-cart/<id>  - move item to cart
"""
from flask import Blueprint, request, jsonify, g
from database import db
from models import WishlistItem, CartItem, Product
from utils.auth_helpers import token_required

wishlist_bp = Blueprint("wishlist", __name__)


@wishlist_bp.route("/", methods=["GET"])
@token_required
def view_wishlist():
    items = WishlistItem.query.filter_by(user_id=g.current_user.id).all()
    return jsonify({"items": [i.to_dict() for i in items], "count": len(items)}), 200


@wishlist_bp.route("/add", methods=["POST"])
@token_required
def add_to_wishlist():
    data       = request.get_json()
    product_id = data.get("product_id")

    if not product_id:
        return jsonify({"error": "product_id required"}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    exists = WishlistItem.query.filter_by(
        user_id=g.current_user.id,
        product_id=product_id
    ).first()

    if exists:
        return jsonify({"message": "Already in wishlist"}), 200

    item = WishlistItem(user_id=g.current_user.id, product_id=product_id)
    db.session.add(item)
    db.session.commit()
    return jsonify({"message": "Added to wishlist"}), 201


@wishlist_bp.route("/<int:item_id>", methods=["DELETE"])
@token_required
def remove_from_wishlist(item_id):
    item = WishlistItem.query.filter_by(id=item_id, user_id=g.current_user.id).first()
    if not item:
        return jsonify({"error": "Item not found"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Removed from wishlist"}), 200


@wishlist_bp.route("/move-to-cart/<int:item_id>", methods=["POST"])
@token_required
def move_to_cart(item_id):
    wish_item = WishlistItem.query.filter_by(id=item_id, user_id=g.current_user.id).first()
    if not wish_item:
        return jsonify({"error": "Wishlist item not found"}), 404

    # Add to cart if not already there
    cart_item = CartItem.query.filter_by(
        user_id=g.current_user.id,
        product_id=wish_item.product_id
    ).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user_id=g.current_user.id, product_id=wish_item.product_id, quantity=1)
        db.session.add(cart_item)

    db.session.delete(wish_item)
    db.session.commit()
    return jsonify({"message": "Moved to cart"}), 200
