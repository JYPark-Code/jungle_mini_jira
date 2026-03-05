# app/services/project_service.py
from app.repositories import project_repository as projects
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

    # 대상 유저 조회
    user = find_by_email(db, email)
    if not user:
        raise ValueError("가입되지 않은 사용자입니다")

    target_id = str(user["_id"])
    if target_id in project.get("member_ids", []):
        raise ValueError("이미 프로젝트 멤버입니다")

    # 즉시 멤버 추가
    return projects.add_member(db, project_id, target_id)


def list_my_projects_service(*, db, user_id):
    return projects.list_by_member(db, user_id)


def leave_project_service(*, db, project_id, user_id):
    project = projects.find_by_id(db, project_id)
    if project and project.get("owner_id") == user_id:
        raise ValueError("owner cannot leave the project")
    return projects.remove_member(db, project_id, user_id)


def remove_member_service(*, db, project_id, owner_id, target_user_id):
    project = projects.find_by_id(db, project_id)
    if not project:
        raise ValueError("project not found")
    if project.get("owner_id") != owner_id:
        raise PermissionError("only owner can remove members")
    if target_user_id == owner_id:
        raise ValueError("자기 자신은 제거할 수 없습니다")
    if target_user_id not in project.get("member_ids", []):
        raise ValueError("해당 유저는 멤버가 아닙니다")

    return projects.remove_member(db, project_id, target_user_id)


def delete_project_service(*, db, project_id, user_id):
    project = projects.find_by_id(db, project_id)
    if not project:
        raise ValueError("project not found")
    if (project.get("name") or "").strip().lower() == "personal":
        raise ValueError("기본 프로젝트는 삭제할 수 없습니다")
    if project.get("owner_id") != user_id:
        raise PermissionError("only owner can delete project")
    return projects.delete_project(db, project_id)
