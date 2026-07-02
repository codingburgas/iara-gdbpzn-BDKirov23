from flask import Blueprint, request, jsonify
from flask_login import current_user
from app import db
from app.auth_middleware import jwt_required
from app.models.incident import (
    Incident,
    IncidentType,
    HazardousMaterial,
    ActionPlan,
    IncidentTeam,
    IncidentPhoto,
    IncidentLog,
)
from app.models.team import Team, TeamMember
from app.models.chat import ChatChannel
from app.models.emergency import EmergencySignal
from app.services.notification_service import NotificationService
from datetime import datetime, timedelta
from sqlalchemy import func
import os
import uuid
from config import Config

incidents_bp = Blueprint("incidents", __name__)


def generate_incident_number():
    last = Incident.query.order_by(Incident.id.desc()).first()
    year = datetime.utcnow().year
    seq = (last.id + 1) if last else 1
    return f"BG-{year}-{seq:06d}"


@incidents_bp.route("", methods=["POST"])
@jwt_required
def create_incident():
    data = request.get_json()
    required = ("incident_type_id",)
    if not data or not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    incident_type = IncidentType.query.get(data["incident_type_id"])
    if not incident_type:
        return jsonify({"error": "Invalid incident type"}), 400

    incident = Incident(
        incident_number=generate_incident_number(),
        incident_type_id=data["incident_type_id"],
        channel=data.get("channel", "112"),
        status="registered",
        priority=data.get("priority", 3),
        address=data.get("address"),
        city=data.get("city"),
        region=data.get("region"),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        description=data.get("description"),
        reported_by=data.get("reported_by"),
        reporter_phone=data.get("reporter_phone"),
        casualties=data.get("casualties", 0),
        injured=data.get("injured", 0),
        created_by=current_user.id,
        assigned_dispatcher=current_user.id if current_user.role in ("dispatcher", "commander", "admin") else None,
    )
    db.session.add(incident)
    db.session.flush()

    channel = ChatChannel(
        incident_id=incident.id,
        name=f"Incident #{incident.incident_number}",
    )
    db.session.add(channel)

    log = IncidentLog(
        incident_id=incident.id,
        user_id=current_user.id,
        action="incident_created",
        details={"channel": incident.channel, "type": incident_type.name},
    )
    db.session.add(log)

    if data.get("team_ids"):
        for team_id in data["team_ids"]:
            team = Team.query.get(team_id)
            if team and team.is_active:
                it = IncidentTeam(incident_id=incident.id, team_id=team_id)
                db.session.add(it)
                incident.status = "dispatched"

    db.session.commit()

    if incident.status == "dispatched":
        NotificationService.notify_incident_teams(incident)

    return jsonify({"incident": incident.to_dict(include_relations=True)}), 201


@incidents_bp.route("", methods=["GET"])
@jwt_required
def list_incidents():
    status = request.args.get("status")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = Incident.query.order_by(Incident.created_at.desc())
    if status:
        query = query.filter_by(status=status)

    incidents = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "incidents": [i.to_dict() for i in incidents.items],
        "total": incidents.total,
        "pages": incidents.pages,
        "current_page": page,
    }), 200


@incidents_bp.route("/<int:incident_id>", methods=["GET"])
@jwt_required
def get_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    return jsonify({"incident": incident.to_dict(include_relations=True)}), 200


@incidents_bp.route("/<int:incident_id>", methods=["PUT"])
@jwt_required
def update_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    data = request.get_json()

    updatable = (
        "status", "priority", "address", "city", "region",
        "latitude", "longitude", "description", "casualties",
        "injured", "wind_direction", "wind_speed", "fire_front_coords",
    )
    for field in updatable:
        if field in data:
            setattr(incident, field, data[field])

    if data.get("status") == "closed":
        incident.closed_at = datetime.utcnow()

    log = IncidentLog(
        incident_id=incident.id,
        user_id=current_user.id,
        action="incident_updated",
        details=data,
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"incident": incident.to_dict(include_relations=True)}), 200


