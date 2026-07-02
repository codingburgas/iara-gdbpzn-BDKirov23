from app import db
from datetime import datetime


class FireTruck(db.Model):
    __tablename__ = "fire_trucks"

    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(32), unique=True, nullable=False)
    model = db.Column(db.String(128), nullable=True)
    type = db.Column(db.String(64), nullable=False)
    capacity = db.Column(db.Integer, nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    gps_device_id = db.Column(db.String(128), nullable=True)
    photo_url = db.Column(db.String(512), nullable=True)
    year_manufactured = db.Column(db.Integer, nullable=True)
    last_service_date = db.Column(db.DateTime, nullable=True)
    mileage_km = db.Column(db.Integer, nullable=True)
    water_tank_l = db.Column(db.Integer, nullable=True)
    foam_tank_l = db.Column(db.Integer, nullable=True)
    equipment_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    teams = db.relationship("Team", back_populates="fire_truck", lazy="dynamic")

    def to_dict(self, include_team=True):
        data = {
            "id": self.id,
            "registration_number": self.registration_number,
            "model": self.model,
            "type": self.type,
            "capacity": self.capacity,
            "is_available": self.is_available,
            "gps_device_id": self.gps_device_id,
            "photo_url": self.photo_url,
            "year_manufactured": self.year_manufactured,
            "last_service_date": self.last_service_date.isoformat() if self.last_service_date else None,
            "mileage_km": self.mileage_km,
            "water_tank_l": self.water_tank_l,
            "foam_tank_l": self.foam_tank_l,
            "equipment_notes": self.equipment_notes,
        }
        if include_team:
            team = self.teams.first()
            data["team"] = {"id": team.id, "name": team.name, "station": team.station} if team else None
        return data


class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    fire_truck_id = db.Column(db.Integer, db.ForeignKey("fire_trucks.id"), nullable=True)
    station = db.Column(db.String(128), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    fire_truck = db.relationship("FireTruck", back_populates="teams")
    members = db.relationship("TeamMember", back_populates="team", lazy="dynamic")
    incident_teams = db.relationship("IncidentTeam", back_populates="team", lazy="dynamic")

    def to_dict(self, include_members=False):
        data = {
            "id": self.id,
            "name": self.name,
            "fire_truck": self.fire_truck.to_dict() if self.fire_truck else None,
            "station": self.station,
            "is_active": self.is_active,
            "member_count": self.members.filter(TeamMember.is_on_shift == True).count(),
        }
        if include_members:
            data["members"] = [
                m.to_dict() for m in self.members.filter(TeamMember.is_on_shift == True).all()
            ]
        return data


class TeamMember(db.Model):
    __tablename__ = "team_members"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    is_team_leader = db.Column(db.Boolean, default=False)
    is_on_shift = db.Column(db.Boolean, default=False)
    shift_start = db.Column(db.DateTime, nullable=True)
    shift_end = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="team_memberships")
    team = db.relationship("Team", back_populates="members")

    def to_dict(self):
        return {
            "id": self.id,
            "user": self.user.to_dict() if self.user else None,
            "team_id": self.team_id,
            "is_team_leader": self.is_team_leader,
            "is_on_shift": self.is_on_shift,
            "shift_start": self.shift_start.isoformat() if self.shift_start else None,
            "shift_end": self.shift_end.isoformat() if self.shift_end else None,
        }


class Shift(db.Model):
    __tablename__ = "shifts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "start_time": self.start_time.strftime("%H:%M") if self.start_time else None,
            "end_time": self.end_time.strftime("%H:%M") if self.end_time else None,
        }
