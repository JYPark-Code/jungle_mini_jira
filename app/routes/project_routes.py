# app/routes/project_routes.py
from flask import Blueprint, current_app, session, redirect, url_for, request, render_template, flash

from app.services.project_service import (
    create_project_service,
    invite_member_service,
    leave_project_service,
    list_my_invites_service,
    accept_invite_service,
)
from app.repositories.user_repository import find_by_id

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
        flash("초대가 완료되었습니다.", "success")
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

@project_bp.route("/invites", methods=["GET"])
def invites_inbox():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = current_app.mongo
    user = find_by_id(db, session["user_id"])
    if not user:
        return redirect(url_for("auth.logout"))

    pending = list_my_invites_service(db=db, email=user["email"])
    return render_template("invites.html", invites=pending)

@project_bp.route("/invites/<invite_id>/accept", methods=["POST"])
def accept_invite(invite_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = current_app.mongo
    user_id = session["user_id"]

    try:
        accept_invite_service(db=db, invite_id=invite_id, user_id=user_id)
        flash("초대를 수락했습니다.", "success")
    except ValueError as e:
        flash(str(e), "error")

    return redirect(url_for("calendar.calendar_view"))
