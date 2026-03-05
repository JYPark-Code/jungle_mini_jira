from flask import Blueprint, render_template, session, redirect, url_for, current_app, request
from app.repositories import project_repository as project_repo
from app.repositories import issue_repository as issue_repo
from app.repositories import invite_repository as invite_repo
from app.repositories.user_repository import find_by_id
from datetime import datetime

calendar_bp = Blueprint("calendar", __name__)

@calendar_bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("calendar.calendar_view"))
    return redirect(url_for("auth.login"))

@calendar_bp.route("/calendar")
def calendar_view():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = current_app.mongo
    user_id = session["user_id"]

    # 1) 내 프로젝트 목록
    projects = project_repo.list_by_member(db, user_id)

    # (옵션) 프로젝트가 없으면 기본 프로젝트 1개 만들어주기
    if not projects:
        default_id = project_repo.create_project(db, name="Personal", owner_id=user_id)
        projects = project_repo.list_by_member(db, user_id)

    # 2) 현재 선택된 프로젝트
    selected_project_id = request.args.get("project_id")
    if not selected_project_id:
        selected_project_id = str(projects[0]["_id"])  # 첫 프로젝트 기본 선택

    # 3) 이슈 로드 (프로젝트 기준)
    issues = issue_repo.find_by_project(db, selected_project_id)

    # 4) 내 초대함 (메일 발송 없이 in-app)
    me = find_by_id(db, user_id)
    username = me.get("username", "User") if me else "User"
    invites = []
    if me and me.get("email"):
        invites = invite_repo.list_pending_by_email(db, me["email"])

    # 5) Calendar week
    weeks = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    return render_template(
        "calendar.html",
        projects=projects,
        selected_project_id=selected_project_id,
        issues=issues,
        pending_invites_count=len(invites),
        invites=invites,  # 필요하면 템플릿에서 목록도 출력 가능
        username=username,
        weeks=weeks,
    )


def _remaining_text(due_value):
    if not due_value:
        return "마감일 없음"

    if isinstance(due_value, datetime):
        due = due_value
    else:
        due = datetime.fromisoformat(str(due_value))

    now = datetime.now()
    delta = due - now
    seconds = int(delta.total_seconds())

    if seconds < 0:
        return "마감 지남"

    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    mins, _ = divmod(rem, 60)

    if days > 0:
        return f"{days}일 {hours}시간 남음"
    elif hours > 0:
        return f"{hours}시간 {mins}분 남음"
    return f"{mins}분 남음"


@calendar_bp.route("/status")
def status_view():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = current_app.mongo
    user_id = session["user_id"]

    # 1) 내 프로젝트 목록
    projects = project_repo.list_by_member(db, user_id)
    project_name_map = {str(p["_id"]): p["name"] for p in projects}

    # 2) 전체 이슈 로드
    all_issues = []
    for p_id in project_name_map:
        all_issues.extend(issue_repo.find_by_project(db, p_id))

    # 3) 생성자 이름 매핑
    creator_ids = list(
        set(str(i.get("created_by")) for i in all_issues if i.get("created_by"))
    )
    user_name_map = {}
    for c_id in creator_ids:
        u = find_by_id(db, c_id)
        user_name_map[c_id] = u.get("username", "Unknown") if u else "Unknown"

    # 4) 이슈별 표시용 필드 추가
    for issue in all_issues:
        issue["project_name"] = project_name_map.get(
            str(issue.get("project_id")), "Unknown Project"
        )
        issue["creator_name"] = user_name_map.get(
            str(issue.get("created_by")), "Unknown User"
        )
        issue["remaining_text"] = _remaining_text(issue.get("due_date"))

    # 5) 공통 템플릿 변수
    me = find_by_id(db, user_id)
    username = me.get("username", "User") if me else "User"
    invites = []
    if me and me.get("email"):
        invites = invite_repo.list_pending_by_email(db, me["email"])

    return render_template(
        "status.html",
        projects=projects,
        issues=all_issues,
        username=username,
        pending_invites_count=len(invites),
        invites=invites,
    )
