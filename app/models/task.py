from app import db
from datetime import datetime


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=True)
    task_type = db.Column(db.String(32), nullable=False)
    priority = db.Column(db.Integer, default=2)
    status = db.Column(db.String(32), default="pending")
    assigned_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    due_by = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    incident = db.relationship("Incident", back_populates="tasks")
    assignments = db.relationship("TaskAssignment", back_populates="task", lazy="dynamic")

    TASK_TYPES = ("logistics", "operational", "administrative", "medical", "other")
    STATUSES = ("pending", "in_progress", "completed", "cancelled")

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type,
            "priority": self.priority,
            "status": self.status,
            "assigned_by": self.assigned_by,
            "due_by": self.due_by.isoformat() if self.due_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "assignments": [a.to_dict() for a in self.assignments.all()],
        }


class TaskAssignment(db.Model):
    __tablename__ = "task_assignments"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    task = db.relationship("Task", back_populates="assignments")
    user = db.relationship("User", back_populates="assigned_tasks")

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "user": self.user.to_dict() if self.user else None,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "notes": self.notes,
        }
