import secrets

from db import InMemoryDB
from core import DoziFlask
from api import api_bp
from frontend import frontend_bp

def create_app():
    app = DoziFlask(__name__)

    app.db = InMemoryDB()
    app.secret_key = secrets.token_bytes()
    app.register_blueprint(api_bp)
    app.register_blueprint(frontend_bp)

    return app

app = create_app()
