import os
from flask import Blueprint, request, jsonify
from utils import require_api_key
from .models import User
from . import db
from flask_jwt_extended import create_access_token, get_jwt
from flask_jwt_extended import jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
@require_api_key
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"message": "Username and password are required"}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "User already exists"}), 400
    
    user = User(username=data['username'])
    user.set_password(data['password'])
    user.is_admin = data.get('is_admin', False)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"message": "Username and password are required"}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        additional_claims = {"is_admin": user.is_admin}
        access_token = create_access_token(identity=user.username, additional_claims=additional_claims)
        return jsonify(access_token=access_token), 200

    return jsonify({"message": "Invalid credentials"}), 401


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    username = get_jwt_identity()
    claims = get_jwt()
    is_admin = claims.get('is_admin', False)

    return {
        "message": f"Welcome {username}",
        "is_admin": is_admin
    }, 200