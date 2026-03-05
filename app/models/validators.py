# models/validators.py
import re

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def validate_login_form(*, email: str, password: str):
    if not email:
        return "이메일을 입력해주세요."
    if not _EMAIL_RE.match(email):
        return "이메일 형식이 올바르지 않습니다."
    if not password:
        return "비밀번호를 입력해주세요."
    return None

def validate_signup_form(*, email: str, username: str, password: str, password2: str):
    if not email:
        return "이메일을 입력해주세요."
    if not _EMAIL_RE.match(email):
        return "이메일 형식이 올바르지 않습니다."
    if not username or not username.strip():
        return "username을 입력해주세요."
    if len(username.strip()) < 2:
        return "username은 2자 이상이어야 합니다."
    if not password:
        return "비밀번호를 입력해주세요."
    if len(password) < 8:
        return "비밀 번호는 8자 이상이어야 합니다."
    if password != password2:
        return "비밀번호가 일치하지 않습니다."
    return None

def validate_issue(data):

    if "title" not in data:
        raise ValueError("title required")

    if "project_id" not in data:
        raise ValueError("project_id required")

    start = data.get("start_date")
    due = data.get("due_date")
    if start and due and start > due:
        raise ValueError("start_date must be before or equal to due_date")