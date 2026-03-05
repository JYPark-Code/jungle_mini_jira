# repositories/user_repository.py

from bson import ObjectId


def find_by_email(db, email):
    return db.users.find_one({"email": email.strip().lower()})


def find_by_username(db, username):
    return db.users.find_one({"username": username})


def find_by_id(db, user_id):
    return db.users.find_one({"_id": ObjectId(user_id)})


def find_by_ids(db, user_ids):
    object_ids = [ObjectId(uid) for uid in user_ids]
    return list(db.users.find({"_id": {"$in": object_ids}}))


def create_user(db, doc):
    result = db.users.insert_one(doc)
    return str(result.inserted_id)
