from __future__ import annotations
"""
Auth Helpers
- generate_token  : create JWT for a user
- token_required  : decorator — 401 if no/invalid token
- token_optional  : decorator — sets g.current_user = None if no token
"""
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, g, current_app
from models import User


def generate_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp":     datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        "iat":     datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def _extract_user() -> User | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
        return User.query.get(payload["user_id"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = _extract_user()
        if not user:
            return jsonify({"error": "Unauthorized — valid token required"}), 401
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def token_optional(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        g.current_user = _extract_user()
        return f(*args, **kwargs)
    return decorated
