from flask import Blueprint, request, jsonify
from flask_login import current_user
from app import db
from app.auth_middleware import jwt_required
from app.models.resource import Resource, ResourceRequest
from app.models.incident import IncidentLog
from datetime import datetime

resources_bp = Blueprint("resources", __name__)


@resources_bp.route("", methods=["GET"])
@jwt_required
def list_resources():
    resource_type = request.args.get("resource_type")
    query = Resource.query
    if resource_type:
        query = query.filter_by(resource_type=resource_type)
    resources = query.all()
    return jsonify({"resources": [r.to_dict() for r in resources]}), 200


@resources_bp.route("", methods=["POST"])
@jwt_required
def create_resource():
    data = request.get_json()
    required = ("name", "resource_type")
    if not data or not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    resource = Resource(
        name=data["name"],
        resource_type=data["resource_type"],
        quantity_available=data.get("quantity_available", 0),
        unit=data.get("unit"),
        storage_location=data.get("storage_location"),
        is_consumable=data.get("is_consumable", True),
    )
    db.session.add(resource)
    db.session.commit()
    return jsonify({"resource": resource.to_dict()}), 201


@resources_bp.route("/requests", methods=["POST"])
@jwt_required
def create_request():
    data = request.get_json()
    required = ("incident_id", "resource_id", "quantity")
    if not data or not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    resource = Resource.query.get(data["resource_id"])
    if not resource:
        return jsonify({"error": "Resource not found"}), 404

    req = ResourceRequest(
        incident_id=data["incident_id"],
        resource_id=data["resource_id"],
        quantity=data["quantity"],
        requested_by=current_user.id,
        notes=data.get("notes"),
    )
    db.session.add(req)

    log = IncidentLog(
        incident_id=data["incident_id"],
        user_id=current_user.id,
        action="resource_requested",
        details={
            "resource_name": resource.name,
            "quantity": data["quantity"],
            "unit": resource.unit,
        },
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"request": req.to_dict()}), 201


@resources_bp.route("/requests/<int:incident_id>", methods=["GET"])
@jwt_required
def list_requests(incident_id):
    requests = ResourceRequest.query.filter_by(incident_id=incident_id)\
        .order_by(ResourceRequest.created_at.desc()).all()
    return jsonify({"requests": [r.to_dict() for r in requests]}), 200


@resources_bp.route("/requests/<int:request_id>/status", methods=["PUT"])
@jwt_required
def update_request_status(request_id):
    req = ResourceRequest.query.get_or_404(request_id)
    data = request.get_json()
    if "status" in data:
        req.status = data["status"]
        if data["status"] == "delivered":
            req.fulfilled_at = datetime.utcnow()
        req.approved_by = current_user.id
    db.session.commit()
    return jsonify({"request": req.to_dict()}), 200
