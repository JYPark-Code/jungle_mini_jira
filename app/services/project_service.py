# app/services/project_service.py
from app.repositories import project_repository as projects
from app.repositories import invite_repository as invites
from app.repositories.user_repository import find_by_email


def create_project_service(*, db, name, owner_id):
    name = (name or "").strip()
    if not name:
        raise ValueError("project name required")
    return projects.create_project(db, name=name, owner_id=owner_id)


def invite_member_service(*, db, project_id, inviter_id, email):
    email = (email or "").strip().lower()
    if not email:
        raise ValueError("email required")

    # 프로젝트 오너만 초대 가능 (RBAC)
    project = projects.find_by_id(db, project_id)
    if not project:
        raise ValueError("project not found")
    if project.get("owner_id") != inviter_id:
        raise PermissionError("only owner can invite members")

    # 초대 중복 방지
    if invites.exists_pending(db, project_id=project_id, email=email):
        raise ValueError("already invited")

    return invites.create_invite(db, project_id=project_id, email=email, invited_by=inviter_id)


def list_my_projects_service(*, db, user_id):
    return projects.list_by_member(db, user_id)


def leave_project_service(*, db, project_id, user_id):
    project = projects.find_by_id(db, project_id)
    if project and project.get("owner_id") == user_id:
        raise ValueError("owner cannot leave the project")
    return projects.remove_member(db, project_id, user_id)


def list_my_invites_service(*, db, email):
    return invites.list_pending_by_email(db, email)


def accept_invite_service(*, db, invite_id, user_id):
    inv = invites.find_by_id(db, invite_id)
    if not inv:
        raise ValueError("invite not found")
    if inv.get("status") != "pending":
        raise ValueError("invite not found")

    # 1) invite accepted 처리
    ok = invites.mark_accepted(db, invite_id, user_id)
    if not ok:
        return False

    # 2) project 멤버로 추가
    return projects.add_member(db, inv["project_id"], user_id)
