from flask import request
from flask_socketio import join_room, leave_room, emit
from app import socketio, db
from app.models.chat import ChatMessage
from app.models.emergency import EmergencySignal
from app.models.user import User
from app.services.notification_service import NotificationService
from app.services.video_service import VideoService
from datetime import datetime
import jwt
from config import Config


def authenticate_socket():
    token = request.args.get("token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
        user = User.query.get(payload["user_id"])
        return user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


@socketio.on("connect")
def handle_connect():
    user = authenticate_socket()
    if user:
        join_room(f"user_{user.id}")
        emit("connected", {"user_id": user.id})


@socketio.on("disconnect")
def handle_disconnect():
    pass


@socketio.on("join_incident")
def join_incident(data):
    incident_id = data.get("incident_id")
    if incident_id:
        join_room(f"incident_{incident_id}")


@socketio.on("leave_incident")
def leave_incident(data):
    incident_id = data.get("incident_id")
    if incident_id:
        leave_room(f"incident_{incident_id}")


@socketio.on("chat_message")
def handle_chat_message(data):
    user = authenticate_socket()
    if not user:
        return

    channel_id = data.get("channel_id")
    content = data.get("content")
    message_type = data.get("message_type", "text")

    if not channel_id or not content:
        return

    msg = ChatMessage(
        channel_id=channel_id,
        user_id=user.id,
        message_type=message_type,
        content=content,
        template_id=data.get("template_id"),
        photo_id=data.get("photo_id"),
    )
    db.session.add(msg)
    db.session.commit()

    emit(
        "new_message",
        {"message": msg.to_dict()},
        room=f"incident_{msg.channel.incident_id}",
    )


@socketio.on("location_update")
def handle_location_update(data):
    user = authenticate_socket()
    if not user:
        return

    incident_id = data.get("incident_id")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if incident_id and latitude and longitude:
        emit(
            "team_location_update",
            {
                "user_id": user.id,
                "user_name": user.full_name,
                "latitude": latitude,
                "longitude": longitude,
                "incident_id": incident_id,
                "timestamp": datetime.utcnow().isoformat(),
            },
            room=f"incident_{incident_id}",
        )


@socketio.on("emergency_signal")
def handle_emergency_signal(data):
    user = authenticate_socket()
    if not user:
        return

    incident_id = data.get("incident_id")
    signal_type = data.get("signal_type", "mayday")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    message = data.get("message")

    if not incident_id:
        return

    signal = EmergencySignal(
        incident_id=incident_id,
        user_id=user.id,
        signal_type=signal_type,
        latitude=latitude,
        longitude=longitude,
        message=message,
    )
    db.session.add(signal)
    db.session.flush()

    NotificationService.notify_emergency(signal)
    db.session.commit()

    emit(
        "emergency_alert",
        {"signal": signal.to_dict()},
        room=f"incident_{incident_id}",
        broadcast=True,
    )


@socketio.on("marker_updated")
def handle_marker_update(data):
    incident_id = data.get("incident_id")
    if incident_id:
        emit("marker_update", data, room=f"incident_{incident_id}", broadcast=True)


@socketio.on("video_call_start")
def handle_video_call_start(data):
    incident_id = data.get("incident_id")
    session_id = data.get("session_id")
    initiator = authenticate_socket()

    if incident_id and session_id and initiator:
        VideoService.create_session(incident_id, initiator.id)
        emit(
            "video_call_started",
            {"session_id": session_id, "initiator_id": initiator.id, "initiator_name": initiator.full_name},
            room=f"incident_{incident_id}",
            broadcast=True,
        )


@socketio.on("video_call_end")
def handle_video_call_end(data):
    incident_id = data.get("incident_id")
    session_id = data.get("session_id")

    if incident_id and session_id:
        VideoService.end_session(session_id)
        emit(
            "video_call_ended",
            {"session_id": session_id},
            room=f"incident_{incident_id}",
            broadcast=True,
        )
