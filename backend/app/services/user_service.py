from app.db.models import User
from app.db.extensions import db
from werkzeug.security import generate_password_hash

class UserService:
    @staticmethod
    def get_user_info(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def create_user(username, password):
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def user_rollback():
        db.session.rollback()
        db.session.close()
