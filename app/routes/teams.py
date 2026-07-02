from flask import Blueprint, request, jsonify
from flask_login import current_user
from app import db
from app.auth_middleware import jwt_required
from app.models.team import Team, TeamMember, FireTruck, Shift
from app.models.user import User
from app.models.leave import Leave
from datetime import datetime, date, time

teams_bp = Blueprint("teams", __name__)


@teams_bp.route("", methods=["GET"])
@jwt_required
def list_teams():
    teams = Team.query.filter_by(is_active=True).all()
    return jsonify({"teams": [t.to_dict(include_members=True) for t in teams]}), 200


@teams_bp.route("", methods=["POST"])
@jwt_required
def create_team():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Team name is required"}), 400

    team = Team(
        name=data["name"],
        fire_truck_id=data.get("fire_truck_id"),
        station=data.get("station"),
    )
    db.session.add(team)
    db.session.commit()
    return jsonify({"team": team.to_dict()}), 201


@teams_bp.route("/<int:team_id>", methods=["GET"])
@jwt_required
def get_team(team_id):
    team = Team.query.get_or_404(team_id)
    return jsonify({"team": team.to_dict(include_members=True)}), 200


@teams_bp.route("/<int:team_id>/members", methods=["POST"])
@jwt_required
def add_member(team_id):
    team = Team.query.get_or_404(team_id)
    data = request.get_json()
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    existing = TeamMember.query.filter_by(user_id=user_id, team_id=team_id).first()
    if existing:
        return jsonify({"error": "User is already a member of this team"}), 409

    member = TeamMember(
        user_id=user_id,
        team_id=team_id,
        is_team_leader=data.get("is_team_leader", False),
    )
    db.session.add(member)
    db.session.commit()
    return jsonify({"member": member.to_dict()}), 201


@teams_bp.route("/members/<int:member_id>", methods=["PUT"])
@jwt_required
def update_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    data = request.get_json()
    if "is_team_leader" in data:
        member.is_team_leader = data["is_team_leader"]
    if "is_on_shift" in data:
        member.is_on_shift = data["is_on_shift"]
        if data["is_on_shift"]:
            member.shift_start = datetime.utcnow()
        else:
            member.shift_end = datetime.utcnow()
    db.session.commit()
    return jsonify({"member": member.to_dict()}), 200


@teams_bp.route("/members/<int:member_id>", methods=["DELETE"])
@jwt_required
def remove_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member removed"}), 200


@teams_bp.route("/available-members", methods=["GET"])
@jwt_required
def get_available_members():
    today = date.today()
    all_members = TeamMember.query.filter_by(is_on_shift=True).all()
    available = []
    for tm in all_members:
        is_on_leave = Leave.query.filter(
            Leave.user_id == tm.user_id,
            Leave.status == "approved",
            Leave.start_date <= today,
            Leave.end_date >= today,
        ).first()
        if not is_on_leave:
            available.append(tm.to_dict())
    return jsonify({"available_members": available}), 200


@teams_bp.route("/fire-trucks", methods=["GET"])
@jwt_required
def list_fire_trucks():
    trucks = FireTruck.query.all()
    return jsonify({"fire_trucks": [t.to_dict() for t in trucks]}), 200


@teams_bp.route("/fire-trucks", methods=["POST"])
@jwt_required
def create_fire_truck():
    data = request.get_json()
    if not data or not data.get("registration_number"):
        return jsonify({"error": "registration_number is required"}), 400

    truck = FireTruck(
        registration_number=data["registration_number"],
        model=data.get("model"),
        type=data.get("type", "fire_engine"),
        capacity=data.get("capacity"),
        gps_device_id=data.get("gps_device_id"),
    )
    db.session.add(truck)
    db.session.commit()
    return jsonify({"fire_truck": truck.to_dict()}), 201


@teams_bp.route("/shifts", methods=["GET"])
@jwt_required
def list_shifts():
    shifts = Shift.query.all()
    return jsonify({"shifts": [s.to_dict() for s in shifts]}), 200


@teams_bp.route("/shifts", methods=["POST"])
@jwt_required
def create_shift():
    data = request.get_json()
    required = ("name", "start_time", "end_time")
    if not data or not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    shift = Shift(
        name=data["name"],
        start_time=time.fromisoformat(data["start_time"]),
        end_time=time.fromisoformat(data["end_time"]),
    )
    db.session.add(shift)
    db.session.commit()
    return jsonify({"shift": shift.to_dict()}), 201


@teams_bp.route("/fleet", methods=["GET"])
@jwt_required
def list_fleet():
    trucks = FireTruck.query.order_by(FireTruck.type).all()
    return jsonify({"trucks": [t.to_dict() for t in trucks]}), 200


@teams_bp.route("/fleet/<int:truck_id>", methods=["PUT"])
@jwt_required
def update_truck(truck_id):
    truck = FireTruck.query.get_or_404(truck_id)
    data = request.get_json() or {}
    for field in ("registration_number", "model", "type", "capacity", "is_available",
                  "gps_device_id", "photo_url", "year_manufactured", "mileage_km",
                  "water_tank_l", "foam_tank_l", "equipment_notes"):
        if field in data:
            setattr(truck, field, data[field])
    if "last_service_date" in data and data["last_service_date"]:
        truck.last_service_date = datetime.fromisoformat(data["last_service_date"])
    db.session.commit()
    return jsonify({"truck": truck.to_dict()}), 200


@teams_bp.route("/fleet/<int:truck_id>/photo", methods=["POST"])
@jwt_required
def upload_truck_photo(truck_id):
    from config import Config
    import uuid as uuid_lib
    import os as os_lib

    truck = FireTruck.query.get_or_404(truck_id)

    if "file" not in request.files:
        return jsonify({"error": "No photo file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else ""
    filename = f"truck_{truck_id}_{uuid_lib.uuid4().hex}.{ext}"
    file.save(os_lib.path.join(Config.UPLOAD_FOLDER, filename))

    truck.photo_url = f"/static/uploads/{filename}"
    db.session.commit()

    return jsonify({"truck": truck.to_dict()}), 200