@incidents_bp.route("/<int:incident_id>/teams", methods=["POST"])
@jwt_required
def assign_team(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    data = request.get_json()
    team_id = data.get("team_id")
    if not team_id:
        return jsonify({"error": "team_id is required"}), 400

    team = Team.query.get(team_id)
    if not team or not team.is_active:
        return jsonify({"error": "Invalid or inactive team"}), 400

    existing = IncidentTeam.query.filter_by(
        incident_id=incident.id, team_id=team_id
    ).first()
    if existing:
        return jsonify({"error": "Team already assigned"}), 409

    it = IncidentTeam(incident_id=incident.id, team_id=team_id)
    db.session.add(it)
    if incident.status == "registered":
        incident.status = "dispatched"

    log = IncidentLog(
        incident_id=incident.id,
        user_id=current_user.id,
        action="team_assigned",
        details={"team_id": team_id, "team_name": team.name},
    )
    db.session.add(log)
    db.session.commit()

    NotificationService.notify_incident_teams(incident)

    return jsonify({"incident_team": it.to_dict()}), 201


@incidents_bp.route("/<int:incident_id>/teams/<int:team_id>", methods=["PUT"])
@jwt_required
def update_team_status(incident_id, team_id):
    incident_team = IncidentTeam.query.filter_by(
        incident_id=incident_id, team_id=team_id
    ).first_or_404()
    data = request.get_json()

    if "status" in data:
        incident_team.status = data["status"]
        if data["status"] == "on_scene" and not incident_team.arrived_at:
            incident_team.arrived_at = datetime.utcnow()
        elif data["status"] == "returning" and not incident_team.departed_at:
            incident_team.departed_at = datetime.utcnow()

    db.session.commit()
    return jsonify({"incident_team": incident_team.to_dict()}), 200


@incidents_bp.route("/<int:incident_id>/hazardous-materials", methods=["POST"])
@jwt_required
def add_hazardous_material(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    data = request.get_json()
    material_id = data.get("hazardous_material_id")
    if not material_id:
        return jsonify({"error": "hazardous_material_id is required"}), 400

    material = HazardousMaterial.query.get(material_id)
    if not material:
        return jsonify({"error": "Material not found"}), 404

    if material in incident.hazardous_materials:
        return jsonify({"error": "Material already added"}), 409

    incident.hazardous_materials.append(material)
    log = IncidentLog(
        incident_id=incident.id,
        user_id=current_user.id,
        action="hazardous_material_added",
        details={"material_id": material_id, "name": material.name},
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"hazardous_materials": [m.to_dict() for m in incident.hazardous_materials]}), 200


@incidents_bp.route("/<int:incident_id>/action-plans", methods=["POST"])
@jwt_required
def create_action_plan(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "Title is required"}), 400

    plan = ActionPlan(
        incident_id=incident.id,
        title=data["title"],
        description=data.get("description"),
        steps=data.get("steps"),
        priority=data.get("priority", 0),
        created_by=current_user.id,
    )
    db.session.add(plan)
    log = IncidentLog(
        incident_id=incident.id,
        user_id=current_user.id,
        action="action_plan_created",
        details={"plan_title": data["title"]},
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"action_plan": plan.to_dict()}), 201


