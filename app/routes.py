import json
import os
from datetime import datetime

from flask import abort, flash, redirect, render_template, request, session, url_for
from loguru import logger
from werkzeug.utils import secure_filename

from app.app import app
from app.db import connections, contents, users
from app.decorators import login_required, logoff_required
from app.services.cloudinary import upload_image_to_cloudinary


@app.route("/")
@login_required
def index():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@login_required
def dashboard():
    user_details = users.fetch_login_details(session.get("name"))

    if not user_details:
        abort(404)

    dashboard_content = contents.get_user_content(user_details)

    return render_template(
        "dashboard.html",
        user_object=user_details,
        dashboard_content=dashboard_content,
        current_date=datetime.today().strftime("%A, %d %B %Y"),
    )


@app.route("/register", methods=["GET", "POST"])
@logoff_required
def register():
    if request.method == "POST":
        new_user = json.dumps(request.form)
        registered, error = users.register_user(new_user)

        if error:
            flash(error, "error")

        if registered:
            flash(
                "Your account has been created. Now you are able to log in!",
                "success",
            )
            return redirect(url_for("login"))

        return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
@logoff_required
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        logged_in, error = users.login(username, password)

        if error:
            flash(error, "error")

        if logged_in:
            session["name"] = username
            return redirect(url_for("dashboard"))

        return render_template("login.html")

    return render_template("login.html")


@app.route("/movies/<int:movie_id>/like")
@login_required
def select_movies(movie_id):
    user_id = users.fetch_login_details(session.get("name")).get("id", "")

    msg, category = contents.select_movies(user_id, movie_id)

    flash(msg, category)

    return redirect(url_for("dashboard"))


@app.route("/user/profile")
@login_required
def user():
    user_details = users.fetch_login_details(session.get("name"))
    followers = len(connections.get_followers(user_details.get("id")))
    following = len(connections.get_following(user_details.get("id")))
    return render_template(
        "user-profile.html",
        user_details=user_details,
        followers=followers,
        following=following,
    )


@app.route("/user/following")
@login_required
def user_following():
    user_details = users.fetch_login_details(session.get("name"))
    following = connections.get_following(user_details.get("id"))
    return render_template("following.html", following=following)


@app.route("/user/followers")
@login_required
def user_followers():
    user_details = users.fetch_login_details(session.get("name"))
    followers = connections.get_followers(user_details.get("id"))
    following = connections.get_following(user_details.get("id"))
    following_id_list = list(map(lambda x: x.get("id"), following))
    return render_template(
        "followers.html",
        followers=followers,
        following_id_list=following_id_list,
    )


@app.route("/user/follow/<username>")
@login_required
def follow_user(username):
    if username == session.get("name"):
        flash("You cannot perform this action!", "error")
        return redirect(url_for("user_following"))
    user_id = users.fetch_login_details(session.get("name")).get("id")
    following_id = users.fetch_login_details(username).get("id")
    msg, error = connections.follow(user_id, following_id)
    flash(msg, error)
    return redirect(url_for("user_following"))


@app.route("/user/unfollow/<username>")
@login_required
def unfollow_user(username):
    user_id = users.fetch_login_details(session.get("name")).get("id")
    following_id = users.fetch_login_details(username).get("id")
    msg, error = connections.unfollow(user_id, following_id)
    flash(msg, error)
    return redirect(url_for("user_following"))


@app.route("/user/edit", methods=["GET", "POST"])
@login_required
def edit_user():
    username = session.get("name", "")

    if request.method == "POST":
        data = dict(request.form)
        if "profile_pic" in request.files and request.files.get("profile_pic"):
            profile_pic = request.files.get("profile_pic")
            filename = secure_filename(profile_pic.filename)
            local_profile_pic_path = os.path.join(app.config["PROFILE_PIC_FOLDER"], filename)
            profile_pic.save(local_profile_pic_path)
            try:
                profile_pic_path = upload_image_to_cloudinary(file_url=local_profile_pic_path, username=username)
            except Exception as exc:
                logger.warning(f"Failed uploading image to cloudinary for username `{username}`. | {str(exc)}")
                data["profile_pic"] = ""
            else:
                # Once the profile_pic is uploaded to cloudinary, remove the file locally
                if profile_pic_path:
                    try:
                        os.remove(local_profile_pic_path)
                    except Exception as exc:
                        logger.warning(f"Error deleting file: {local_profile_pic_path} | {str(exc)}")
                data["profile_pic"] = profile_pic_path
        is_updated, error = users.update_user_profile(user=data, username=username)
        if error:
            flash(error, "error")
        if is_updated:
            flash("Successfully updated profile!", "success")
            return redirect(url_for("user"))
        return redirect(url_for("edit_user"))
    user_details = users.fetch_login_details(username=username)
    return render_template("edit-user-profile.html", user_details=user_details)


@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))


@app.route("/movies/")
@app.route("/movies/<string:category>")
@login_required
def get_movies(category="imdb"):
    user_details = users.fetch_login_details(session.get("name"))
    movies = contents.load_movies(category)
    return render_template(
        "movies.html",
        movies=movies,
        category=category,
        user_object=user_details,
    )


@app.route("/movie/<string:category>/<int:movie_id>")
@login_required
def movie_details(category, movie_id):
    user_details = users.fetch_login_details(session.get("name"))
    if movie_id <= 0:
        abort(404)
    movie = contents.load_movies(category)[movie_id - 1]
    return render_template(
        "movie-details.html",
        movie=movie,
        category=category,
        user_object=user_details,
    )


@app.route("/search/movies")
@login_required
def search_movies():
    title = request.args.get("title", "").strip()
    category = request.args.get("category", "imdb")
    movies = contents.search_movie(category, title)
    return render_template("search.html", movies=movies, category=category)


@app.route("/@<string:username>")
def public_user_profile(username):
    user_details = users.fetch_login_details(username)
    current_user = users.fetch_login_details(session.get("name", ""))
    if not user_details:
        abort(404)
    user_id = user_details.get("id")
    followers = len(connections.get_followers(user_id))
    following = len(connections.get_following(user_id))
    movies_liked = contents.get_user_selected_movies(user_id)

    is_current_user = False
    following_id_list = []

    if current_user:
        following_list = connections.get_following(current_user.get("id"))
        following_id_list = list(map(lambda x: x.get("id"), following_list))
        is_current_user = current_user.get("username", "") == username

    return render_template(
        "public-user-profile.html",
        user_details=user_details,
        followers=followers,
        following=following,
        following_id_list=following_id_list,
        movies_liked=movies_liked,
        is_current_user=is_current_user,
    )


@app.errorhandler(404)
def handle_errors(_):
    return render_template("404.html"), 404
