from flask import Blueprint, render_template, session, redirect, url_for, current_app, request
from app.repositories import project_repository as project_repo
from app.repositories import issue_repository as issue_repo
from app.repositories import invite_repository as invite_repo
from app.repositories.user_repository import find_by_id

calendar_bp = Blueprint("calendar", __name__)

# @calendar_bp.route("/")
# def index():
#     if "user_id" in session:
#         return redirect(url_for("calendar.calendar_view"))
#     return redirect(url_for("auth.login"))

@calendar_bp.route("/calendar")
def calendar_view():
    # if "user_id" not in session:
    #     return redirect(url_for("auth.login"))

    # db = current_app.mongo
    # user_id = session["user_id"]

    # # 1) 내 프로젝트 목록
    # projects = project_repo.list_by_member(db, user_id)

    # # (옵션) 프로젝트가 없으면 기본 프로젝트 1개 만들어주기
    # if not projects:
    #     default_id = project_repo.create_project(db, name="Personal", owner_id=user_id)
    #     projects = project_repo.list_by_member(db, user_id)

    # # 2) 현재 선택된 프로젝트
    # selected_project_id = request.args.get("project_id")
    # if not selected_project_id:
    #     selected_project_id = str(projects[0]["_id"])  # 첫 프로젝트 기본 선택

    # # 3) 이슈 로드 (프로젝트 기준)
    # issues = issue_repo.find_by_project(db, selected_project_id)

    # # 4) 내 초대함 (메일 발송 없이 in-app)
    # me = find_by_id(db, user_id)
    # invites = []
    # if me and me.get("email"):
    #     invites = invite_repo.list_pending_by_email(db, me["email"])

    weeks = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    return render_template(
        "calendar.html",
        # projects=projects,
        # selected_project_id=selected_project_id,
        # issues=issues,
        # pending_invites_count=len(invites),
        # invites=invites,  # 필요하면 템플릿에서 목록도 출력 가능
        weeks=weeks
    )