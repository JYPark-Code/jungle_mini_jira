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
        "author_name": comment.get("author_name", "Unknown"),
        "content": comment.get("content"),
        "created_at": _convert_value(comment.get("created_at")),
        "deleted": comment.get("deleted", False),
        "deleted_at": _convert_value(comment.get("deleted_at")),
        "deleted_by": _convert_value(comment.get("deleted_by")),
    }


def serialize_issue(issue):
    result = dict(issue)
    result["_id"] = _convert_value(result["_id"])
    result["project_id"] = _convert_value(result["project_id"])
    result["created_by"] = _convert_value(result.get("created_by"))
    result["created_at"] = _convert_value(result.get("created_at"))
    result["start_date"] = _convert_value(result.get("start_date"))
    result["due_date"] = _convert_value(result.get("due_date"))
    result["updated_by"] = _convert_value(result.get("updated_by"))
    result["updated_at"] = _convert_value(result.get("updated_at"))

    if "comments" in result:
        sorted_comments = sorted(
            result["comments"],
            key=lambda c: c.get("created_at") or datetime.min,
            reverse=True,
        )
        result["comments"] = [_serialize_comment(c) for c in sorted_comments]

    return result
