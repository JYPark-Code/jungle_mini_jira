# services/issue_service.py
from __future__ import annotations

from bson import ObjectId
from datetime import datetime

from app.models.schema import build_issue, parse_date
from app.models.serializers import serialize_issue
from app.models.validators import validate_issue

from app.repositories import issue_repository as repo
from app.repositories import project_repository as project_repo
from app.repositories import user_repository


def _check_membership(db, project_id, user_id):
    project = project_repo.find_by_id(db, project_id)
    if not project:
        raise ValueError("project not found")
    if user_id not in project.get("member_ids", []):
        raise PermissionError("not a member of this project")
    return project


def create_issue_service(db, project_id, payload, actor_id):
    _check_membership(db, project_id, actor_id)

    data = dict(payload)
    data["project_id"] = project_id
    validate_issue(data)

    data["project_id"] = ObjectId(project_id)
    data["created_by"] = actor_id

    doc = build_issue(data)
    issue_id = repo.create_issue(db, doc)
    created = repo.find_by_id(db, issue_id)
    _attach_creator_name(db, created)
    return serialize_issue(created)


def list_issues_by_project_service(db, project_id, actor_id, sort_order=1):
    _check_membership(db, project_id, actor_id)
    issues = repo.find_by_project(db, project_id, sort_order=sort_order)
    for i in issues:
        _attach_creator_name(db, i)
    return [serialize_issue(i) for i in issues]


def list_issues_by_range_service(db, project_id, start_date, end_date, actor_id, sort_order=1):
    _check_membership(db, project_id, actor_id)

    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date)

    issues = repo.find_by_range(db, project_id, start_dt, end_dt)

    # 기간이 긴 순서로 정렬 (start_date 빠른 순 → 같으면 due_date 늦은 순)
    def _sort_key(issue):
        s = issue.get("start_date") or issue.get("due_date") or datetime.min
        d = issue.get("due_date") or datetime.min
        return s, -d.timestamp()

    issues.sort(key=_sort_key)

    for i in issues:
        _attach_creator_name(db, i)
    return [serialize_issue(i) for i in issues]


def _attach_creator_name(db, issue):
    user = user_repository.find_by_id(db, issue.get("created_by"))
    issue["creator_name"] = user["username"] if user else "Unknown"


def _is_owner_or_creator(db, issue, actor_id):
    if issue.get("created_by") == actor_id:
        return True
    project = project_repo.find_by_id(db, issue["project_id"])
    return project and project.get("owner_id") == actor_id


def update_issue_fields_service(db, issue_id, expected_version, payload, actor_id):
    issue = repo.find_by_id(db, issue_id)
    if not issue:
        raise ValueError("issue not found")

    _check_membership(db, issue["project_id"], actor_id)

    if "status" in payload:
        if not _is_owner_or_creator(db, issue, actor_id):
            raise PermissionError("only creator or project owner can change status")
        allowed_statuses = {"TODO", "IN_PROGRESS", "DONE"}
        if payload["status"] not in allowed_statuses:
            raise ValueError("invalid status")

    allowed_fields = {"title", "description", "start_date", "due_date", "status"}
    date_fields = {"start_date", "due_date"}
    patch = {}
    for k, v in payload.items():
        if k in allowed_fields and v != "" and v is not None:
            patch[k] = parse_date(v) if k in date_fields else v

    if not patch:
        raise ValueError("no updatable fields")

    return repo.update_fields_if_version(
        db, issue_id, expected_version, patch, actor_id
    )


def get_issue_service(db, issue_id):
    doc = repo.find_by_id(db, issue_id)
    if doc:
        _attach_creator_name(db, doc)
        return serialize_issue(doc)
    return None


def delete_issue_service(db, issue_id, actor_id):
    issue = repo.find_by_id(db, issue_id)
    if not issue:
        raise ValueError("issue not found")

    if not _is_owner_or_creator(db, issue, actor_id):
        raise PermissionError("only creator or project owner can delete issue")

    repo.delete_issue(db, issue_id)
    return True


def add_comment_service(db, issue_id, actor_id, content):
    if not content.strip():
        raise ValueError("empty comment")

    user = user_repository.find_by_id(db, actor_id)
    author_name = user["username"] if user else "Unknown"

    return repo.add_comment(db, issue_id, actor_id, content, author_name)


def delete_comment_service(db, issue_id, comment_id, actor_id):
    ok = repo.soft_delete_comment_if_author(
        db, issue_id, comment_id, actor_id
    )

    if not ok:
        raise PermissionError("not allowed")
