from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from flask_cors import CORS


db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app) 
    db.init_app(app)
    Migrate(app, db)
    jwt.init_app(app)

    from .routes import product_bp
    app.register_blueprint(product_bp)
    with app.app_context():
        db.create_all()
        
    return app