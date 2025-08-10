from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from flask_cors import CORS

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    jwt.init_app(app)
    CORS(app)
    from .routes import cart_bp
    app.register_blueprint(cart_bp)

    return app