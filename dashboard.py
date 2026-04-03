"""
Dashboard Routes  (auth required)
GET /api/dashboard/summary         - user stats (orders, wishlist, cart, emotion)
GET /api/dashboard/orders          - order history
GET /api/dashboard/emotion-stats   - aggregated emotion analytics
"""
from flask import Blueprint, jsonify, g
from database import db
from models import Order, CartItem, WishlistItem, EmotionLog
from utils.auth_helpers import token_required
from sqlalchemy import func

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/summary", methods=["GET"])
@token_required
def summary():
    user = g.current_user

    order_count    = Order.query.filter_by(user_id=user.id).count()
    total_spent    = db.session.query(func.sum(Order.total_amount)).filter_by(user_id=user.id).scalar() or 0
    cart_count     = db.session.query(func.sum(CartItem.quantity)).filter_by(user_id=user.id).scalar() or 0
    wishlist_count = WishlistItem.query.filter_by(user_id=user.id).count()
    emotion_count  = EmotionLog.query.filter_by(user_id=user.id).count()

    return jsonify({
        "user":           user.to_dict(),
        "total_orders":   order_count,
        "total_spent":    round(float(total_spent), 2),
        "cart_items":     int(cart_count),
        "wishlist_items": wishlist_count,
        "emotion_sessions": emotion_count,
    }), 200


@dashboard_bp.route("/orders", methods=["GET"])
@token_required
def order_history():
    orders = (
        Order.query
        .filter_by(user_id=g.current_user.id)
        .order_by(Order.placed_at.desc())
        .all()
    )
    return jsonify({"orders": [o.to_dict() for o in orders]}), 200


@dashboard_bp.route("/emotion-stats", methods=["GET"])
@token_required
def emotion_stats():
    rows = (
        db.session.query(EmotionLog.detected_emotion, func.count(EmotionLog.id).label("count"))
        .filter_by(user_id=g.current_user.id)
        .group_by(EmotionLog.detected_emotion)
        .all()
    )
    stats = {row.detected_emotion: row.count for row in rows}
    total = sum(stats.values())
    pct   = {k: round(v / total * 100, 1) for k, v in stats.items()} if total else {}

    return jsonify({
        "emotion_counts":      stats,
        "emotion_percentages": pct,
        "total_detections":    total,
    }), 200
