import os

from flask import Flask
from loguru import logger

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.config["PROFILE_PIC_FOLDER"] = os.path.join(app.root_path, "static/profile_pics")
logger.info(f"Creating folder {app.config['PROFILE_PIC_FOLDER']} if not exists ...")
os.makedirs(app.config["PROFILE_PIC_FOLDER"], exist_ok=True)

from app.routes import *

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
