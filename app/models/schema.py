# models/schema.py
from datetime import datetime

def _parse_due_date(value):
    if value is None or isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


def build_issue(data):
    return {
        "project_id": data["project_id"],
        "title": data["title"],
        "description": data.get("description", ""),
        "status": "TODO",
        "created_at": datetime.now(),
        "start_date": _parse_due_date(data.get("start_date")),
        "due_date": _parse_due_date(data.get("due_date")),
        "version": 1,
        "created_by": data["created_by"],
        "comments": [],
    }

def build_user(*, email: str, username: str, password_hash: str):
    return {
        "email": email,
        "username": username.strip(),
        "password_hash": password_hash,
        "created_at": datetime.now(),
    }