@incidents_bp.route("/<int:incident_id>/photos", methods=["POST"])
@jwt_required
def upload_photo(incident_id):
    incident = Incident.query.get_or_404(incident_id)

    if "file" not in request.files:
        return jsonify({"error": "No photo file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else ""
    filename = f"{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(Config.UPLOAD_FOLDER, filename))

    photo = IncidentPhoto(
        incident_id=incident.id,
        user_id=current_user.id,
        filename=filename,
        caption=request.form.get("caption"),
    )
    db.session.add(photo)
    db.session.commit()

    return jsonify({"photo": photo.to_dict()}), 201


@incidents_bp.route("/photos/<int:photo_id>", methods=["DELETE"])
@jwt_required
def delete_photo(photo_id):
    photo = IncidentPhoto.query.get_or_404(photo_id)
    filepath = os.path.join(Config.UPLOAD_FOLDER, photo.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    db.session.delete(photo)
    db.session.commit()
    return jsonify({"message": "Photo deleted"}), 200


@incidents_bp.route("/types", methods=["GET"])
@jwt_required
def list_incident_types():
    types = IncidentType.query.all()
    return jsonify({"incident_types": [t.to_dict() for t in types]}), 200


@incidents_bp.route("/<int:incident_id>/log", methods=["GET"])
@jwt_required
def get_incident_log(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    logs = incident.logs.order_by(IncidentLog.created_at.desc()).all()
    return jsonify({"logs": [l.to_dict() for l in logs]}), 200


@incidents_bp.route("/sos", methods=["POST"])
@jwt_required
def create_sos():
    data = request.get_json()
    if not data or not data.get("incident_id"):
        return jsonify({"error": "incident_id is required"}), 400

    signal = EmergencySignal(
        incident_id=data["incident_id"],
        user_id=current_user.id,
        message=data.get("message"),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        signal_type=data.get("signal_type", "mayday"),
    )
    db.session.add(signal)
    db.session.commit()

    return jsonify({"signal": signal.to_dict()}), 201


@incidents_bp.route("/sos", methods=["GET"])
@jwt_required
def list_sos():
    signals = EmergencySignal.query.filter_by(resolved_at=None).order_by(
        EmergencySignal.created_at.desc()
    ).all()
    return jsonify({"signals": [s.to_dict() for s in signals]}), 200


@incidents_bp.route("/stats", methods=["GET"])
@jwt_required
def get_incident_stats():
    total = Incident.query.count()
    active = Incident.query.filter(Incident.status != "closed").count()
    closed = Incident.query.filter_by(status="closed").count()

    type_rows = db.session.query(
        IncidentType.name, func.count(Incident.id)
    ).join(Incident, Incident.incident_type_id == IncidentType.id
    ).group_by(IncidentType.id).all()
    by_type = [{"name": name, "count": count} for name, count in type_rows]

    status_rows = db.session.query(
        Incident.status, func.count(Incident.id)
    ).group_by(Incident.status).all()
    by_status = [{"status": status, "count": count} for status, count in status_rows]

    priority_rows = db.session.query(
        Incident.priority, func.count(Incident.id)
    ).group_by(Incident.priority).all()
    by_priority = [{"priority": priority, "count": count} for priority, count in priority_rows]

    on_scene_logs = IncidentLog.query.filter(
        IncidentLog.action == "status_change",
        IncidentLog.details.contains("on_scene"),
    ).all()
    hours = []
    for log in on_scene_logs:
        incident = Incident.query.get(log.incident_id)
        if incident and incident.created_at and log.created_at:
            diff = (log.created_at - incident.created_at).total_seconds() / 3600
            hours.append(diff)
    avg_response_time = round(sum(hours) / len(hours), 2) if hours else None

    today = datetime.utcnow().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    today_count = Incident.query.filter(
        func.date(Incident.created_at) == today
    ).count()
    this_week_count = Incident.query.filter(
        func.date(Incident.created_at) >= week_start
    ).count()
    this_month_count = Incident.query.filter(
        func.date(Incident.created_at) >= month_start
    ).count()
    teams_on_shift = TeamMember.query.filter_by(is_on_shift=True).count()

    return jsonify({
        "total": total,
        "active": active,
        "closed": closed,
        "by_type": by_type,
        "by_status": by_status,
        "by_priority": by_priority,
        "avg_response_time_hours": avg_response_time,
        "today_count": today_count,
        "this_week_count": this_week_count,
        "this_month_count": this_month_count,
        "teams_on_shift": teams_on_shift,
    }), 200
