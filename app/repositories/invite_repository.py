# app/repositories/invite_repository.py
from bson import ObjectId
from datetime import datetime


def create_invite(db, *, project_id, email, invited_by):
    doc = {
        "project_id": project_id,
        "email": email.lower().strip(),
        "invited_by": invited_by,
        "status": "pending",
        "created_at": datetime.now(),
    }
    result = db.project_invites.insert_one(doc)
    return str(result.inserted_id)


def list_pending_by_email(db, email):
    return list(db.project_invites.find({
        "email": email.lower().strip(),
        "status": "pending",
    }))


def find_by_id(db, invite_id):
    return db.project_invites.find_one({"_id": ObjectId(invite_id)})


def mark_accepted(db, invite_id, user_id):
    result = db.project_invites.update_one(
        {"_id": ObjectId(invite_id), "status": "pending"},
        {"$set": {
            "status": "accepted",
            "accepted_by": user_id,
            "accepted_at": datetime.now(),
        }},
    )
    return result.modified_count == 1


def exists_pending(db, *, project_id, email):
    return db.project_invites.count_documents({
        "project_id": project_id,
        "email": email.lower().strip(),
        "status": "pending",
    }, limit=1) > 0
