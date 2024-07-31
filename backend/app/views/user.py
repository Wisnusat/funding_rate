from flask import Blueprint, request, jsonify
from app.services.user_service import UserService
from app.schemas import UserSchema
from app.middleware.auth_middleware import token_required
from sqlalchemy.exc import IntegrityError

user_bp = Blueprint('user', __name__)

@user_bp.route('/me', methods=['GET'])
@token_required
def get_user_info(current_user):
    user = UserService.get_user_info(current_user)
    user_schema = UserSchema()
    return jsonify(user_schema.dump(user))


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