# app/repositories/project_repository.py
from bson import ObjectId
from datetime import datetime


def create_project(db, *, name, owner_id):
    doc = {
        "name": name,
        "owner_id": owner_id,
        "member_ids": [owner_id],
        "created_at": datetime.now(),
    }
    result = db.projects.insert_one(doc)
    return str(result.inserted_id)


def find_by_id(db, project_id):
    return db.projects.find_one({"_id": ObjectId(project_id)})


def list_by_member(db, user_id):
    return list(db.projects.find({"member_ids": user_id}))


def add_member(db, project_id, user_id):
    result = db.projects.update_one(
        {"_id": ObjectId(project_id)},
        {"$addToSet": {"member_ids": user_id}},
    )
    return result.modified_count == 1


def remove_member(db, project_id, user_id):
    result = db.projects.update_one(
        {"_id": ObjectId(project_id)},
        {"$pull": {"member_ids": user_id}},
    )
    return result.modified_count == 1
