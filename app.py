"""
ShopHub - Emotion-Aware E-Commerce Backend
Flask Application Entry Point
"""

from flask import Flask
from flask_cors import CORS
from config import Config
from routes.auth import auth_bp
from routes.shop import shop_bp
from routes.emotion import emotion_bp
from routes.wishlist import wishlist_bp
from routes.cart import cart_bp
from routes.dashboard import dashboard_bp
from database import db
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp,      url_prefix="/api/auth")
    app.register_blueprint(shop_bp,      url_prefix="/api/shop")
    app.register_blueprint(emotion_bp,   url_prefix="/api/emotion")
    app.register_blueprint(wishlist_bp,  url_prefix="/api/wishlist")
    app.register_blueprint(cart_bp,      url_prefix="/api/cart")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    # Create tables on first run
    with app.app_context():
        db.create_all()
        from utils.seed import seed_products
        seed_products()
        logger.info("Database ready.")

    @app.route("/api/health", methods=["GET"])
    def health():
        return {"status": "ok", "message": "ShopHub backend is running"}, 200

    return app


import os

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
