from functools import wraps

from flask import redirect, session, url_for


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "name" in session.keys():
            return f(*args, **kwargs)
        return redirect(url_for("login"))

    return wrap


def logoff_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "name" not in session.keys():
            return f(*args, **kwargs)
        return redirect(url_for("index"))

    return wrap
