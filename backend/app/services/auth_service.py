from werkzeug.security import check_password_hash
from app.db.models import User
import jwt
import datetime
from flask import current_app

class AuthService:
    @staticmethod
    def authenticate_user(username, password):
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            token = jwt.encode(
                {
                    'username': username,
                    # 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=120)
                },
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            return token
        return None
