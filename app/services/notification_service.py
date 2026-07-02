from app import db
from app.models.notification import Notification
from app.models.incident import IncidentTeam
from app.models.team import TeamMember


class NotificationService:
    @staticmethod
    def notify_user(user_id, title, body, notification_type, incident_id=None, data=None):
        notification = Notification(
            user_id=user_id,
            title=title,
            body=body,
            notification_type=notification_type,
            incident_id=incident_id,
            data=data,
        )
        db.session.add(notification)
        db.session.flush()
        return notification

    @staticmethod
    def notify_incident_teams(incident):
        assigned_teams = IncidentTeam.query.filter_by(incident_id=incident.id).all()
        for it in assigned_teams:
            members = TeamMember.query.filter_by(
                team_id=it.team_id, is_on_shift=True
            ).all()
            for member in members:
                NotificationService.notify_user(
                    user_id=member.user_id,
                    title="New Incident Assigned",
                    body=f"Incident #{incident.incident_number}: {incident.description or 'No description'}",
                    notification_type="new_incident",
                    incident_id=incident.id,
                    data={"incident_id": incident.id, "incident_number": incident.incident_number},
                )
        db.session.flush()

    @staticmethod
    def notify_emergency(emergency_signal):
        assigned_teams = IncidentTeam.query.filter_by(
            incident_id=emergency_signal.incident_id
        ).all()
        for it in assigned_teams:
            members = TeamMember.query.filter_by(
                team_id=it.team_id, is_on_shift=True
            ).all()
            for member in members:
                if member.user_id != emergency_signal.user_id:
                    NotificationService.notify_user(
                        user_id=member.user_id,
                        title="EMERGENCY - Mayday",
                        body=f"Firefighter {emergency_signal.user.full_name} needs help!",
                        notification_type="emergency_alert",
                        incident_id=emergency_signal.incident_id,
                        data={
                            "signal_id": emergency_signal.id,
                            "type": emergency_signal.signal_type,
                            "latitude": emergency_signal.latitude,
                            "longitude": emergency_signal.longitude,
                        },
                    )
        db.session.flush()
