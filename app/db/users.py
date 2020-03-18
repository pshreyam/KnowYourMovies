import json

from loguru import logger
from werkzeug.security import check_password_hash, generate_password_hash

from app.utils.string import is_any_empty

from . import connect_to_db


def register_user(user):
    conn = connect_to_db()
    cursor = conn.cursor()
    user = json.loads(user)

    username = user.get("username", "").strip().lower()
    fullname = user.get("fullname", "").strip()
    gender = user.get("gender", "").strip()
    email = user.get("email", "").strip()
    password = user.get("password", "").strip()
    repassword = user.get("re_password", "").strip()

    if is_any_empty(
        username,
        fullname,
        gender,
        email,
        password,
        repassword,
    ):
        return False, "One or more fields are empty!"

    if not password == repassword:
        return False, "Passwords do not match!"

    hashed_password = generate_password_hash(password)

    sql = f"SELECT * FROM user WHERE username='{username}'"

    cursor.execute(sql)
    existing_user = cursor.fetchone()
    if existing_user:
        logger.info(existing_user)
        return False, "Username already exists!"
    sql = (
        "INSERT INTO user (id, username, fullname,"
        "email, gender, password) VALUES"
        f"(NULL, '{username}', '{fullname}',"
        f" '{email}', '{gender}', '{hashed_password}');"
    )

    cursor.execute(sql)
    conn.commit()
    conn.close()

    return True, None


def update_user_profile(user, username):
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)

    fullname = user.get("fullname", "").strip()
    gender = user.get("gender", "").strip()
    email = user.get("email", "").strip()
    profile_pic = user.get("profile_pic", "").strip()

    if is_any_empty(fullname, gender, email):
        return False, "One or more fields are empty!"

    sql = f"SELECT * FROM user WHERE username='{username}'"

    cursor.execute(sql)
    existing_user = cursor.fetchone()
    if not existing_user:
        return False, "No such user!"

    sql = f"""UPDATE user
        SET fullname='{fullname}',
        email='{email}',
        gender='{gender}'
        WHERE username='{username}'; """

    cursor.execute(sql)

    if profile_pic:
        cursor.execute(f"UPDATE user SET profile_pic='{profile_pic}' WHERE username='{username}';")

    conn.commit()
    conn.close()

    return True, None


def login(username, password):
    username = username.lower()

    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)
    sql = f"SELECT * FROM user WHERE username = '{username}'"
    cursor.execute(sql)
    user_details = cursor.fetchone()

    if not user_details:
        return False, "The user with that username does not exist!"

    db_password = user_details["password"]
    if not check_password_hash(db_password, password):
        return False, "The credentials you have supplied is invalid!"

    conn.close()

    return True, None


def fetch_login_details(username):
    username = username.lower()

    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)
    sql = f"SELECT * FROM user WHERE username = '{username}'"
    cursor.execute(sql)
    user_details = cursor.fetchone()
    conn.close()

    return user_details
