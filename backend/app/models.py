import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db

class User(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
