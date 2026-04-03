"""
Emotion Detection & Recommendation Routes
POST /api/emotion/detect          - receive base64 frame, return emotion + products
GET  /api/emotion/recommend/<em>  - get products for explicit emotion
GET  /api/emotion/history         - user's emotion log (auth required)
"""
from flask import Blueprint, request, jsonify, g, current_app
from models import Product, EmotionLog
from database import db
from utils.auth_helpers import token_optional
from utils.emotion_engine import EmotionEngine
import json, uuid

emotion_bp = Blueprint("emotion", __name__)
_engine = EmotionEngine()   # singleton; loads FER model once


# ── EMOTION_PRODUCT_MAP ────────────────────────────────────────────────────────
# Maps each detected emotion to preferred product tags/categories.
EMOTION_PRODUCT_MAP = {
    "happy":    {"tags": ["colorful", "party", "casual", "summer", "vibrant"],  "boost_discount": False},
    "sad":      {"tags": ["cozy",    "comfort", "warm",  "soft",  "neutral"],   "boost_discount": True},
    "angry":    {"tags": ["sport",   "activewear","running","training","bold"],  "boost_discount": True},
    "surprise": {"tags": ["trending","new",     "limited","unique","statement"],"boost_discount": False},
    "fear":     {"tags": ["cozy",    "home",    "comfort","soft",  "basics"],   "boost_discount": True},
    "disgust":  {"tags": ["classic", "minimal", "simple","clean", "timeless"], "boost_discount": False},
    "neutral":  {"tags": ["popular", "recommended","bestseller","essentials"],  "boost_discount": False},
}

EMOTION_MESSAGES = {
    "happy":    "You're glowing! ✨ Here are vibrant picks to match your mood.",
    "sad":      "A little retail therapy? 🛍️ Here are some comforting favourites.",
    "angry":    "Channel that energy! 💪 Check out these power picks.",
    "surprise": "Feeling adventurous? 🎉 Here are some exciting new arrivals.",
    "fear":     "Let's keep it cosy 🏠 — here are some feel-good essentials.",
    "disgust":  "Clean. Classic. Timeless. 🕊️ Just the way you like it.",
    "neutral":  "Looking for something great? 🌟 Here are our top picks for you.",
}


# ── DETECT ─────────────────────────────────────────────────────────────────────
@emotion_bp.route("/detect", methods=["POST"])
@token_optional
def detect_emotion():
    """
    Accepts a JSON body:
        { "image": "<base64-encoded JPEG/PNG frame>" }

    Returns detected emotion + recommended products.
    """
    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "No image data provided"}), 400

    threshold   = current_app.config.get("EMOTION_CONFIDENCE_THRESHOLD", 0.40)
    limit       = current_app.config.get("EMOTION_RECOMMENDATION_LIMIT", 8)

    # ── Run emotion engine ────────────────────────────────────────────────────
    result = _engine.detect(data["image"])

    if result["error"]:
        return jsonify({"error": result["error"]}), 422

    emotion    = result["emotion"]
    confidence = result["confidence"]
    all_scores = result["all_scores"]

    # Fall back to neutral if below threshold
    if confidence < threshold:
        emotion = "neutral"

    # ── Persist log ───────────────────────────────────────────────────────────
    log = EmotionLog(
        user_id          = g.current_user.id if g.current_user else None,
        detected_emotion = emotion,
        confidence       = confidence,
        all_scores       = json.dumps(all_scores),
        session_id       = data.get("session_id", str(uuid.uuid4())),
        ip_address       = request.remote_addr,
    )
    db.session.add(log)
    db.session.commit()

    # ── Fetch recommended products ────────────────────────────────────────────
    products  = _get_products_for_emotion(emotion, limit)
    em_config = EMOTION_PRODUCT_MAP.get(emotion, EMOTION_PRODUCT_MAP["neutral"])

    return jsonify({
        "emotion":     emotion,
        "confidence":  round(confidence, 4),
        "all_scores":  all_scores,
        "message":     EMOTION_MESSAGES.get(emotion, EMOTION_MESSAGES["neutral"]),
        "boost_discount": em_config["boost_discount"],
        "products":    [p.to_dict() for p in products],
    }), 200


# ── RECOMMEND BY EMOTION (explicit) ───────────────────────────────────────────
@emotion_bp.route("/recommend/<string:emotion>", methods=["GET"])
def recommend_by_emotion(emotion):
    emotion = emotion.lower()
    if emotion not in EMOTION_PRODUCT_MAP:
        emotion = "neutral"

    limit    = request.args.get("limit", 8, type=int)
    products = _get_products_for_emotion(emotion, limit)

    return jsonify({
        "emotion":  emotion,
        "message":  EMOTION_MESSAGES.get(emotion),
        "products": [p.to_dict() for p in products],
    }), 200


# ── EMOTION HISTORY ───────────────────────────────────────────────────────────
@emotion_bp.route("/history", methods=["GET"])
def emotion_history():
    """Returns aggregated emotion history for the current session."""
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"logs": []}), 200

    logs = (
        EmotionLog.query
        .filter_by(session_id=session_id)
        .order_by(EmotionLog.detected_at.desc())
        .limit(20)
        .all()
    )
    return jsonify({"logs": [l.to_dict() for l in logs]}), 200


# ── Helper ─────────────────────────────────────────────────────────────────────
def _get_products_for_emotion(emotion: str, limit: int):
    """
    Strategy:
    1. Try products with matching emotion_tags.
    2. Supplement with top-rated / discounted products up to `limit`.
    """
    em_config  = EMOTION_PRODUCT_MAP.get(emotion, EMOTION_PRODUCT_MAP["neutral"])
    tag_list   = em_config["tags"]
    boost_disc = em_config["boost_discount"]

    from sqlalchemy import or_
    tag_filters = [Product.emotion_tags.ilike(f"%{t}%") for t in tag_list]
    emotion_matches = (
        Product.query
        .filter(or_(*tag_filters))
        .order_by(Product.discount_pct.desc() if boost_disc else Product.rating.desc())
        .limit(limit)
        .all()
    )

    if len(emotion_matches) >= limit:
        return emotion_matches

    # Supplement
    existing_ids = [p.id for p in emotion_matches]
    supplement = (
        Product.query
        .filter(Product.id.notin_(existing_ids))
        .order_by(Product.rating.desc())
        .limit(limit - len(emotion_matches))
        .all()
    )
    return emotion_matches + supplement
