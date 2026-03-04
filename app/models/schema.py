# models/schema.py
from datetime import datetime

def build_issue(data):
    return {
        "project_id": data["project_id"],
        "title": data["title"],
        "description": data.get("description", ""),
        "status": "TODO",
        "created_at": datetime.now(),
        "due_date": data.get("due_date"),
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
