from app import db
from datetime import datetime


class ChatChannel(db.Model):
    __tablename__ = "chat_channels"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=False, unique=True)
    name = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    incident = db.relationship("Incident", back_populates="chat_channel")
    messages = db.relationship("ChatMessage", back_populates="channel", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "name": self.name or (f"Incident #{self.incident.incident_number}" if self.incident else None),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ChatTemplate(db.Model):
    __tablename__ = "chat_templates"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(64), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    CATEGORIES = (
        "status_update",
        "resource_request",
        "arrival_notification",
        "emergency",
        "coordination",
        "general",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "message_text": self.message_text,
            "is_active": self.is_active,
        }


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey("chat_channels.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message_type = db.Column(db.String(16), default="text")
    content = db.Column(db.Text, nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey("chat_templates.id"), nullable=True)
    photo_id = db.Column(db.Integer, db.ForeignKey("incident_photos.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    channel = db.relationship("ChatChannel", back_populates="messages")
    user = db.relationship("User", back_populates="chat_messages")
    template = db.relationship("ChatTemplate")

    MESSAGE_TYPES = ("text", "template", "photo", "system")

    def to_dict(self):
        return {
            "id": self.id,
            "channel_id": self.channel_id,
            "user": self.user.to_dict() if self.user else None,
            "message_type": self.message_type,
            "content": self.content,
            "template_id": self.template_id,
            "photo_id": self.photo_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
