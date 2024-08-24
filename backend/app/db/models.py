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
class AevoDB(Base):
    __tablename__ = 'funding_data_aevo'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    instrument_name = db.Column(String, nullable=False)
    timestamp = db.Column(BigInteger, nullable=False)
    funding_rate = db.Column(String, nullable=False)
    mark_price = db.Column(String)

    created_at = db.Column(DateTime, server_default=func.now())
    updated_at = db.Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<AevoDB(instrument_name={self.instrument_name}, timestamp={self.timestamp}, funding_rate={self.funding_rate}, mark_price={self.mark_price})>"

    def to_dict(self):
        return {
            'instrument_name': self.instrument_name,
            'timestamp': self.timestamp,
            'funding_rate': self.funding_rate,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

# BybitDB model
class BybitDB(Base):
    __tablename__ = 'funding_data_bybit'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    instrument_name = db.Column(String, nullable=False)
    timestamp = db.Column(BigInteger, nullable=False)
    funding_rate = db.Column(String, nullable=False)
    mark_price = db.Column(String)

    created_at = db.Column(DateTime, server_default=func.now())
    updated_at = db.Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<BybitDB(instrument_name={self.instrument_name}, timestamp={self.timestamp}, funding_rate={self.funding_rate}, mark_price={self.mark_price})>"

    def to_dict(self):
        return {
            'instrument_name': self.instrument_name,
            'timestamp': self.timestamp,
            'funding_rate': self.funding_rate,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

# GateioDB model
class GateioDB(Base):
    __tablename__ = 'funding_data_gateio'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    instrument_name = db.Column(String, nullable=False)
    timestamp = db.Column(BigInteger, nullable=False)
    funding_rate = db.Column(String, nullable=False)
    mark_price = db.Column(String)

    created_at = db.Column(DateTime, server_default=func.now())
    updated_at = db.Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<GateioDB(instrument_name={self.instrument_name}, timestamp={self.timestamp}, funding_rate={self.funding_rate}, mark_price={self.mark_price})>"

    def to_dict(self):
        return {
            'instrument_name': self.instrument_name,
            'timestamp': self.timestamp,
            'funding_rate': self.funding_rate,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

# HyperliquidDB model
class HyperliquidDB(Base):
    __tablename__ = 'funding_data_hyperliquid'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    instrument_name = db.Column(String, nullable=False)
    timestamp = db.Column(BigInteger, nullable=False)
    funding_rate = db.Column(String, nullable=False)
    mark_price = db.Column(String)

    created_at = db.Column(DateTime, server_default=func.now())
    updated_at = db.Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<HyperliquidDB(instrument_name={self.instrument_name}, timestamp={self.timestamp}, funding_rate={self.funding_rate}, mark_price={self.mark_price})>"

    def to_dict(self):
        return {
            'instrument_name': self.instrument_name,
            'timestamp': self.timestamp,
            'funding_rate': self.funding_rate,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)
