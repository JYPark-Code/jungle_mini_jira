from flask import Blueprint, render_template, request, redirect, session, url_for, current_app
from app.services.auth_service import authenticate_user, register_user
from app.models.validators import validate_login_form, validate_signup_form

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # 1) 이미 로그인 상태면 바로 이동
    if "user_id" in session:
        return redirect(url_for("calendar.calendar_view"))

    # 2) GET: 로그인 화면
    if request.method == "GET":
        return render_template("login.html")

    # 3) POST: 폼 입력 읽기
    form = request.form  # ImmutableMultiDict
    email = form.get("email", "").strip()
    password = form.get("password", "")

    # 4) 입력 검증(빈 값/형식)
    error = validate_login_form(email=email, password=password)
    if error:
        return render_template("login.html", error=error)

    # 5) 인증 (DB 조회 + 비밀번호 해시 검증은 service에서)
    db = current_app.mongo  # create_app에서 app.mongo 세팅했다고 가정
    user = authenticate_user(db=db, email=email, password=password)

    if not user:
        return render_template("login.html", error="이메일 또는 비밀번호가 틀립니다")

    # 6) 세션 저장 (최소 정보만)
    session["user_id"] = str(user["_id"])
    # session["email"] = user.get("email")  #  디버깅용

    return redirect(url_for("calendar.calendar_view"))

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if "user_id" in session:
        return redirect(url_for("calendar.calendar_view"))

    if request.method == "GET":
        return render_template("signup.html")

    form = request.form
    email = form.get("email", "").strip()
    username = form.get("username", "").strip()
    password = form.get("password", "")
    password2 = form.get("password2", "")

    error = validate_signup_form(email=email, username=username, password=password, password2=password2)
    if error:
        return render_template("signup.html", error=error)

    db = current_app.mongo
    try:
        user = register_user(db=db, email=email, username=username, password=password)
    except ValueError as e:
        return render_template("signup.html", error=str(e))

    session["user_id"] = str(user["_id"])
    return redirect(url_for("calendar.calendar_view"))

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))