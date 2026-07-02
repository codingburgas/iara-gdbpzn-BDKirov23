from app import db
from app.models.video import VideoSession
from datetime import datetime
import uuid


class VideoService:
    @staticmethod
    def create_session(incident_id, initiator_id):
        session_id = str(uuid.uuid4())
        session = VideoSession(
            incident_id=incident_id,
            initiator_id=initiator_id,
            session_id=session_id,
        )
        db.session.add(session)
        db.session.flush()
        return session

    @staticmethod
    def end_session(session_id):
        session = VideoSession.query.filter_by(session_id=session_id).first()
        if session:
            session.status = "ended"
            session.ended_at = datetime.utcnow()
            db.session.flush()
        return session
