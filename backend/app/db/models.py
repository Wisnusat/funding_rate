import uuid
import json
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, BigInteger, String, DateTime, func
from app.db.extensions import db
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# User model
class User(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __repr__(self):
        return f'<User {self.username}>'

# AevoDB model
class BaseModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    instrument_name = Column(String, nullable=False)
    timestamp = Column(BigInteger, nullable=False)
    funding_rate = Column(String, nullable=False)
    mark_price = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<{self.__class__.__name__}(instrument_name={self.instrument_name}, timestamp={self.timestamp}, funding_rate={self.funding_rate}, mark_price={self.mark_price})>"

    def to_dict(self):
        return {
            'instrument_name': self.instrument_name,
            'timestamp': self.timestamp,
            'funding_rate': self.funding_rate,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)


# AevoDB model
class AevoDB(BaseModel):
    __tablename__ = 'funding_data_aevo'


# BybitDB model
class BybitDB(BaseModel):
    __tablename__ = 'funding_data_bybit'


# GateioDB model
class GateioDB(BaseModel):
    __tablename__ = 'funding_data_gateio'


# HyperliquidDB model
class HyperliquidDB(BaseModel):
    __tablename__ = 'funding_data_hyperliquid'
