import os
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_cors import CORS
from config import Config

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
socketio = SocketIO()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    config_class.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    CORS(app)
    socketio.init_app(app, cors_allowed_origins="*", message_queue=app.config.get("SOCKETIO_MESSAGE_QUEUE"))

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.incidents import incidents_bp
    from app.routes.teams import teams_bp
    from app.routes.tasks import tasks_bp
    from app.routes.map import map_bp
    from app.routes.chat import chat_bp
    from app.routes.notifications import notifications_bp
    from app.routes.resources import resources_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(incidents_bp, url_prefix="/api/incidents")
    app.register_blueprint(teams_bp, url_prefix="/api/teams")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(map_bp, url_prefix="/api/map")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")
    app.register_blueprint(resources_bp, url_prefix="/api/resources")

    from app.websocket import handlers

    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/manifest.json")
    def manifest():
        return {
            "name": "ГДПБЗН - Пожарна безопасност",
            "short_name": "ГДПБЗН",
            "description": "Система за управление на произшествия",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#0d1117",
            "theme_color": "#dc3545",
            "orientation": "portrait",
            "icons": [
                {"src": "/static/icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"},
            ],
            "categories": ["business", "utilities"],
            "lang": "bg-BG",
            "scope": "/",
        }, 200, {"Content-Type": "application/json"}

    @app.route("/sw.js")
    def service_worker():
        js = '''const CACHE = "gdpbzn-v1";
const STATIC = ["/", "/static/icon.svg"];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(STATIC)));
  self.skipWaiting();
});
self.addEventListener("activate", e => e.waitUntil(clients.claim()));
self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (url.pathname.startsWith("/api/")) {
    e.respondWith(networkFirst(e.request));
  } else {
    e.respondWith(cacheFirst(e.request));
  }
});
async function networkFirst(req) {
  try {
    const res = await fetch(req);
    const cache = await caches.open(CACHE);
    cache.put(req, res.clone());
    return res;
  } catch { return caches.match(req); }
}
async function cacheFirst(req) {
  const cached = await caches.match(req);
  if (cached) return cached;
  try { const res = await fetch(req); return res; } catch { return Response.error(); }
}'''
        return js, 200, {"Content-Type": "application/javascript", "Service-Worker-Allowed": "/"}

    return app
