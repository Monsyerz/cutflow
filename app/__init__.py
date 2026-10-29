from flask import Flask
import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL
from app.extensions import db,migrate


load_dotenv()

def create_app(test_config=None):
    app = Flask(__name__)

  
    if test_config is None:
        app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

        app.config["SQLALCHEMY_DATABASE_URI"] = URL.create(
            drivername="postgresql+psycopg",
            username=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            database=os.environ["DB_NAME"]
    )
    else:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import db_models

    from app.routes import main
    app.register_blueprint(main)

    return app