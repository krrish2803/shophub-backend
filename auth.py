"""
Authentication Routes
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/profile
PUT  /api/auth/profile
POST /api/auth/logout
"""
from flask import Blueprint, request, jsonify, g
from database import db
from models import User
from utils.auth_helpers import generate_token, token_required
import re

auth_bp = Blueprint("auth", __name__)


# ── Register ──────────────────────────────────────────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    # Validation
    required = ["name", "email", "password"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"'{field}' is required"}), 400

    email = data["email"].strip().lower()
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Invalid email format"}), 400
    if len(data["password"]) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(name=data["name"].strip(), email=email)
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    token = generate_token(user.id)
    return jsonify({"message": "Registered successfully", "token": token, "user": user.to_dict()}), 201


# ── Login ─────────────────────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_token(user.id)
    return jsonify({"message": "Login successful", "token": token, "user": user.to_dict()}), 200


# ── Profile GET ───────────────────────────────────────────────────────────────
@auth_bp.route("/profile", methods=["GET"])
@token_required
def get_profile():
    return jsonify({"user": g.current_user.to_dict()}), 200


# ── Profile UPDATE ────────────────────────────────────────────────────────────
@auth_bp.route("/profile", methods=["PUT"])
@token_required
def update_profile():
    data = request.get_json()
    user = g.current_user

    if data.get("name"):
        user.name = data["name"].strip()
    if data.get("avatar_url"):
        user.avatar_url = data["avatar_url"]
    if data.get("new_password"):
        if len(data["new_password"]) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        user.set_password(data["new_password"])

    db.session.commit()
    return jsonify({"message": "Profile updated", "user": user.to_dict()}), 200


# ── Logout (client-side token invalidation; stub endpoint) ───────────────────
@auth_bp.route("/logout", methods=["POST"])
@token_required
def logout():
    # Stateless JWT — client simply discards the token.
    return jsonify({"message": "Logged out successfully"}), 200
