# services/auth_service.py
from werkzeug.security import check_password_hash, generate_password_hash
from app.repositories.user_repository import find_by_email, create_user
from app.models.schema import build_user

def authenticate_user(*, db, email: str, password: str):
    user = find_by_email(db=db, email=email)
    if not user:
        return None
    if not check_password_hash(user.get("password_hash", ""), password):
        return None
    return user

def register_user(*, db, email: str, username: str, password: str):
    exists = find_by_email(db=db, email=email)
    if exists:
        raise ValueError("이미 가입된 이메일입니다.")

    password_hash = generate_password_hash(password)
    doc = build_user(email=email, username=username, password_hash=password_hash)
    user_id = create_user(db=db, doc=doc)

    # 생성된 유저 반환(세션 저장용)
    return {"_id": user_id, "email": email}