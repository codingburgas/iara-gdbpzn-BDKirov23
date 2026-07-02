from app import db
from datetime import datetime


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=True)
    title = db.Column(db.String(256), nullable=False)
    body = db.Column(db.Text, nullable=True)
    notification_type = db.Column(db.String(64), nullable=False)
    data = db.Column(db.JSON, nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="notifications")

    NOTIFICATION_TYPES = (
        "new_incident",
        "task_assigned",
        "status_change",
        "emergency_alert",
        "chat_message",
        "resource_update",
        "shift_reminder",
        "general",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "incident_id": self.incident_id,
            "title": self.title,
            "body": self.body,
            "notification_type": self.notification_type,
            "data": self.data,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
