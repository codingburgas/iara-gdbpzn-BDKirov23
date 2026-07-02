from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user
from app import db
from app.models.user import User
from app.auth_middleware import jwt_required
from datetime import datetime, timedelta
import jwt
from config import Config

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is deactivated"}), 403

    login_user(user)

    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS),
        },
        Config.JWT_SECRET_KEY,
        algorithm="HS256",
    )

    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    required = ("email", "password", "first_name", "last_name", "role")
    if not data or not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    if data["role"] not in User.ROLES:
        return jsonify({"error": f"Invalid role. Must be one of: {User.ROLES}"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(
        email=data["email"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone=data.get("phone"),
        rank=data.get("rank"),
        role=data["role"],
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS),
        },
        Config.JWT_SECRET_KEY,
        algorithm="HS256",
    )

    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.route("/me", methods=["GET"])
@jwt_required
def get_current_user():
    return jsonify({"user": current_user.to_dict()}), 200


@auth_bp.route("/me", methods=["PUT"])
@jwt_required
def update_current_user():
    data = request.get_json()
    user = current_user
    for field in ("first_name", "last_name", "phone", "rank"):
        if field in data:
            setattr(user, field, data[field])
    if "fcm_token" in data:
        user.fcm_token = data["fcm_token"]
    db.session.commit()
    return jsonify({"user": user.to_dict()}), 200
