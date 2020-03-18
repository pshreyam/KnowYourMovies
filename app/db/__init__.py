"""
Handles Connection And Interaction With Database!
"""

import os

import mysql.connector as db


def connect_to_db():
    config = {
        "host": os.environ.get("DB_HOST", ""),
        "user": os.environ.get("DB_USER", ""),
        "password": os.environ.get("DB_PASSWORD", ""),
        "database": os.environ.get("DB_NAME", ""),
    }
    connection = db.connect(**config)
    return connection
