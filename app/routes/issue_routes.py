# routes/issue_routes.py
from flask import (
    Blueprint,
    request,
    jsonify,
    current_app,
    session,
    redirect,
    url_for,
    flash,
)
from app.services.issue_service import (
    create_issue_service,
    list_issues_by_project_service,
    list_issues_by_range_service,
    update_issue_fields_service,
    get_issue_service,
    delete_issue_service,
    add_comment_service,
    delete_comment_service,
)

issue_bp = Blueprint("issue", __name__)


@issue_bp.route("/api/projects/<project_id>/issues", methods=["POST"])
def create_issue(project_id):
    if "user_id" not in session:
        return jsonify({"message": "login required"}), 401

    payload = request.get_json(silent=True) or {}
    db = current_app.mongo
    user_id = session["user_id"]

    try:
        created = create_issue_service(db=db, project_id=project_id, payload=payload, actor_id=user_id)
        return jsonify({"message": "이슈 생성 성공", "issue": created}), 201
    except PermissionError as e:
        return jsonify({"message": str(e)}), 403
    except ValueError as e:
        return jsonify({"message": str(e)}), 400


@issue_bp.route("/api/projects/<project_id>/issues", methods=["GET"])
def list_issues_by_project(project_id):
    if "user_id" not in session:
        return jsonify({"message": "login required"}), 401

    db = current_app.mongo
    user_id = session["user_id"]
    sort_order = int(request.args.get("sort_order", "1"))
    if sort_order not in (1, -1):
        sort_order = 1

    try:
        issues = list_issues_by_project_service(db=db, project_id=project_id, actor_id=user_id, sort_order=sort_order)
    except PermissionError as e:
        return jsonify({"message": str(e)}), 403
    except ValueError as e:
        return jsonify({"message": str(e)}), 400

    return jsonify(issues), 200


@issue_bp.route("/api/projects/<project_id>/issues/range", methods=["GET"])
def list_issues_by_range(project_id):
    if "user_id" not in session:
        return jsonify({"message": "login required"}), 401

    start = request.args.get("start")
    end = request.args.get("end")
    if not start or not end:
        return jsonify({"message": "start and end query params are required"}), 400

    db = current_app.mongo
    user_id = session["user_id"]
    sort_order = int(request.args.get("sort_order", "1"))
    if sort_order not in (1, -1):
        sort_order = 1

    try:
        issues = list_issues_by_range_service(db=db, project_id=project_id, start_date=start, end_date=end, actor_id=user_id, sort_order=sort_order)
    except PermissionError as e:
        return jsonify({"message": str(e)}), 403
    except ValueError as e:
        return jsonify({"message": str(e)}), 400

    return jsonify(issues), 200


@issue_bp.route("/api/issues/<issue_id>/fields", methods=["PATCH"])
def update_issue_fields(issue_id):
    if "user_id" not in session:
        return jsonify({"message": "login required"}), 401

    payload = request.get_json(silent=True) or {}
    if "expected_version" not in payload:
        return jsonify({"message": "expected_version is required"}), 400

    db = current_app.mongo
    user_id = session["user_id"]

    try:
        ok = update_issue_fields_service(
            db=db,
            issue_id=issue_id,
            expected_version=int(payload["expected_version"]),
            payload=payload,
            actor_id=user_id,
        )
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except PermissionError as e:
        return jsonify({"message": str(e)}), 403

    if not ok:
        current = get_issue_service(db=db, issue_id=issue_id)
        return jsonify({"message": "version conflict", "current": current}), 409

    updated = get_issue_service(db=db, issue_id=issue_id)
    return jsonify(updated), 200


@issue_bp.route("/issues/<issue_id>/delete", methods=["POST"])
def delete_issue(issue_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = current_app.mongo
    user_id = session["user_id"]

    try:
        delete_issue_service(db, issue_id, user_id)
        flash("이슈가 삭제되었습니다.", "success")
    except PermissionError:
        flash("삭제 권한이 없습니다.", "error")

    return redirect(url_for("calendar.calendar_view"))


@issue_bp.route("/api/issues/<issue_id>/comments", methods=["POST"])
def add_comment(issue_id):
    if "user_id" not in session:
        return jsonify({"message": "login required"}), 401

    db = current_app.mongo
    user_id = session["user_id"]
    payload = request.get_json(silent=True) or {}
    content = payload.get("content", "")

    if not content.strip():
        return jsonify({"message": "empty comment"}), 400

    comment_id = add_comment_service(db=db, issue_id=issue_id, actor_id=user_id, content=content)
    return jsonify({"message": "댓글이 등록되었습니다.", "comment_id": comment_id}), 201


@issue_bp.route("/api/issues/<issue_id>/comments/<comment_id>", methods=["DELETE"])
def delete_comment(issue_id, comment_id):
    if "user_id" not in session:
        return jsonify({"message": "login required"}), 401

    db = current_app.mongo
    user_id = session["user_id"]

    try:
        delete_comment_service(db=db, issue_id=issue_id, comment_id=comment_id, actor_id=user_id)
    except PermissionError:
        return jsonify({"message": "not allowed"}), 403

    return jsonify({"message": "댓글이 삭제되었습니다."}), 200
