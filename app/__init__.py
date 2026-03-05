from flask import Flask, jsonify, request, render_template
import os
from pymongo import MongoClient


def _is_api_request():
    return request.path.startswith("/api/") or request.accept_mimetypes.best == "application/json"


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

    # 글로벌 에러 핸들러
    @app.errorhandler(404)
    def not_found(e):
        if _is_api_request():
            return jsonify({"message": "not found"}), 404
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        if _is_api_request():
            return jsonify({"message": "internal server error"}), 500
        return render_template("500.html"), 500

    return app
