# services/issue_service.py
from __future__ import annotations

from bson import ObjectId
from datetime import datetime

from app.models.schema import build_issue
from app.models.serializers import serialize_issue
from app.models.validators import validate_issue

from app.repositories import issue_repository as repo
from app.repositories import project_repository as project_repo


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
    return serialize_issue(created)


def list_issues_by_project_service(db, project_id, actor_id):
    _check_membership(db, project_id, actor_id)
    issues = repo.find_by_project(db, project_id)
    return [serialize_issue(i) for i in issues]


def list_issues_by_range_service(db, project_id, start_date, end_date, actor_id):
    _check_membership(db, project_id, actor_id)

    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date)

    issues = repo.find_by_range(db, project_id, start_dt, end_dt)
    return [serialize_issue(i) for i in issues]


def _is_owner_or_creator(db, issue, actor_id):
    if issue.get("created_by") == actor_id:
        return True
    project = project_repo.find_by_id(db, issue["project_id"])
    return project and project.get("owner_id") == actor_id


def update_issue_status_service(db, issue_id, expected_version, to_status, actor_id):
    issue = repo.find_by_id(db, issue_id)
    if not issue:
        raise ValueError("issue not found")

    if not _is_owner_or_creator(db, issue, actor_id):
        raise PermissionError("only creator or project owner can change status")

    allowed = {"TODO", "IN_PROGRESS", "DONE"}
    if to_status not in allowed:
        raise ValueError("invalid status")

    return repo.update_status_if_version(
        db, issue_id, expected_version, to_status, actor_id
    )


def update_issue_fields_service(db, issue_id, expected_version, payload, actor_id):
    issue = repo.find_by_id(db, issue_id)
    if not issue:
        raise ValueError("issue not found")

    _check_membership(db, issue["project_id"], actor_id)

    allowed_fields = {"title", "description", "start_date", "due_date"}
    patch = {}
    for k, v in payload.items():
        if k in allowed_fields:
            patch[k] = v

    if not patch:
        raise ValueError("no updatable fields")

    return repo.update_fields_if_version(
        db, issue_id, expected_version, patch, actor_id
    )


def get_issue_service(db, issue_id):
    doc = repo.find_by_id(db, issue_id)
    if doc:
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

    return repo.add_comment(db, issue_id, actor_id, content)


def delete_comment_service(db, issue_id, comment_id, actor_id):
    ok = repo.soft_delete_comment_if_author(
        db, issue_id, comment_id, actor_id
    )

    if not ok:
        raise PermissionError("not allowed")
