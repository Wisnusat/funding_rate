from app.models import User
from app.extensions import db
from werkzeug.security import generate_password_hash

class UserService:
    @staticmethod
    def get_all_users():
        return User.query.all()

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
