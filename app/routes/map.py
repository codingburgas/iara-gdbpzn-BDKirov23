from flask import Blueprint, request, jsonify
from flask_login import current_user
from app import db
from app.auth_middleware import jwt_required
from app.models.map_marker import MapMarker
from app.models.incident import Incident, IncidentLog
from app.models.incident import IncidentTeam
from app.models.team import TeamMember

map_bp = Blueprint("map", __name__)


@map_bp.route("/<int:incident_id>/markers", methods=["GET"])
@jwt_required
def get_markers(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    markers = incident.map_markers.all()
    return jsonify({"markers": [m.to_dict() for m in markers]}), 200


@map_bp.route("/<int:incident_id>/markers", methods=["POST"])
@jwt_required
def create_marker(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    data = request.get_json()

    required = ("marker_type", "latitude", "longitude")
    if not data or not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    if data["marker_type"] not in MapMarker.MARKER_TYPES:
        return jsonify({"error": f"Invalid marker type. Must be one of: {MapMarker.MARKER_TYPES}"}), 400

    marker = MapMarker(
        incident_id=incident.id,
        user_id=current_user.id,
        marker_type=data["marker_type"],
        label=data.get("label"),
        latitude=data["latitude"],
        longitude=data["longitude"],
        radius=data.get("radius"),
        color=data.get("color"),
        icon=data.get("icon"),
        is_visible_to_all=data.get("is_visible_to_all", True),
    )
    db.session.add(marker)
    db.session.commit()

    return jsonify({"marker": marker.to_dict()}), 201


@map_bp.route("/markers/<int:marker_id>", methods=["PUT"])
@jwt_required
def update_marker(marker_id):
    marker = MapMarker.query.get_or_404(marker_id)
    data = request.get_json()

    updatable = ("label", "latitude", "longitude", "radius", "color", "icon", "is_visible_to_all")
    for field in updatable:
        if field in data:
            setattr(marker, field, data[field])

    db.session.commit()
    return jsonify({"marker": marker.to_dict()}), 200


@map_bp.route("/markers/<int:marker_id>", methods=["DELETE"])
@jwt_required
def delete_marker(marker_id):
    marker = MapMarker.query.get_or_404(marker_id)
    db.session.delete(marker)
    db.session.commit()
    return jsonify({"message": "Marker deleted"}), 200


@map_bp.route("/<int:incident_id>/fire-front", methods=["PUT"])
@jwt_required
def update_fire_front(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    data = request.get_json()

    if "fire_front_coords" in data:
        incident.fire_front_coords = data["fire_front_coords"]
    if "wind_direction" in data:
        incident.wind_direction = data["wind_direction"]
    if "wind_speed" in data:
        incident.wind_speed = data["wind_speed"]

    log = IncidentLog(
        incident_id=incident.id,
        user_id=current_user.id,
        action="fire_front_updated",
        details={
            "fire_front_coords": data.get("fire_front_coords"),
            "wind_direction": data.get("wind_direction"),
            "wind_speed": data.get("wind_speed"),
        },
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        "fire_front_coords": incident.fire_front_coords,
        "wind_direction": incident.wind_direction,
        "wind_speed": incident.wind_speed,
    }), 200


@map_bp.route("/markers/all", methods=["GET"])
@jwt_required
def get_all_markers():
    markers = MapMarker.query.order_by(MapMarker.created_at.desc()).all()
    return jsonify({"markers": [m.to_dict() for m in markers]}), 200


@map_bp.route("/team-locations/<int:incident_id>", methods=["GET"])
@jwt_required
def get_team_locations(incident_id):
    incident_teams = IncidentTeam.query.filter_by(incident_id=incident_id).all()
    locations = []
    for it in incident_teams:
        if it.team:
            members = TeamMember.query.filter_by(
                team_id=it.team.id, is_on_shift=True
            ).all()
            for m in members:
                if m.user:
                    locations.append({
                        "team_id": it.team.id,
                        "team_name": it.team.name,
                        "user_id": m.user.id,
                        "user_name": m.user.full_name,
                        "latitude": None,
                        "longitude": None,
                        "status": it.status,
                    })
    return jsonify({"locations": locations}), 200
