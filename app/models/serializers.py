# models/serializer.py
# models/serializers.py
from bson import ObjectId
from datetime import datetime


def _convert_value(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _serialize_comment(comment):
    return {
        "id": comment.get("id"),
        "author_id": _convert_value(comment.get("author_id")),
        "content": comment.get("content"),
        "created_at": _convert_value(comment.get("created_at")),
        "deleted": comment.get("deleted", False),
        "deleted_at": _convert_value(comment.get("deleted_at")),
        "deleted_by": _convert_value(comment.get("deleted_by")),
    }


def serialize_issue(issue):
    issue["_id"] = _convert_value(issue["_id"])
    issue["project_id"] = _convert_value(issue["project_id"])
    issue["created_by"] = _convert_value(issue.get("created_by"))
    issue["created_at"] = _convert_value(issue.get("created_at"))
    issue["due_date"] = _convert_value(issue.get("due_date"))

    if "comments" in issue:
        issue["comments"] = [_serialize_comment(c) for c in issue["comments"]]

    return issue