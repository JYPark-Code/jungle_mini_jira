from bson import ObjectId
from datetime import datetime
import uuid


def find_by_id(db, issue_id):
    return db.issues.find_one({"_id": ObjectId(issue_id)})


def create_issue(db, doc):
    result = db.issues.insert_one(doc)
    return str(result.inserted_id)

# 내림차순 필요할 경우 파라미터 -1 쓰기.
def find_by_project(db, project_id, sort_order=1):
    return list(
        db.issues.find({"project_id": ObjectId(project_id)}).sort("due_date", sort_order)
    )


def find_by_range(db, project_id, start_date, end_date, sort_order=1):
    query = {
        "project_id": ObjectId(project_id),
        "due_date": {"$gte": start_date},
        "$or": [
            {"start_date": {"$lte": end_date}},
            {
                "start_date": None,
                "due_date": {"$lte": end_date},
            },
            {
                "start_date": {"$exists": False},
                "due_date": {"$lte": end_date},
            },
        ],
    }
    return list(
        db.issues.find(query).sort("due_date", sort_order)
    )


def update_status_if_version(db, issue_id, expected_version, to_status, actor_id):
    result = db.issues.update_one(
        {
            "_id": ObjectId(issue_id),
            "version": expected_version,
        },
        {
            "$set": {
                "status": to_status,
                "updated_by": actor_id,
                "updated_at": datetime.now(),
            },
            "$inc": {
                "version": 1,
            },
        },
    )
    return result.modified_count == 1


def update_fields_if_version(db, issue_id, expected_version, patch, actor_id):
    update = {
        "$set": {
            **patch,
            "updated_by": actor_id,
            "updated_at": datetime.now(),
        },
        "$inc": {"version": 1},
    }
    result = db.issues.update_one(
        {"_id": ObjectId(issue_id), "version": expected_version}, update
    )
    return result.modified_count == 1


def delete_issue(db, issue_id):
    result = db.issues.delete_one({"_id": ObjectId(issue_id)})
    return result.deleted_count == 1


def add_comment(db, issue_id, author_id, content, author_name):
    comment_id = str(uuid.uuid4())
    comment = {
        "id": comment_id,
        "author_id": author_id,
        "author_name": author_name,
        "content": content,
        "created_at": datetime.now(),
        "deleted": False,
        "deleted_at": None,
        "deleted_by": None,
    }

    db.issues.update_one(
        {"_id": ObjectId(issue_id)},
        {"$push": {"comments": comment}},
    )
    return comment_id


def soft_delete_comment_if_author(db, issue_id, comment_id, actor_id):
    result = db.issues.update_one(
        {"_id": ObjectId(issue_id)},
        {
            "$set": {
                "comments.$[c].deleted": True,
                "comments.$[c].deleted_at": datetime.now(),
                "comments.$[c].deleted_by": actor_id,
                "comments.$[c].content": "[deleted]",
            }
        },
        array_filters=[
            {"c.id": comment_id, "c.author_id": actor_id, "c.deleted": False}
        ],
    )
    return result.modified_count == 1
