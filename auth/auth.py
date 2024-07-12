from flask import Blueprint, request, jsonify, current_app
from dotenv import load_dotenv
import os
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import jwt

load_dotenv()

auth_bp = Blueprint('auth', __name__)

DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

@auth_bp.route('/register', methods=['POST'])
def register():
    input_username = request.form.get('username')
    input_password = request.form.get('password')
    if not input_username or not input_password:
        return jsonify({'code': 400, 'message': 'Username and password are required'}), 400

    hashed_password = generate_password_hash(input_password)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (input_username, hashed_password))
        conn.commit()
        return jsonify({'code': 201, 'message': 'User registered successfully'}), 201
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'code': 409, 'message': 'Username already exists'}), 409
    except Exception as e:
        return jsonify({'code': 500, 'message': f'An error occurred: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    input_username = request.form.get('username')
    input_password = request.form.get('password')
    if not input_username or not input_password:
        return jsonify({'code': 400, 'message': 'Username and password are required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT * FROM users WHERE username = %s', (input_username,))
        user = cur.fetchone()
        if user and check_password_hash(user['password'], input_password):
            token = jwt.encode(
                {
                    'username': input_username,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=120)
                },
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            return jsonify({'code': 200, 'token': token})
        else:
            return jsonify({'code': 401, 'message': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'code': 500, 'message': f'An error occurred: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({'code': 200, 'message': 'Successfully logged out'}), 200
