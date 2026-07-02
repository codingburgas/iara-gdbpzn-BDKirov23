import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "gdpbzn-secret-key-change-in-production"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "gdpbzn.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "jwt-secret-key-change"
    JWT_EXPIRATION_HOURS = 24
    UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    REDIS_URL = os.environ.get("REDIS_URL") or "redis://localhost:6379/0"
    SOCKETIO_MESSAGE_QUEUE = os.environ.get("SOCKETIO_MESSAGE_QUEUE") or None
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or "your-gemini-api-key-here"

    @staticmethod
    def init_app(app):
        os.makedirs(os.path.join(basedir, "app", "static", "uploads"), exist_ok=True)
        app.config["GEMINI_API_KEY"] = Config.GEMINI_API_KEY
