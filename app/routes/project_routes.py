# app/routes/project_routes.py
from flask import Blueprint, current_app, session, redirect, url_for, request, flash

from app.services.project_service import (
    create_project_service,
    invite_member_service,
    leave_project_service,
    remove_member_service,
    delete_project_service,
)

project_bp = Blueprint("project", __name__)

@project_bp.route("/projects", methods=["POST"])
def create_project():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = current_app.mongo
    user_id = session["user_id"]
    name = request.form.get("name", "")

    try:
        create_project_service(db=db, name=name, owner_id=user_id)
        flash("프로젝트가 생성되었습니다.", "success")
    except ValueError as e:
        flash(str(e), "error")

    return redirect(url_for("calendar.calendar_view"))

@project_bp.route("/projects/<project_id>/invite", methods=["POST"])
def invite(project_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = current_app.mongo
    user_id = session["user_id"]
    email = request.form.get("email", "")

    try:
        invite_member_service(db=db, project_id=project_id, inviter_id=user_id, email=email)
        flash("멤버가 추가되었습니다.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except PermissionError:
        flash("초대 권한이 없습니다.", "error")

    return redirect(url_for("calendar.calendar_view"))

@project_bp.route("/projects/<project_id>/leave", methods=["POST"])
def leave(project_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = current_app.mongo
    user_id = session["user_id"]
    try:
        leave_project_service(db=db, project_id=project_id, user_id=user_id)
        flash("프로젝트에서 나갔습니다.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("calendar.calendar_view"))

@project_bp.route("/projects/<project_id>/remove-member", methods=["POST"])
def remove_member(project_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = current_app.mongo
    owner_id = session["user_id"]
    target_user_id = request.form.get("user_id", "")

    try:
        remove_member_service(db=db, project_id=project_id, owner_id=owner_id, target_user_id=target_user_id)
        flash("멤버가 제거되었습니다.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except PermissionError:
        flash("멤버 제거 권한이 없습니다.", "error")

    return redirect(url_for("calendar.calendar_view"))


@project_bp.route("/projects/<project_id>/delete", methods=["POST"])
def delete_project(project_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = current_app.mongo
    user_id = session["user_id"]

    try:
        delete_project_service(db=db, project_id=project_id, user_id=user_id)
        flash("프로젝트가 삭제되었습니다.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except PermissionError:
        flash("삭제 권한이 없습니다.", "error")

    return redirect(url_for("calendar.calendar_view"))
