from flask import Blueprint, request, jsonify
from app.services.user_service import UserService
from app.schemas import UserSchema
from app.auth.auth_middleware import token_required
from sqlalchemy.exc import IntegrityError

user_bp = Blueprint('user', __name__)

@user_bp.route('/', methods=['GET'])
@token_required
def get_users(current_user):
    users = UserService.get_all_users()
    user_schema = UserSchema(many=True)
    return jsonify(user_schema.dump(users))

@user_bp.route('/', methods=['POST'])
def create_user():
    input_username = request.json.get('username')
    input_password = request.json.get('password')
    if not input_username or not input_password:
        return jsonify({'code': 400, 'message': 'Username and password are required'}), 400

    try:
        user = UserService.create_user(input_username, input_password)
        user_schema = UserSchema()
        return jsonify({'code': 200, 'message': 'user registered', 'user': user_schema.dump(user)}), 201
    except IntegrityError:
        UserService.user_rollback()
        return jsonify({'code': 409, 'message': 'Username already exists'}), 409
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500