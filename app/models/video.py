from app import db
from datetime import datetime


class VideoSession(db.Model):
    __tablename__ = "video_sessions"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=False)
    initiator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    session_id = db.Column(db.String(128), unique=True, nullable=False)
    status = db.Column(db.String(32), default="active")
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)

    incident = db.relationship("Incident", back_populates="video_sessions")

    STATUSES = ("active", "ended")

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "initiator_id": self.initiator_id,
            "session_id": self.session_id,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
        }
