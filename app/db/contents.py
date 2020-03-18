from base64 import b64encode

from . import connect_to_db


def load_movies(table_name):
    """
    Loads Movies From Different Tables.
    """
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)
    sql = f"SELECT * FROM {table_name}"
    cursor.execute(sql)
    movies = cursor.fetchall()
    conn.close()
    for movie in movies:
        movie["image"] = b64encode(movie.get("image", "")).decode("utf-8")
    return movies


def get_user_selected_movies(user_id):
    """
    Gets Movies Liked By Users.
    """
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)
    sql = f"""SELECT * FROM user_selected_movies, imdb WHERE `imdb`.`id` = `user_selected_movies`.`movie_id` AND `user_selected_movies`.`user_id` = {user_id}"""
    cursor.execute(sql)
    movies = cursor.fetchall()
    conn.close()
    for movie in movies:
        movie["image"] = b64encode(movie.get("image", "")).decode("utf-8")
    return movies


def get_user_content(user):
    """
    Get content for user dashboard using rule-based algo.
    """
    # TODO: This logic has to be updated with better algo for recommending the movies.
    content = {}

    content["user_selected"] = get_user_selected_movies(user.get("id"))
    content["user_selected_title"] = "Movies liked"
    content["user_selected_category"] = "imdb"

    content["primary"] = load_movies("nepali")[:5]
    content["primary_category"] = "Nepali"

    content["secondary"] = load_movies("action")[:5]
    content["secondary_category"] = "Action"

    return content


def select_movies(user_id, movie_id):
    """
    Like Movie For Users From Imdb.
    """
    if not user_id:
        return "There was some problem adding the movie!", "error"
    conn = connect_to_db()
    cursor = conn.cursor()
    sql = f"""SELECT * FROM user_selected_movies
            WHERE movie_id = {movie_id} AND user_id = {user_id}"""
    cursor.execute(sql)
    existing = cursor.fetchone()
    if existing:
        conn.commit()
        conn.close()
        return "Movie already added to dashboard!", "info"
    sql = f"INSERT INTO user_selected_movies(movie_id,user_id) VALUES({movie_id},{user_id})"
    cursor.execute(sql)
    conn.commit()
    conn.close()
    return "Successfully added to dashboard!", "success"


def search_movie(category, title):
    if not title:
        return None
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)
    sql = f"SELECT * FROM {category} WHERE title LIKE '%{title}%'"
    cursor.execute(sql)
    movies = cursor.fetchall()
    conn.close()
    for movie in movies:
        movie["image"] = b64encode(movie.get("image", "")).decode("utf-8")
    return movies
