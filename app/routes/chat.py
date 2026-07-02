from flask import Blueprint, request, jsonify
from flask_login import current_user
from app import db
from app.auth_middleware import jwt_required
from app.models.chat import ChatChannel, ChatMessage, ChatTemplate
from app.models.incident import Incident
from app.services.ai_service import AIService
from app.services.ai_chat_service import ai_chat_service

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/channels/<int:incident_id>", methods=["GET"])
@jwt_required
def get_channel(incident_id):
    channel = ChatChannel.query.filter_by(incident_id=incident_id).first()
    if not channel:
        return jsonify({"error": "No chat channel for this incident"}), 404
    return jsonify({"channel": channel.to_dict()}), 200


@chat_bp.route("/messages/<int:channel_id>", methods=["GET"])
@jwt_required
def get_messages(channel_id):
    channel = ChatChannel.query.get_or_404(channel_id)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    messages = ChatMessage.query.filter_by(channel_id=channel.id)\
        .order_by(ChatMessage.created_at.asc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "messages": [m.to_dict() for m in messages.items],
        "total": messages.total,
        "page": page,
    }), 200


@chat_bp.route("/messages", methods=["POST"])
@jwt_required
def send_message():
    data = request.get_json()
    required = ("channel_id", "content")
    if not data or not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    channel = ChatChannel.query.get(data["channel_id"])
    if not channel:
        return jsonify({"error": "Channel not found"}), 404

    message_type = data.get("message_type", "text")
    if message_type not in ChatMessage.MESSAGE_TYPES:
        return jsonify({"error": f"Invalid message type: {message_type}"}), 400

    msg = ChatMessage(
        channel_id=channel.id,
        user_id=current_user.id,
        message_type=message_type,
        content=data["content"],
        template_id=data.get("template_id"),
        photo_id=data.get("photo_id"),
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify({"message": msg.to_dict()}), 201


@chat_bp.route("/templates", methods=["GET"])
@jwt_required
def list_templates():
    category = request.args.get("category")
    query = ChatTemplate.query.filter_by(is_active=True)
    if category:
        query = query.filter_by(category=category)
    templates = query.all()
    return jsonify({"templates": [t.to_dict() for t in templates]}), 200


@chat_bp.route("/templates", methods=["POST"])
@jwt_required
def create_template():
    data = request.get_json()
    required = ("category", "message_text")
    if not data or not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    if data["category"] not in ChatTemplate.CATEGORIES:
        return jsonify({"error": f"Invalid category: {data['category']}"}), 400

    template = ChatTemplate(
        category=data["category"],
        message_text=data["message_text"],
    )
    db.session.add(template)
    db.session.commit()
    return jsonify({"template": template.to_dict()}), 201


@chat_bp.route("/ai-suggest", methods=["POST"])
@jwt_required
def ai_suggest():
    data = request.get_json()
    incident_id = data.get("incident_id") if data else None
    last_message = data.get("last_message") if data else None

    suggestions = AIService.suggest_response(incident_id, last_message)
    return jsonify({"suggestions": suggestions}), 200


@chat_bp.route("/ai-auto-reply", methods=["POST"])
@jwt_required
def ai_auto_reply():
    data = request.get_json()
    incident_id = data.get("incident_id") if data else None
    channel_id = data.get("channel_id") if data else None
    user_message = (data.get("message") or "") if data else ""

    reply = AIService.auto_reply(incident_id, channel_id, user_message)

    channel = ChatChannel.query.get(channel_id) if channel_id else None

    result = {
        "has_reply": reply is not None,
        "reply": reply if reply else "No automatic reply available",
    }

    return jsonify(result), 200


@chat_bp.route("/ai-chat", methods=["POST"])
@jwt_required
def ai_chat():
    data = request.get_json() or {}
    message = data.get("message", "")
    incident_id = data.get("incident_id")

    if not message:
        return jsonify({"error": "Message is required"}), 400

    response = ai_chat_service.get_response(current_user.id, message, incident_id)

    return jsonify({
        "response": response,
        "user_message": message,
    }), 200
