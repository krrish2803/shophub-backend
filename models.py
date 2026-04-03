"""
ShopHub Database Models
"""
from database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# ─────────────────────────────────────────────────────────────────────────────
# User
# ─────────────────────────────────────────────────────────────────────────────
class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar_url    = db.Column(db.String(500), nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    cart_items    = db.relationship("CartItem",    backref="user", lazy=True, cascade="all, delete-orphan")
    wishlist_items= db.relationship("WishlistItem",backref="user", lazy=True, cascade="all, delete-orphan")
    orders        = db.relationship("Order",       backref="user", lazy=True)
    emotion_logs  = db.relationship("EmotionLog",  backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id":         self.id,
            "name":       self.name,
            "email":      self.email,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat(),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Product
# ─────────────────────────────────────────────────────────────────────────────
class Product(db.Model):
    __tablename__ = "products"

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(200), nullable=False)
    brand           = db.Column(db.String(100), nullable=False)
    category        = db.Column(db.String(100), nullable=False)   # clothing / footwear / accessories
    sub_category    = db.Column(db.String(100), nullable=True)
    price           = db.Column(db.Float, nullable=False)
    original_price  = db.Column(db.Float, nullable=True)
    discount_pct    = db.Column(db.Integer, default=0)            # 0–100
    rating          = db.Column(db.Float, default=4.0)
    review_count    = db.Column(db.Integer, default=0)
    image_url       = db.Column(db.String(500), nullable=True)
    description     = db.Column(db.Text, nullable=True)
    tags            = db.Column(db.String(500), nullable=True)    # comma-separated
    stock           = db.Column(db.Integer, default=100)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    # Emotion mapping tags (comma-separated): happy,surprise,neutral …
    emotion_tags    = db.Column(db.String(200), nullable=True)

    def to_dict(self):
        return {
            "id":            self.id,
            "name":          self.name,
            "brand":         self.brand,
            "category":      self.category,
            "sub_category":  self.sub_category,
            "price":         self.price,
            "original_price":self.original_price,
            "discount_pct":  self.discount_pct,
            "rating":        self.rating,
            "review_count":  self.review_count,
            "image_url":     self.image_url,
            "description":   self.description,
            "tags":          self.tags.split(",") if self.tags else [],
            "stock":         self.stock,
        }


# ─────────────────────────────────────────────────────────────────────────────
# CartItem
# ─────────────────────────────────────────────────────────────────────────────
class CartItem(db.Model):
    __tablename__ = "cart_items"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity   = db.Column(db.Integer, default=1)
    size       = db.Column(db.String(20), nullable=True)
    color      = db.Column(db.String(50), nullable=True)
    added_at   = db.Column(db.DateTime, default=datetime.utcnow)

    product    = db.relationship("Product")

    def to_dict(self):
        return {
            "id":       self.id,
            "product":  self.product.to_dict(),
            "quantity": self.quantity,
            "size":     self.size,
            "color":    self.color,
            "subtotal": round(self.product.price * self.quantity, 2),
        }


# ─────────────────────────────────────────────────────────────────────────────
# WishlistItem
# ─────────────────────────────────────────────────────────────────────────────
class WishlistItem(db.Model):
    __tablename__ = "wishlist_items"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    added_at   = db.Column(db.DateTime, default=datetime.utcnow)

    product    = db.relationship("Product")

    def to_dict(self):
        return {
            "id":       self.id,
            "product":  self.product.to_dict(),
            "added_at": self.added_at.isoformat(),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Order
# ─────────────────────────────────────────────────────────────────────────────
class Order(db.Model):
    __tablename__ = "orders"

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status       = db.Column(db.String(50), default="pending")  # pending/confirmed/shipped/delivered/cancelled
    payment_mode = db.Column(db.String(50), nullable=True)
    address      = db.Column(db.Text, nullable=True)
    placed_at    = db.Column(db.DateTime, default=datetime.utcnow)

    items        = db.relationship("OrderItem", backref="order", lazy=True)

    def to_dict(self):
        return {
            "id":           self.id,
            "total_amount": self.total_amount,
            "status":       self.status,
            "payment_mode": self.payment_mode,
            "placed_at":    self.placed_at.isoformat(),
            "items":        [i.to_dict() for i in self.items],
        }


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity   = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)

    product    = db.relationship("Product")

    def to_dict(self):
        return {
            "product":    self.product.to_dict(),
            "quantity":   self.quantity,
            "unit_price": self.unit_price,
            "subtotal":   round(self.unit_price * self.quantity, 2),
        }


# ─────────────────────────────────────────────────────────────────────────────
# EmotionLog  (audit trail of every emotion detection event)
# ─────────────────────────────────────────────────────────────────────────────
class EmotionLog(db.Model):
    __tablename__ = "emotion_logs"

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    detected_emotion= db.Column(db.String(50), nullable=False)
    confidence      = db.Column(db.Float, nullable=False)
    all_scores      = db.Column(db.Text, nullable=True)   # JSON string
    session_id      = db.Column(db.String(100), nullable=True)
    ip_address      = db.Column(db.String(50), nullable=True)
    detected_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            "id":               self.id,
            "detected_emotion": self.detected_emotion,
            "confidence":       self.confidence,
            "all_scores":       json.loads(self.all_scores) if self.all_scores else {},
            "detected_at":      self.detected_at.isoformat(),
        }
