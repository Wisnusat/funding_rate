from flask import Blueprint, request, jsonify, current_app
from dotenv import load_dotenv
import os
from app.services.auth_service import AuthService
from app.services.user_service import UserService
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
import jwt
import datetime

load_dotenv()

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['POST'])
def login():
    input_username = request.form.get('username')
    input_password = request.form.get('password')
    if not input_username or not input_password:
        return jsonify({'code': 400, 'message': 'Username and password are required'}), 400

    token = AuthService.authenticate_user(input_username, input_password)
    if token:
        return jsonify({'code': 200, 'token': token})
    else:
        return jsonify({'code': 401, 'message': 'Invalid credentials'}), 401