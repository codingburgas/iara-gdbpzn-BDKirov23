from app import db
from datetime import datetime


class EmergencySignal(db.Model):
    __tablename__ = "emergency_signals"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    signal_type = db.Column(db.String(32), default="mayday")
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(32), default="active")
    acknowledged_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    incident = db.relationship("Incident", back_populates="emergency_signals")
    user = db.relationship("User", back_populates="emergency_signals", foreign_keys=[user_id])
    acknowledged_by_user = db.relationship("User", foreign_keys=[acknowledged_by])

    SIGNAL_TYPES = ("mayday", "injury", "trapped", "lost", "equipment_failure", "other")
    STATUSES = ("active", "acknowledged", "resolved")

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "user": self.user.to_dict() if self.user else None,
            "signal_type": self.signal_type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "message": self.message,
            "status": self.status,
            "acknowledged_by": self.acknowledged_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }
