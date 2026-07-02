from app import db
from datetime import datetime


class MapMarker(db.Model):
    __tablename__ = "map_markers"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    marker_type = db.Column(db.String(32), nullable=False)
    label = db.Column(db.String(256), nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    radius = db.Column(db.Float, nullable=True)
    color = db.Column(db.String(16), nullable=True)
    icon = db.Column(db.String(64), nullable=True)
    is_visible_to_all = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    incident = db.relationship("Incident", back_populates="map_markers")

    MARKER_TYPES = (
        "fire_front",
        "wind_direction",
        "danger_zone",
        "assembly_point",
        "water_source",
        "hazard",
        "team_position",
        "casualty",
        "other",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "user_id": self.user_id,
            "marker_type": self.marker_type,
            "label": self.label,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "radius": self.radius,
            "color": self.color,
            "icon": self.icon,
            "is_visible_to_all": self.is_visible_to_all,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
