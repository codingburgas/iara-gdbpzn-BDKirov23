from flask import Blueprint, request, jsonify
from flask_login import current_user
from app import db
from app.auth_middleware import jwt_required
from app.models.notification import Notification

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("", methods=["GET"])
@jwt_required
def get_notifications():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    unread_only = request.args.get("unread_only", type=bool, default=False)

    query = Notification.query.filter_by(user_id=current_user.id)
    if unread_only:
        query = query.filter_by(is_read=False)
    query = query.order_by(Notification.created_at.desc())

    notifications = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "notifications": [n.to_dict() for n in notifications.items],
        "total": notifications.total,
        "unread_count": Notification.query.filter_by(user_id=current_user.id, is_read=False).count(),
        "page": page,
    }), 200


@notifications_bp.route("/<int:notification_id>/read", methods=["POST"])
@jwt_required
def mark_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    notification.is_read = True
    db.session.commit()
    return jsonify({"notification": notification.to_dict()}), 200


@notifications_bp.route("/read-all", methods=["POST"])
@jwt_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False)\
        .update({"is_read": True})
    db.session.commit()
    return jsonify({"message": "All notifications marked as read"}), 200


@notifications_bp.route("/register-device", methods=["POST"])
@jwt_required
def register_device():
    data = request.get_json()
    fcm_token = data.get("fcm_token") if data else None
    if not fcm_token:
        return jsonify({"error": "fcm_token is required"}), 400
    current_user.fcm_token = fcm_token
    db.session.commit()
    return jsonify({"message": "Device registered"}), 200
