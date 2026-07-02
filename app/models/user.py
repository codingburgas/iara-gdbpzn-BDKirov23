from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    rank = db.Column(db.String(64), nullable=True)
    role = db.Column(db.String(32), nullable=False, default="firefighter")
    is_active = db.Column(db.Boolean, default=True)
    fcm_token = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    team_memberships = db.relationship("TeamMember", back_populates="user", lazy="dynamic")
    leaves = db.relationship("Leave", back_populates="user", lazy="dynamic", foreign_keys="Leave.user_id")
    assigned_tasks = db.relationship("TaskAssignment", back_populates="user", lazy="dynamic")
    chat_messages = db.relationship("ChatMessage", back_populates="user", lazy="dynamic")
    notifications = db.relationship("Notification", back_populates="user", lazy="dynamic")
    emergency_signals = db.relationship("EmergencySignal", back_populates="user", lazy="dynamic", foreign_keys="EmergencySignal.user_id")
    approved_leaves = db.relationship("Leave", foreign_keys="Leave.approved_by", back_populates="approved_by_user", lazy="dynamic")

    ROLES = ("firefighter", "team_leader", "dispatcher", "commander", "admin")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "phone": self.phone,
            "rank": self.rank,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<User {self.email}>"
