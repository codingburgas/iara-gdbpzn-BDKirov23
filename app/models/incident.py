from app import db
from datetime import datetime


class IncidentType(db.Model):
    __tablename__ = "incident_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    code = db.Column(db.String(16), nullable=False, unique=True)
    category = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "category": self.category,
            "description": self.description,
        }


class HazardousMaterial(db.Model):
    __tablename__ = "hazardous_materials"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    un_number = db.Column(db.String(16), nullable=True)
    hazard_class = db.Column(db.String(32), nullable=True)
    description = db.Column(db.Text, nullable=True)
    handling_instructions = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "un_number": self.un_number,
            "hazard_class": self.hazard_class,
            "description": self.description,
            "handling_instructions": self.handling_instructions,
        }


class ActionPlan(db.Model):
    __tablename__ = "action_plans"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=True)
    steps = db.Column(db.JSON, nullable=True)
    priority = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    incident = db.relationship("Incident", back_populates="action_plans")

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "title": self.title,
            "description": self.description,
            "steps": self.steps,
            "priority": self.priority,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


incident_hazardous_materials = db.Table(
    "incident_hazardous_materials",
    db.Column("incident_id", db.Integer, db.ForeignKey("incidents.id"), primary_key=True),
    db.Column("hazardous_material_id", db.Integer, db.ForeignKey("hazardous_materials.id"), primary_key=True),
)


class Incident(db.Model):
    __tablename__ = "incidents"

    id = db.Column(db.Integer, primary_key=True)
    incident_number = db.Column(db.String(32), unique=True, nullable=False)
    incident_type_id = db.Column(db.Integer, db.ForeignKey("incident_types.id"), nullable=False)
    channel = db.Column(db.String(32), default="112")
    status = db.Column(db.String(32), default="registered")
    priority = db.Column(db.Integer, default=3)

    address = db.Column(db.String(256), nullable=True)
    city = db.Column(db.String(128), nullable=True)
    region = db.Column(db.String(128), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    description = db.Column(db.Text, nullable=True)
    reported_by = db.Column(db.String(128), nullable=True)
    reporter_phone = db.Column(db.String(20), nullable=True)
    casualties = db.Column(db.Integer, default=0)
    injured = db.Column(db.Integer, default=0)

    fire_front_coords = db.Column(db.JSON, nullable=True)
    wind_direction = db.Column(db.String(16), nullable=True)
    wind_speed = db.Column(db.Float, nullable=True)

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_dispatcher = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)

    incident_type = db.relationship("IncidentType")
    action_plans = db.relationship("ActionPlan", back_populates="incident", lazy="dynamic")
    incident_teams = db.relationship("IncidentTeam", back_populates="incident", lazy="dynamic")
    tasks = db.relationship("Task", back_populates="incident", lazy="dynamic")
    chat_channel = db.relationship("ChatChannel", back_populates="incident", uselist=False)
    map_markers = db.relationship("MapMarker", back_populates="incident", lazy="dynamic")
    video_sessions = db.relationship("VideoSession", back_populates="incident", lazy="dynamic")
    emergency_signals = db.relationship("EmergencySignal", back_populates="incident", lazy="dynamic")
    photos = db.relationship("IncidentPhoto", back_populates="incident", lazy="dynamic")
    logs = db.relationship("IncidentLog", back_populates="incident", lazy="dynamic")
    hazardous_materials = db.relationship(
        "HazardousMaterial", secondary=incident_hazardous_materials, lazy="subquery"
    )
    resource_requests = db.relationship("ResourceRequest", back_populates="incident", lazy="dynamic")

    STATUSES = ("registered", "dispatched", "en_route", "on_scene", "in_progress", "contained", "closed")
    CHANNELS = ("112", "direct_call", "radio", "citizen_report", "other")

    def to_dict(self, include_relations=False):
        data = {
            "id": self.id,
            "incident_number": self.incident_number,
            "incident_type": self.incident_type.to_dict() if self.incident_type else None,
            "channel": self.channel,
            "status": self.status,
            "priority": self.priority,
            "address": self.address,
            "city": self.city,
            "region": self.region,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "description": self.description,
            "reported_by": self.reported_by,
            "reporter_phone": self.reporter_phone,
            "casualties": self.casualties,
            "injured": self.injured,
            "fire_front_coords": self.fire_front_coords,
            "wind_direction": self.wind_direction,
            "wind_speed": self.wind_speed,
            "created_by": self.created_by,
            "assigned_dispatcher": self.assigned_dispatcher,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
        }
        if include_relations:
            data["teams"] = [it.to_dict() for it in self.incident_teams.all()]
            data["action_plans"] = [ap.to_dict() for ap in self.action_plans.all()]
            data["hazardous_materials"] = [hm.to_dict() for hm in self.hazardous_materials]
            data["photos"] = [p.to_dict() for p in self.photos.all()]
        return data


class IncidentTeam(db.Model):
    __tablename__ = "incident_teams"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    status = db.Column(db.String(32), default="dispatched")
    dispatched_at = db.Column(db.DateTime, default=datetime.utcnow)
    arrived_at = db.Column(db.DateTime, nullable=True)
    departed_at = db.Column(db.DateTime, nullable=True)

    incident = db.relationship("Incident", back_populates="incident_teams")
    team = db.relationship("Team", back_populates="incident_teams")

    STATUSES = ("dispatched", "en_route", "on_scene", "returning", "completed")

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "team": self.team.to_dict() if self.team else None,
            "status": self.status,
            "dispatched_at": self.dispatched_at.isoformat() if self.dispatched_at else None,
            "arrived_at": self.arrived_at.isoformat() if self.arrived_at else None,
            "departed_at": self.departed_at.isoformat() if self.departed_at else None,
        }


class IncidentPhoto(db.Model):
    __tablename__ = "incident_photos"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    filename = db.Column(db.String(256), nullable=False)
    caption = db.Column(db.Text, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    incident = db.relationship("Incident", back_populates="photos")

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "user_id": self.user_id,
            "filename": self.filename,
            "caption": self.caption,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "url": f"/static/uploads/{self.filename}",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class IncidentLog(db.Model):
    __tablename__ = "incident_logs"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String(128), nullable=False)
    details = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    incident = db.relationship("Incident", back_populates="logs")

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "user_id": self.user_id,
            "action": self.action,
            "details": self.details,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
