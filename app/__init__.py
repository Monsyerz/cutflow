from flask import Flask
import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL
from app.extensions import db

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "your_secret_key_here"

    app.config["SQLALCHEMY_DATABASE_URI"] = URL.create(
        drivername="postgresql+psycopg",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"]
    )

    db.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    return app