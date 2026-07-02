from functools import wraps
from flask import request, jsonify, g
from app.models.user import User
import jwt
from config import Config
from flask_login import login_user


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ", 1)[1] if " " in auth_header else ""

        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            user = User.query.get(payload.get("user_id"))
            if not user or not user.is_active:
                return jsonify({"error": "Invalid or inactive user"}), 401
            login_user(user)
            g.current_user = user
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated
