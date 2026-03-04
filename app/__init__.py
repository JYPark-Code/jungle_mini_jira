from flask import Flask
import os
from pymongo import MongoClient

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = os.environ.get("SECRET_KEY", "dev")

    # DB 연결 (예시)
    client = MongoClient(
        os.environ.get("MONGO_HOST", "localhost"),
        int(os.environ.get("MONGO_PORT", "27017")),
    )
    app.mongo = client.mini_jira

    # Blueprint import & register
    from app.routes.auth_routes import auth_bp
    from app.routes.calendar_routes import calendar_bp
    from app.routes.issue_routes import issue_bp
    from app.routes.project_routes import project_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(issue_bp)
    app.register_blueprint(project_bp)

    return app
