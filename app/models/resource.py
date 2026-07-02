from app import db
from datetime import datetime


class Resource(db.Model):
    __tablename__ = "resources"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    resource_type = db.Column(db.String(64), nullable=False)
    quantity_available = db.Column(db.Float, default=0)
    unit = db.Column(db.String(32), nullable=True)
    storage_location = db.Column(db.String(256), nullable=True)
    is_consumable = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    TYPE_CHOICES = ("water", "fuel", "foam", "equipment", "vehicle", "medical", "food", "other")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "resource_type": self.resource_type,
            "quantity_available": self.quantity_available,
            "unit": self.unit,
            "storage_location": self.storage_location,
            "is_consumable": self.is_consumable,
        }


class ResourceRequest(db.Model):
    __tablename__ = "resource_requests"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    requested_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(32), default="pending")
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    fulfilled_at = db.Column(db.DateTime, nullable=True)

    incident = db.relationship("Incident", back_populates="resource_requests")
    resource = db.relationship("Resource")

    STATUSES = ("pending", "approved", "in_transit", "delivered", "rejected")

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "resource": self.resource.to_dict() if self.resource else None,
            "quantity": self.quantity,
            "requested_by": self.requested_by,
            "status": self.status,
            "approved_by": self.approved_by,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "fulfilled_at": self.fulfilled_at.isoformat() if self.fulfilled_at else None,
        }
