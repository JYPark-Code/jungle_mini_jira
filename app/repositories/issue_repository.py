from bson import ObjectId
from datetime import datetime
import uuid


def find_by_id(db, issue_id):
    return db.issues.find_one({"_id": ObjectId(issue_id)})


def create_issue(db, doc):
    result = db.issues.insert_one(doc)
    return str(result.inserted_id)


def find_by_project(db, project_id):
    return list(
        db.issues.find({"project_id": ObjectId(project_id)})
    )


def find_by_range(db, project_id, start_date, end_date):
    return list(
        db.issues.find({
            "project_id": ObjectId(project_id),
            "due_date": {
                "$gte": start_date,
                "$lte": end_date,
            },
        })
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
        },
        "$inc": {"version": 1},
    }
    result = db.issues.update_one(
        {"_id": ObjectId(issue_id), "version": expected_version}, update
    )
    return result.modified_count == 1


def delete_if_creator(db, issue_id, actor_id):
    result = db.issues.delete_one({
        "_id": ObjectId(issue_id),
        "created_by": actor_id,
    })
    return result.deleted_count == 1


def add_comment(db, issue_id, author_id, content):
    comment_id = str(uuid.uuid4())
    comment = {
        "id": comment_id,
        "author_id": author_id,
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
