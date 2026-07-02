from flask import Blueprint, request, jsonify
from flask_login import current_user
from app import db
from app.auth_middleware import jwt_required
from app.models.task import Task, TaskAssignment
from app.services.notification_service import NotificationService
from datetime import datetime

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("", methods=["POST"])
@jwt_required
def create_task():
    data = request.get_json()
    required = ("incident_id", "title", "task_type")
    if not data or not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    if data["task_type"] not in Task.TASK_TYPES:
        return jsonify({"error": f"Invalid task type. Must be one of: {Task.TASK_TYPES}"}), 400

    task = Task(
        incident_id=data["incident_id"],
        title=data["title"],
        description=data.get("description"),
        task_type=data["task_type"],
        priority=data.get("priority", 2),
        assigned_by=current_user.id,
        due_by=datetime.fromisoformat(data["due_by"]) if data.get("due_by") else None,
    )
    db.session.add(task)
    db.session.flush()

    if data.get("assigned_user_ids"):
        for user_id in data["assigned_user_ids"]:
            assignment = TaskAssignment(task_id=task.id, user_id=user_id)
            db.session.add(assignment)
            NotificationService.notify_user(
                user_id=user_id,
                title="New Task Assigned",
                body=f"Task: {task.title}",
                notification_type="task_assigned",
                incident_id=data["incident_id"],
                data={"task_id": task.id},
            )

    db.session.commit()
    return jsonify({"task": task.to_dict()}), 201


@tasks_bp.route("/incident/<int:incident_id>", methods=["GET"])
@jwt_required
def list_tasks(incident_id):
    tasks = Task.query.filter_by(incident_id=incident_id).order_by(Task.priority.desc(), Task.created_at.asc()).all()
    return jsonify({"tasks": [t.to_dict() for t in tasks]}), 200


@tasks_bp.route("/<int:task_id>", methods=["PUT"])
@jwt_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()

    updatable = ("title", "description", "priority", "status", "due_by")
    for field in updatable:
        if field in data:
            if field == "due_by" and data[field]:
                setattr(task, field, datetime.fromisoformat(data[field]))
            else:
                setattr(task, field, data[field])

    if data.get("status") == "completed":
        task.completed_at = datetime.utcnow()

    db.session.commit()
    return jsonify({"task": task.to_dict()}), 200


@tasks_bp.route("/<int:task_id>/assign", methods=["POST"])
@jwt_required
def assign_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    assignment = TaskAssignment(task_id=task.id, user_id=user_id)
    db.session.add(assignment)
    db.session.commit()

    NotificationService.notify_user(
        user_id=user_id,
        title="Task Assigned",
        body=f"Task: {task.title}",
        notification_type="task_assigned",
        incident_id=task.incident_id,
        data={"task_id": task.id},
    )

    return jsonify({"assignment": assignment.to_dict()}), 201


@tasks_bp.route("/assignments/<int:assignment_id>/complete", methods=["POST"])
@jwt_required
def complete_assignment(assignment_id):
    assignment = TaskAssignment.query.get_or_404(assignment_id)
    assignment.completed_at = datetime.utcnow()
    assignment.notes = request.get_json().get("notes") if request.get_json() else None
    db.session.commit()
    return jsonify({"assignment": assignment.to_dict()}), 200


@tasks_bp.route("/my", methods=["GET"])
@jwt_required
def get_my_tasks():
    assignments = TaskAssignment.query.filter_by(
        user_id=current_user.id, completed_at=None
    ).all()
    return jsonify({
        "tasks": [a.task.to_dict() for a in assignments if a.task]
    }), 200
